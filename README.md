# Lakebase-Powered AI Support App

A small Flask app backed by Databricks Lakebase (managed Postgres) that lets users
create support tickets, add messages, and update ticket status.

## Files

- `app.py` — Flask app with full CRUD (list tickets, view/add messages, create ticket,
  update status, delete ticket, filter by status, stats)
- `templates/index.html`, `templates/ticket.html` — pages
- `static/style.css` — styling
- `app.yaml` — Databricks App runtime config (fill in placeholders)
- `requirements.txt` — Python dependencies
- `01_setup_role.sql` — grants your app's service principal an OAuth Postgres role
- `02_schema_and_sample_data.sql` — creates `tickets` / `ticket_messages` + sample rows

## Setup

### 1. Create the Databricks App
Apps -> Create app -> Flask Hello World template. Note the `DATABRICKS_CLIENT_ID`
from the app's Environment tab. Don't deploy yet.

### 2. Create the Lakebase database
App switcher -> Lakebase Postgres -> Create project. Wait ~1 min for compute.

### 3. Run the SQL setup
In the Lakebase SQL Editor, run `01_setup_role.sql` then `02_schema_and_sample_data.sql`,
replacing `<DATABRICKS_CLIENT_ID>` in both files with your real client ID first.

### 4. Configure app.yaml
Fill in `PGHOST`, `PGUSER`, and `ENDPOINT_NAME` using the values from the Lakebase
project's Connect modal ("Parameters only") and the branch's Computes tab
("Get ID" -> "Copy resource name").

### 5. Test locally
```bash
databricks auth login
export PGHOST="<your-endpoint-hostname>"
export PGDATABASE="databricks_postgres"
export PGUSER="your.email@company.com"   # your own email for local testing
export PGPORT="5432"
export PGSSLMODE="require"
export ENDPOINT_NAME="<your-endpoint-name>"
export FLASK_SECRET_KEY="dev"

pip3 install --upgrade -r requirements.txt
python3 app.py
```
Open http://localhost:8000 — you should see the 3 sample tickets.

Note: for local testing, your own Databricks user account also needs the same
GRANTs run against it (or just log in with a role that already has them) — simplest
is to temporarily also grant your user account the same SELECT/INSERT/UPDATE/DELETE
permissions used in `02_schema_and_sample_data.sql`.

### 6. Deploy
```bash
databricks sync . /Workspace/Users/<your-email>/support-ticket-app
databricks apps deploy support-ticket-app --source-code-path /Workspace/Users/<your-email>/support-ticket-app
```

### 7. Verify
- Existing tickets load
- Create a new ticket -> appears in the list
- Open a ticket, add a message -> appears immediately
- Update status -> badge changes
- Refresh the page -> everything persists (proves it's reading from Lakebase, not memory)

## Reflection (fill in for submission)

- **Most difficult part:** _(your answer)_
- **Lakebase vs. a traditional analytics table:** Lakebase is a row-oriented, transactional
  Postgres database optimized for many small, fast reads/writes (OLTP) — like a single
  ticket insert or status update — with OAuth-secured per-request connections. A
  traditional analytics table (e.g. Delta/Parquet on the lakehouse) is column-oriented
  and optimized for scanning large volumes of historical data for aggregation/BI, not for
  single-row transactional updates.
- **What I'd add next:** _(your answer, e.g. ticket assignment to a specific agent,
  email notifications on new messages, full-text search across tickets)
