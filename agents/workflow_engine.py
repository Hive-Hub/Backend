import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.utils import timezone
from .models import AgentWorkflow, WorkflowStep, AgentTask, TaskResult, AgentExecution, AgentExecutionLog
from .executors.llm_executor import LLMExecutor

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """
    Enterprise-grade engine for orchestrating and executing multi-agent workflows.
    Supports:
    - Sequential & Parallel step execution (via ThreadPoolExecutor)
    - Conditional step execution (dynamic skip conditions)
    - Retry Logic & Timeouts
    - Manual Approval pause states
    """
    
    def __init__(self, workflow_id, request_context=None):
        self.workflow = AgentWorkflow.objects.get(id=workflow_id)
        self.request_context = request_context or {}
        self.step_results = {}  # Maps step_number -> output_text

    def execute(self, initial_input):
        logger.info(f"Starting execution of workflow: {self.workflow.name}")
        steps = list(self.workflow.steps_list.all().order_by('step_number'))
        
        # Reset step statuses
        for step in steps:
            step.status = WorkflowStep.StepStatus.PENDING
            step.retry_count = 0
            step.save()

        completed_steps = set()
        failed_steps = set()

        while len(completed_steps) + len(failed_steps) < len(steps):
            # Find steps that are ready (all dependencies satisfied)
            ready_steps = []
            for step in steps:
                if step.step_number in completed_steps or step.step_number in failed_steps:
                    continue
                
                # Check dependencies
                dependencies = step.depends_on_steps or []
                if all(dep in completed_steps for dep in dependencies):
                    ready_steps.append(step)

            if not ready_steps:
                # Deadlock or no steps ready
                break

            # If there are multiple ready steps, we can run them in PARALLEL!
            if len(ready_steps) > 1:
                logger.info(f"Running steps in parallel: {[s.step_number for s in ready_steps]}")
                self._run_steps_parallel(ready_steps, initial_input, completed_steps, failed_steps)
            else:
                logger.info(f"Running step sequentially: {ready_steps[0].step_number}")
                self._run_step(ready_steps[0], initial_input, completed_steps, failed_steps)

            # If a critical step failed, we abort the entire workflow
            for step in ready_steps:
                if step.status == WorkflowStep.StepStatus.FAILED and step.is_critical:
                    logger.error(f"Critical step {step.step_number} failed. Aborting workflow.")
                    return "FAILED"
                
                # If a step is awaiting manual approval, we pause execution
                if step.status == WorkflowStep.StepStatus.AWAITING_APPROVAL:
                    logger.info(f"Workflow paused. Step {step.step_number} is awaiting approval.")
                    return "AWAITING_APPROVAL"

        return "COMPLETED" if not failed_steps else "FAILED"

    def _run_step(self, step, initial_input, completed_steps, failed_steps):
        step.status = WorkflowStep.StepStatus.IN_PROGRESS
        step.save()

        # 1. Evaluate Conditional execution
        if not self._should_execute_step(step):
            logger.info(f"Step {step.step_number} ({step.name}) skipped due to condition check.")
            step.status = WorkflowStep.StepStatus.SKIPPED
            step.save()
            completed_steps.add(step.step_number)
            return

        # 2. Build input from mapping or initial input
        input_data = self._resolve_input_data(step, initial_input)

        # 3. Create or get AgentTask
        task = AgentTask.objects.create(
            title=f"Workflow {self.workflow.name} - Step {step.step_number}",
            description=step.name,
            status=AgentTask.Status.IN_PROGRESS,
            assigned_agent=step.agent
        )

        # 4. Check if Manual Approval is required
        if step.status == WorkflowStep.StepStatus.AWAITING_APPROVAL or task.approval_required:
            step.status = WorkflowStep.StepStatus.AWAITING_APPROVAL
            step.save()
            task.status = AgentTask.Status.AWAITING_APPROVAL
            task.save()
            return

        # 5. Run execution with Retry Logic & Timeout wrapper
        success = False
        output_text = ""
        tokens_used = 0
        execution_time = 0.0
        error_msg = ""

        executor = LLMExecutor(agent=step.agent)

        for attempt in range(1, step.max_retries + 1):
            step.retry_count = attempt - 1
            step.save()

            try:
                # Run the executor
                res = executor.execute(task, input_data)
                
                execution_time = res.get("execution_time", 0.0)
                tokens_used = res.get("tokens_used", 0)
                
                if res.get("status") == "SUCCESS":
                    success = True
                    output_text = res.get("output", "")
                    break
                else:
                    error_msg = res.get("error_message", "Execution failed")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error running step {step.step_number} attempt {attempt}: {error_msg}")
            
            # Wait brief delay before retry
            if attempt < step.max_retries:
                time.sleep(1)

        # 6. Record Results
        task.completed_at = timezone.now()
        if success:
            task.status = AgentTask.Status.COMPLETED
            task.save()
            
            # Create TaskResult
            TaskResult.objects.create(
                task=task,
                output_data=output_text,
                execution_time=execution_time,
                tokens_used=tokens_used,
                status="SUCCESS"
            )
            
            step.status = WorkflowStep.StepStatus.COMPLETED
            step.save()
            
            self.step_results[step.step_number] = output_text
            completed_steps.add(step.step_number)
        else:
            task.status = AgentTask.Status.FAILED
            task.save()
            
            TaskResult.objects.create(
                task=task,
                output_data=error_msg,
                execution_time=execution_time,
                tokens_used=tokens_used,
                status="FAILED",
                error_message=error_msg
            )
            
            step.status = WorkflowStep.StepStatus.FAILED
            step.save()
            failed_steps.add(step.step_number)

    def _run_steps_parallel(self, ready_steps, initial_input, completed_steps, failed_steps):
        # We can use ThreadPoolExecutor to run steps concurrently
        with ThreadPoolExecutor(max_workers=len(ready_steps)) as executor:
            futures = {
                executor.submit(self._run_step, step, initial_input, completed_steps, failed_steps): step
                for step in ready_steps
            }
            for future in as_completed(futures):
                step = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Exception during parallel execution of step {step.step_number}: {str(e)}")
                    step.status = WorkflowStep.StepStatus.FAILED
                    step.save()
                    failed_steps.add(step.step_number)

    def _should_execute_step(self, step):
        input_mapping = step.input_mapping or {}
        skip_condition = input_mapping.get("skip_if", None)
        if not skip_condition:
            return True
            
        prev_step_num = skip_condition.get("previous_step")
        contains_val = skip_condition.get("contains")
        if prev_step_num in self.step_results:
            prev_output = self.step_results[prev_step_num]
            if contains_val in prev_output:
                return False
        return True

    def _resolve_input_data(self, step, initial_input):
        input_mapping = step.input_mapping or {}
        source_step = input_mapping.get("source_step", None)
        if source_step and source_step in self.step_results:
            return self.step_results[source_step]
        return initial_input
