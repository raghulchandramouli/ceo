"""PostgreSQL tenant isolation policies."""


def tenant_rls_statements(table_name: str, tenant_column: str) -> tuple[str, str, str]:
    table = '"' + table_name.replace('"', '""') + '"'
    column = '"' + tenant_column.replace('"', '""') + '"'
    predicate = f"{column} = NULLIF(current_setting('app.tenant_id', true), '')::uuid"
    return (
        f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY",
        f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY",
        f"CREATE POLICY tenant_isolation ON {table} USING ({predicate}) WITH CHECK ({predicate})",
    )
