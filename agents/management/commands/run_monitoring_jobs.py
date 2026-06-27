from django.core.management.base import BaseCommand
from agents.services.monitoring_service import MonitoringService
from agents.scheduler import AgentOSScheduler


class Command(BaseCommand):
    help = "Triggers monitoring checks and populates system/student telemetry logs."

    def add_arguments(self, parser):
        parser.add_argument(
            '--job',
            type=str,
            help="Specify which job to run: 'telemetry' (runs health audits), 'student' (evaluates student progress), or 'scheduler' (runs AgentOS background jobs)."
        )

    def handle(self, *args, **options):
        job = options.get('job')

        if job == 'telemetry':
            self.stdout.write("Running telemetry check...")
            res = MonitoringService.run_telemetry_check()
            self.stdout.write(self.style.SUCCESS(f"Telemetry check complete. Overall status: {res['system_health']}"))
            
        elif job == 'student':
            self.stdout.write("Evaluating student analytics...")
            MonitoringService.process_student_analytics()
            self.stdout.write(self.style.SUCCESS("Student analytics processing complete."))
            
        elif job == 'scheduler':
            self.stdout.write("Running AgentOS scheduled background jobs...")
            AgentOSScheduler.run_minute_jobs()
            AgentOSScheduler.run_five_minute_jobs()
            AgentOSScheduler.run_ten_minute_jobs()
            AgentOSScheduler.run_hourly_jobs()
            AgentOSScheduler.run_daily_jobs()
            self.stdout.write(self.style.SUCCESS("AgentOS background scheduler tasks finished successfully."))
            
        else:
            self.stdout.write("Running all scheduled monitoring jobs...")
            
            # Telemetry checks
            t_res = MonitoringService.run_telemetry_check()
            self.stdout.write(f"- Telemetry: CPU/Memory logs generated. Status: {t_res['system_health']}")
            
            # Student checks
            MonitoringService.process_student_analytics()
            self.stdout.write("- Student experience scores and risk analytics completed.")
            
            # Predictions check
            pred = MonitoringService.run_predictions()
            self.stdout.write(f"- Growth predictions gathered (at-risk count: {pred['at_risk_students_count']})")
            
            # AgentOS jobs
            self.stdout.write("Triggering AgentOS scheduler routines...")
            AgentOSScheduler.run_minute_jobs()
            AgentOSScheduler.run_five_minute_jobs()
            AgentOSScheduler.run_ten_minute_jobs()
            AgentOSScheduler.run_hourly_jobs()
            AgentOSScheduler.run_daily_jobs()
            
            self.stdout.write(self.style.SUCCESS("All monitoring checks succeeded."))
