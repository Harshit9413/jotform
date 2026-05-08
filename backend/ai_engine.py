from __future__ import annotations
import json
from groq import Groq


class AIEngine:
    def __init__(self, api_key: str, schema: dict) -> None:
        self.client = Groq(api_key=api_key)
        self.schema = schema
        self.schema_text = self._build_schema_text()

    # ── schema text builder ─────────────────────────────────────
    def _build_schema_text(self) -> str:
        lines: list[str] = []
        for table, info in self.schema.items():
            lines.append(f"\nTable: {table}  ({info['row_count']} rows)")
            lines.append("Columns:")
            for col in info["columns"]:
                flags: list[str] = []
                if col["primary_key"]:
                    flags.append("PK")
                if col["foreign_key"]:
                    flags.append(f"FK→{col['foreign_key']}")
                if not col["nullable"]:
                    flags.append("NOT NULL")
                flag_str = f"  [{', '.join(flags)}]" if flags else ""
                lines.append(f"  - {col['name']} ({col['type']}){flag_str}")
            samples = info.get("sample_rows", [])
            if samples:
                lines.append("Sample rows:")
                for row in samples[:2]:
                    lines.append(f"  {json.dumps(row, default=str)}")
        return "\n".join(lines)

    # ── prompts ─────────────────────────────────────────────────
    def _build_sql_system_prompt(self) -> str:
        return f"""You are QueryMind, an expert AI SQL assistant that helps users explore their database using plain English.

DATABASE SCHEMA:
{self.schema_text}

RULES:
1. Generate ONLY SELECT queries — never INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or any data-modification query.
2. Use EXACT column and table names from the schema above.
3. Do NOT add a LIMIT clause unless the user explicitly asks for a specific number of rows (e.g. "top 10", "first 5", "last 20"). When the user asks for "all data", "full data", "all records", or a general query without a count, return all matching rows without any LIMIT.
4. Use proper JOINs when querying related tables (use foreign key relationships shown above).
5. For aggregations always include a GROUP BY on the appropriate column(s).
6. Handle NULLs with COALESCE or IS NULL checks where relevant.
7. If the user asks a greeting, meta question, or something unrelated to querying data, respond conversationally.

RESPONSE FORMAT — respond ONLY with valid JSON, no extra text:

For database queries:
{{"type": "sql", "sql": "SELECT ...", "explanation": "One sentence explaining what this query does."}}

For conversational replies:
{{"type": "conversation", "answer": "Your friendly response here."}}"""

    # ── inference ────────────────────────────────────────────────
    def generate_sql(self, question: str, conversation_history: list) -> dict:
        messages: list[dict] = [
            {"role": "system", "content": self._build_sql_system_prompt()}
        ]
        for msg in conversation_history[-6:]:
            messages.append({"role": msg["role"], "content": str(msg["content"])})
        messages.append({"role": "user", "content": question})

        resp = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=1000,
        )
        return json.loads(resp.choices[0].message.content)

    def generate_answer(
        self,
        question: str,
        sql: str,
        data: list,
        columns: list,
    ) -> str:
        preview = json.dumps(data[:20], default=str, indent=2)
        total = len(data)

        resp = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful data analyst. "
                        "Turn SQL query results into clear, concise natural language insights. "
                        "Max 150 words. Highlight key numbers in **bold**. "
                        "Use bullet points when listing multiple items. Be direct and informative."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n"
                        f"SQL used: {sql}\n"
                        f"Total rows returned: {total}\n"
                        f"Column names: {columns}\n"
                        f"Data sample (first 20 rows):\n{preview}\n\n"
                        "Provide a clear, insightful answer."
                    ),
                },
            ],
            temperature=0.3,
            max_tokens=400,
        )
        return resp.choices[0].message.content.strip()
