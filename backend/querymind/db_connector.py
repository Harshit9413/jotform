from __future__ import annotations
import re
from decimal import Decimal
from datetime import datetime, date, time
from sqlalchemy import create_engine, text, inspect


_BLOCKED = re.compile(
    r'\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|EXEC|EXECUTE|GRANT|REVOKE|CREATE|REPLACE|MERGE)\b'
    r'|--|/\*|\*/',
    re.IGNORECASE,
)


class DatabaseConnector:
    def __init__(self, db_url: str) -> None:
        self.db_url = db_url
        self.db_type = self._detect_type(db_url)
        self.engine = create_engine(db_url, pool_pre_ping=True)
        with self.engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    # ── helpers ────────────────────────────────────────────────
    @staticmethod
    def _detect_type(url: str) -> str:
        if url.startswith(("postgresql", "postgres")):
            return "postgresql"
        if url.startswith("mysql"):
            return "mysql"
        if url.startswith("sqlite"):
            return "sqlite"
        return "sql"

    @staticmethod
    def _ser(val):
        if isinstance(val, (datetime, date, time)):
            return str(val)
        if isinstance(val, Decimal):
            return float(val)
        if isinstance(val, bytes):
            return val.hex()
        return val

    # ── schema ─────────────────────────────────────────────────
    def extract_schema(self) -> dict:
        inspector = inspect(self.engine)
        schema: dict = {}

        for table in inspector.get_table_names():
            pk_cols: set[str] = set(
                inspector.get_pk_constraint(table).get("constrained_columns", [])
            )
            fk_map: dict[str, str] = {}
            for fk in inspector.get_foreign_keys(table):
                for col in fk["constrained_columns"]:
                    ref_cols = fk.get("referred_columns", [])
                    ref_col = ref_cols[0] if ref_cols else "?"
                    fk_map[col] = f"{fk['referred_table']}.{ref_col}"

            columns = []
            for col in inspector.get_columns(table):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "primary_key": col["name"] in pk_cols,
                    "foreign_key": fk_map.get(col["name"]),
                })

            # row count
            row_count: int | str = "unknown"
            with self.engine.connect() as conn:
                try:
                    row_count = conn.execute(
                        text(f"SELECT COUNT(*) FROM {table}")  # noqa: S608
                    ).scalar() or 0
                except Exception:
                    pass

            # 3 sample rows
            sample_rows: list[dict] = []
            with self.engine.connect() as conn:
                try:
                    res = conn.execute(
                        text(f"SELECT * FROM {table} LIMIT 3")  # noqa: S608
                    )
                    keys = list(res.keys())
                    for row in res.fetchall():
                        sample_rows.append(
                            dict(zip(keys, [self._ser(v) for v in row]))
                        )
                except Exception:
                    pass

            schema[table] = {
                "columns": columns,
                "row_count": row_count,
                "sample_rows": sample_rows,
            }

        return schema

    # ── safety ─────────────────────────────────────────────────
    def is_safe_query(self, sql: str) -> tuple[bool, str]:
        if _BLOCKED.search(sql):
            return False, "Query contains blocked keywords or patterns."
        stripped = sql.strip().rstrip(";")
        if ";" in stripped:
            return False, "Multiple statements are not allowed."
        if not re.match(r"^\s*SELECT\b", sql.strip(), re.IGNORECASE):
            return False, "Only SELECT queries are permitted."
        return True, ""

    # ── execution ──────────────────────────────────────────────
    def execute_query(self, sql: str, max_rows: int = 100000) -> dict:
        ok, reason = self.is_safe_query(sql)
        if not ok:
            raise ValueError(reason)
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            # Fetch one extra row to detect truncation without a false-positive
            # when the DB happens to have exactly max_rows rows.
            rows = result.fetchmany(max_rows + 1)
            truncated = len(rows) > max_rows
            if truncated:
                rows = rows[:max_rows]
            data = [
                dict(zip(columns, [self._ser(v) for v in row]))
                for row in rows
            ]
        return {
            "data": data,
            "columns": columns,
            "row_count": len(data),
            "truncated": truncated,
        }

    def close(self) -> None:
        self.engine.dispose()
