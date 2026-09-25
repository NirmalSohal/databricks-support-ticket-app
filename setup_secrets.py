"""
One-time setup script: creates the Databricks secret scope and stores the
Massive API key. Run this locally (with the Databricks CLI configured) or
from a notebook - never commit the resulting secret value anywhere.

Usage:
    python setup_secrets.py
"""
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
import getpass

w = WorkspaceClient()

# w.secrets.create_scope(scope="massive")
# w.secrets.put_secret(
#     scope="massive",
#     key="api-key",
#     string_value=getpass.getpass("Paste your Massive API key: ")
# )

w.secrets.create_scope(scope="database_ticket_system")
w.secrets.put_secret(
    scope="database_ticket_system",
    key="lakebase-ticket-system-url",
    string_value=getpass.getpass("Paste your Lakebase URL: ")
)


w.secrets.put_acl(
    scope="database_ticket_system",
    principal="users",
    permission=workspace.AclPermission.READ,
)

# w.secrets.put_acl(
#     scope="massive",
#     principal="users",
#     permission=workspace.AclPermission.READ,
# )
