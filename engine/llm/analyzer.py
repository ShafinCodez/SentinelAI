import os
import json
from openai import AsyncOpenAI
from schemas.finding import Finding, Remediation
from engine.graph.context_builder import ContextBuilder

class LLMAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.context_builder = ContextBuilder()

    async def enrich_finding(self, finding: Finding, full_file_content: str) -> Finding:
        if not self.api_key or "placeholder" in self.api_key:
            finding.description += " [AI Enrichment Skipped: No API Key]"
            return finding

        context = self.context_builder.get_context(finding.location, full_file_content)
        
        prompt = f"""
        You are an expert Application Security Engineer. 
        Analyze this SAST finding.

        Vulnerability: {finding.title}
        File: {finding.location.file_path}
        
        Code Context:
        ```
        {context}
        ```

        Task:
        1. Assess if this is a True Positive.
        2. Provide a secure code fix.
        
        Respond in JSON:
        {{
            "is_true_positive": boolean,
            "confidence": float,
            "explanation": string,
            "fix_code": string
        }}
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            analysis = json.loads(response.choices[0].message.content)

            if not analysis["is_true_positive"]:
                finding.confidence_score = 0.1
                finding.description = f"[Suspected False Positive] {analysis["explanation"]}"
            else:
                finding.confidence_score = analysis["confidence"]
                finding.description = analysis["explanation"]
                finding.remediation = Remediation(
                    description="AI Generated Fix",
                    fixed_code=analysis["fix_code"]
                )
        except Exception as e:
            print(f"LLM Error: {e}")
            
        return finding
