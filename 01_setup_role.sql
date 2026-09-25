-- Run this in the Lakebase SQL Editor.
-- Replace <DATABRICKS_CLIENT_ID> with the value from your App's Environment tab.

CREATE EXTENSION IF NOT EXISTS databricks_auth;

SELECT databricks_create_role('<DATABRICKS_CLIENT_ID>', 'SERVICE_PRINCIPAL');

GRANT CONNECT ON DATABASE databricks_postgres TO "<DATABRICKS_CLIENT_ID>";
GRANT CREATE, USAGE ON SCHEMA public TO "<DATABRICKS_CLIENT_ID>";
