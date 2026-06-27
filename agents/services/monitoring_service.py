import logging
import csv
import io
from django.utils import timezone
from django.db.models import Avg, Sum, Count
from ..models import (
    Agent, AgentExecution, SystemHealth, AgentHealth, DatabaseHealth,
    StorageHealth, APIHealth, StudentAnalytics, CRAnalytics,
    AdminAnalytics, AIAnalytics, Alert, Recommendation
)
from accounts.models import Student, CR
from academics.models import Section, SemesterSubject, SemesterSubject as AcademicSubject

logger = logging.getLogger(__name__)


class MonitoringService:
    """
    MonitoringService handles telemetry gathering, calculations for Student Experience scores,
    alert creation, prediction metrics, and exporting analytical reports.
    """

    @staticmethod
    def calculate_student_experience_score(student):
        """
        Calculates a score between 0 and 100 based on the student's metrics:
        - Assignment completion rate (40%)
        - AI assignment accuracy (30%)
        - Daily usage consistency (30%)
        """
        try:
            # Look up existing analytics history or calculate dynamically
            # For dynamic calculation, we look at progress records:
            progress_records = student.subject_progress.all()
            if not progress_records.exists():
                return 75  # Default baseline score

            total_comp = sum([p.completion_percentage for p in progress_records]) / progress_records.count()
            
            # Simulated usage consistency (baseline is 80%)
            usage_factor = 85.0
            
            # Simulated AI accuracy
            ai_accuracy = 90.0

            # Weights calculation
            score = (float(total_comp) * 0.40) + (ai_accuracy * 0.30) + (usage_factor * 0.30)
            return int(min(max(score, 0), 100))
        except Exception as e:
            logger.error(f"Error calculating experience score: {str(e)}")
            return 70

    @staticmethod
    def run_telemetry_check():
        """
        Simulates gathering real-time telemetry from QISHub nodes and saves it into health models.
        Automatically generates warnings/alerts based on telemetry thresholds.
        """
        now = timezone.now()

        # 1. System Health
        sys_health = SystemHealth.objects.create(
            overall_status="HEALTHY",
            cpu_usage=18.5,
            memory_usage=45.2,
            active_connections=12
        )

        # 2. Agent Health
        for agent in Agent.objects.all():
            executions = AgentExecution.objects.filter(agent=agent)
            avg_exec = executions.aggregate(Avg('execution_time'))['execution_time__avg'] or 0.0
            error_count = executions.filter(status='FAILED').count()
            
            AgentHealth.objects.create(
                agent=agent,
                status="RUNNING" if error_count < 3 else "ERROR",
                avg_response_time=avg_exec * 1.1,
                avg_execution_time=avg_exec,
                error_count=error_count,
                retry_count=0,
                last_executed_at=executions.order_by('-started_at').values_list('started_at', flat=True).first()
            )

        # 3. Database Health
        db_health = DatabaseHealth.objects.create(
            connections_count=15,
            slow_queries_count=0,
            cache_hit_ratio=99.4,
            table_sizes={"accounts_user": "450KB", "academics_semester": "120KB", "agents_agentexecution": "2.1MB"},
            index_usage_stats={"idx_agent_slug": "95%", "idx_execution_task": "88%"},
            migration_status="UP_TO_DATE",
            suggestions="Database is operating inside optimal thresholds."
        )

        # 4. Storage Health
        storage_health = StorageHealth.objects.create(
            bucket_name="StudentHub",
            storage_size_bytes=104857600, # 100MB
            file_count=240,
            broken_urls_count=0,
            upload_failures_count=1,
            download_speed_kbps=4500.0,
            duplicate_files_count=3
        )

        # 5. API Health
        api_health = APIHealth.objects.create(
            endpoint="/agents/run/",
            avg_response_time=0.45,
            success_rate=98.5,
            failure_rate=1.5,
            auth_errors_count=2,
            validation_errors_count=5,
            traffic_count=120
        )

        # 6. Generate Alerts & Recommendations if necessary
        if storage_health.storage_size_bytes > 800000000: # Limit simulation
            Alert.objects.create(
                title="Storage Almost Full",
                message="Supabase Storage bucket StudentHub has exceeded 80% usage threshold.",
                alert_type=Alert.AlertType.STORAGE,
                severity=Alert.Severity.WARNING
            )
            Recommendation.objects.create(
                title="Storage cleanup recommended",
                message="Supabase Storage is reaching 80%. Clean up duplicate files.",
                category=Recommendation.Category.SYSTEM
            )

        if storage_health.duplicate_files_count > 0:
            Recommendation.objects.create(
                title="Duplicate resources detected",
                message=f"Detected {storage_health.duplicate_files_count} duplicate files in StudentHub.",
                category=Recommendation.Category.DATABASE
            )

        return {
            "system_health": sys_health.overall_status,
            "db_status": db_health.migration_status,
            "files_count": storage_health.file_count
        }

    @staticmethod
    def process_student_analytics():
        """
        Evaluates student statistics and creates alert notifications for students who are falling behind.
        """
        for student in Student.objects.all():
            score = MonitoringService.calculate_student_experience_score(student)
            
            # Simulate completion rate
            progress_records = student.subject_progress.all()
            avg_completion = float(progress_records.aggregate(Avg('completion_percentage'))['completion_percentage__avg'] or 0.0)
            
            status = 'ON_TRACK'
            rec_msg = "Keep up the consistent effort!"
            
            if avg_completion < 50.0:
                status = 'AT_RISK'
                rec_msg = "Your DBMS unit completion is low. Dedicate time to review Unit 3 concepts."
                
                # Create Alerts and Recommendations
                Alert.objects.create(
                    title="Student falling behind",
                    message=f"Student {student.name} has completion rate of {avg_completion}%, placing them at risk.",
                    alert_type=Alert.AlertType.ACADEMIC,
                    severity=Alert.Severity.WARNING,
                    student=student
                )
                Recommendation.objects.create(
                    title="Provide Academic Support",
                    message=f"Students are struggling with DBMS Unit 3. Set up a tutorial section B study plan.",
                    category=Recommendation.Category.ACADEMIC,
                    student=student,
                    section=student.section
                )

            StudentAnalytics.objects.create(
                student=student,
                dashboard_load_time=0.35,
                assignment_completion_rate=avg_completion,
                ai_assignment_accuracy=88.5,
                daily_usage_minutes=25.0,
                activity_score=avg_completion * 1.1,
                experience_score=score,
                progress_status=status,
                personalized_recommendations=rec_msg
            )

    @staticmethod
    def run_predictions():
        """
        Performs observation logic to predict storage, database scaling constraints, and student risks.
        """
        at_risk_students = StudentAnalytics.objects.filter(progress_status='AT_RISK').count()
        storage_growth = 12.5 # Predicted storage growth percentage
        
        return {
            "at_risk_students_count": at_risk_students,
            "predicted_storage_growth_pct": storage_growth,
            "predicted_database_growth_pct": 5.8,
            "exam_readiness_avg_pct": 82.4
        }

    @staticmethod
    def generate_report(report_type):
        """
        Generates structured data report matching daily, weekly, or monthly logs.
        """
        now = timezone.now()
        report_data = {
            "report_type": report_type,
            "timestamp": now.isoformat(),
            "metrics": {
                "overall_status": "HEALTHY",
                "active_users": Student.objects.count(),
                "alerts_raised": Alert.objects.filter(is_resolved=False).count(),
                "recommendations_count": Recommendation.objects.count()
            }
        }
        return report_data

    @staticmethod
    def export_csv_to_string(queryset, fields):
        """
        Helper utility to compile query records into CSV string.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(fields)
        for obj in queryset:
            row = []
            for field in fields:
                val = getattr(obj, field, None)
                if callable(val):
                    val = val()
                row.append(str(val) if val is not None else '')
            writer.writerow(row)
        return output.getvalue()

    @staticmethod
    def export_excel_html_string(queryset, fields):
        """
        Helper utility to compile query records into a clean, Excel-loadable HTML table layout.
        """
        output = io.StringIO()
        output.write('<html xmlns:x="urn:schemas-microsoft-com:office:excel">\n')
        output.write('<head><meta charset="utf-8"></head>\n')
        output.write('<body>\n<table border="1">\n')
        
        # Headers
        output.write('  <tr>\n')
        for field in fields:
            output.write(f'    <th>{field}</th>\n')
        output.write('  </tr>\n')
        
        # Rows
        for obj in queryset:
            output.write('  <tr>\n')
            for field in fields:
                val = getattr(obj, field, None)
                if callable(val):
                    val = val()
                output.write(f'    <td>{val if val is not None else ""}</td>\n')
            output.write('  </tr>\n')
            
        output.write('</table>\n</body>\n</html>')
        return output.getvalue()

    @staticmethod
    def export_pdf_html_string(queryset, fields, title="Analytical Report"):
        """
        Helper utility to compile query records into a clean, printable HTML-based PDF format.
        """
        output = io.StringIO()
        output.write('<!DOCTYPE html>\n<html>\n<head>\n')
        output.write('<style>\n')
        output.write('  body { font-family: sans-serif; margin: 30px; color: #333; }\n')
        output.write('  h1 { text-align: center; color: #1a2a3a; }\n')
        output.write('  table { width: 100%; border-collapse: collapse; margin-top: 20px; }\n')
        output.write('  th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }\n')
        output.write('  th { background-color: #1a2a3a; color: white; }\n')
        output.write('  tr:nth-child(even) { background-color: #f9f9f9; }\n')
        output.write('</style>\n</head>\n<body>\n')
        
        output.write(f'<h1>{title}</h1>\n')
        output.write(f'<p>Generated at: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}</p>\n')
        
        output.write('<table>\n  <thead>\n    <tr>\n')
        for field in fields:
            output.write(f'      <th>{field}</th>\n')
        output.write('    </tr>\n  </thead>\n  <tbody>\n')
        
        for obj in queryset:
            output.write('    <tr>\n')
            for field in fields:
                val = getattr(obj, field, None)
                if callable(val):
                    val = val()
                output.write(f'      <td>{val if val is not None else ""}</td>\n')
            output.write('    </tr>\n')
            
        output.write('  </tbody>\n</table>\n</body>\n</html>')
        return output.getvalue()
