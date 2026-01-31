import asyncio
import os
from engine.sast.scanner import SastScanner
from engine.llm.analyzer import LLMAnalyzer
from schemas.finding import Finding

class ScanOrchestrator:
    def __init__(self):
        self.sast = SastScanner()
        self.llm = LLMAnalyzer()

    async def scan_directory(self, project_path: str):
        print(f"[*] Starting scan on {project_path}")
        all_findings = []
        
        # 1. Discovery (Simple walk for demo)
        files_to_scan = []
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith((".py", ".js", ".java")):
                    files_to_scan.append(os.path.join(root, file))

        # 2. SAST Phase
        print(f"[*] Running SAST on {len(files_to_scan)} files...")
        sast_tasks = [self.sast.scan_file(f) for f in files_to_scan]
        raw_results = await asyncio.gather(*sast_tasks)
        
        # Flatten list
        flat_findings = [item for sublist in raw_results for item in sublist]
        print(f"[*] SAST identified {len(flat_findings)} potential issues.")

        # 3. AI Enrichment Phase
        enrichment_tasks = []
        final_findings = []
        
        for finding in flat_findings:
            # Only enrich HIGH/CRITICAL to save tokens in this demo
            if finding.severity in ["CRITICAL", "HIGH"]:
                try:
                    with open(finding.location.file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    enrichment_tasks.append(
                        self.llm.enrich_finding(finding, content)
                    )
                except Exception:
                    final_findings.append(finding)
            else:
                final_findings.append(finding)
        
        if enrichment_tasks:
            print(f"[*] Enriching {len(enrichment_tasks)} critical findings with AI...")
            enriched = await asyncio.gather(*enrichment_tasks)
            final_findings.extend(enriched)

        return final_findings
