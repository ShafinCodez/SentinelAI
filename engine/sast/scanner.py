import subprocess
import json
import uuid
from typing import List
from schemas.finding import Finding, Severity, CodeLocation, Remediation, FindingType

class SastScanner:
    def __init__(self, rules_path: str = "config/rules"):
        self.rules_path = rules_path

    async def scan_file(self, file_path: str) -> List[Finding]:
        """Runs Semgrep as a subprocess for rapid deterministic analysis."""
        # Note: In a real deployment, we would ensure rules exist or use registry
        cmd = ["semgrep", "--config=p/security-audit", "--json", file_path]
        
        try:
            # Using subprocess directly for demonstration
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0 and not result.stdout:
                print(f"Semgrep Error: {result.stderr}")
                return []
                
            output = json.loads(result.stdout)
            return self._normalize_results(output, file_path)
        except Exception as e:
            print(f"SAST Scan failed for {file_path}: {e}")
            return []

    def _normalize_results(self, raw_data: dict, file_path: str) -> List[Finding]:
        findings = []
        for result in raw_data.get("results", []):
            findings.append(Finding(
                id=str(uuid.uuid4()),
                title=result["extra"]["message"],
                description=result["extra"]["metadata"].get("description", "Potential Issue"),
                severity=Severity(result["extra"]["severity"].upper()),
                cwe_id=result["extra"]["metadata"].get("cwe", ["Unknown"])[0],
                location=CodeLocation(
                    file_path=file_path,
                    start_line=result["start"]["line"],
                    end_line=result["end"]["line"],
                    snippet=result["extra"]["lines"]
                ),
                type=FindingType.SAST,
                confidence_score=0.8,
                remediation=Remediation(
                    description="Pending AI Enrichment",
                    fixed_code=""
                )
            ))
        return findings
