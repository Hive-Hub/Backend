import logging
import re

logger = logging.getLogger(__name__)


class ReviewService:
    """
    Service to help with security code scan, performance reviews, and duplicate pattern checks.
    """

    @staticmethod
    def audit_security_and_practices(code_snippet):
        """
        Parses python code snippets to audit typical Django security pitfalls and duplicates.
        """
        findings = []
        
        # 1. Unsafe RAW SQL check
        if re.search(r'\.raw\(', code_snippet) or re.search(r'execute\(', code_snippet):
            findings.append({
                "type": "SECURITY_WARNING",
                "message": "Detected direct RAW SQL executions. Ensure parameterized queries are used to prevent SQL injections."
            })
            
        # 2. Hardcoded secret pattern check
        secret_keys = ['api_key', 'secret_key', 'password', 'token', 'access_key']
        for key in secret_keys:
            pattern = rf'{key}\s*=\s*[\'"][^\'"]+[\'"]'
            if re.search(pattern, code_snippet, re.IGNORECASE):
                findings.append({
                    "type": "SECURITY_CRITICAL",
                    "message": f"Potential hardcoded credentials detected for key '{key}'. Load from settings or environment instead."
                })

        # 3. Model inheritance check
        if "models.Model" in code_snippet and "def __str__" not in code_snippet:
            findings.append({
                "type": "BEST_PRACTICE",
                "message": "Django model detected without a __str__ method definition."
            })

        return {
            "is_clean": len(findings) == 0,
            "findings": findings
        }
