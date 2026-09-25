import os

from flask import Flask, render_template, request, redirect, url_for, flash
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

VALID_STATUSES = ["open", "in_progress", "resolved"]
VALID_PRIORITIES = ["low", "medium", "high"]

# ---------------------------------------------------------------------------
# Lakebase connection: password-based auth
# ---------------------------------------------------------------------------

username = os.environ["PGUSER"]
password = os.environ["PGPASSWORD"]
host = os.environ["PGHOST"]
port = os.environ.get("PGPORT", "5432")
database = os.environ["PGDATABASE"]
sslmode = os.environ.get("PGSSLMODE", "require")

pool = ConnectionPool(
    conninfo=f"dbname={database} user={username} password={password} host={host} port={port} sslmode={sslmode}",
    min_size=1,
    max_size=10,
    open=True,
    kwargs={"row_factory": dict_row},
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    status_filter = request.args.get("status", "")  # bonus: filter by status
    search_query = request.args.get("q", "").strip()  # bonus: search by title

    query = """
        SELECT t.*, (SELECT COUNT(*) FROM ticket_messages tm WHERE tm.ticket_id = t.ticket_id) AS message_count
        FROM tickets t
    """
    params = []
    conditions = []
    if status_filter in VALID_STATUSES:
        conditions.append("t.status = %s")
        params.append(status_filter)
    if search_query:
        conditions.append("t.title ILIKE %s")
        params.append(f"%{search_query}%")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY t.created_at DESC"

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            tickets = cur.fetchall()

            # bonus: stats by status
            cur.execute("SELECT status, COUNT(*) AS n FROM tickets GROUP BY status")
            status_counts = {row["status"]: row["n"] for row in cur.fetchall()}

            # bonus: stats by priority
            cur.execute("SELECT priority, COUNT(*) AS n FROM tickets GROUP BY priority")
            priority_counts = {row["priority"]: row["n"] for row in cur.fetchall()}

            # total count (unfiltered)
            cur.execute("SELECT COUNT(*) AS n FROM tickets")
            total_count = cur.fetchone()["n"]

    return render_template(
        "index.html",
        tickets=tickets,
        status_counts=status_counts,
        priority_counts=priority_counts,
        total_count=total_count,
        statuses=VALID_STATUSES,
        active_filter=status_filter,
        search_query=search_query,
    )


@app.route("/ticket/new", methods=["POST"])
def create_ticket():
    title = request.form.get("title", "").strip()
    created_by = request.form.get("created_by", "").strip()
    priority = request.form.get("priority", "medium")
    category = request.form.get("category", "").strip() or None

    # bonus: input validation
    errors = []
    if not title:
        errors.append("Title is required.")
    if not created_by:
        errors.append("Your name/email is required.")
    if priority not in VALID_PRIORITIES:
        errors.append("Invalid priority.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("index"))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO tickets (title, status, priority, category, created_by)
                   VALUES (%s, 'open', %s, %s, %s)""",
                (title, priority, category, created_by),
            )

    flash("Ticket created.", "success")
    return redirect(url_for("index"))


@app.route("/ticket/<int:ticket_id>")
def view_ticket(ticket_id):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tickets WHERE ticket_id = %s", (ticket_id,))
            ticket = cur.fetchone()
            if not ticket:
                flash("Ticket not found.", "error")
                return redirect(url_for("index"))

            cur.execute(
                "SELECT * FROM ticket_messages WHERE ticket_id = %s ORDER BY created_at ASC",
                (ticket_id,),
            )
            messages = cur.fetchall()

    return render_template(
        "ticket.html", ticket=ticket, messages=messages, statuses=VALID_STATUSES
    )


@app.route("/ticket/<int:ticket_id>/message", methods=["POST"])
def add_message(ticket_id):
    message_text = request.form.get("message_text", "").strip()
    author = request.form.get("author", "").strip()

    if not message_text or not author:
        flash("Both message and author are required.", "error")
        return redirect(url_for("view_ticket", ticket_id=ticket_id))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM tickets WHERE ticket_id = %s", (ticket_id,))
            if not cur.fetchone():
                flash("Ticket not found.", "error")
                return redirect(url_for("index"))

            cur.execute(
                """INSERT INTO ticket_messages (ticket_id, message_text, author)
                   VALUES (%s, %s, %s)""",
                (ticket_id, message_text, author),
            )

    flash("Message added.", "success")
    return redirect(url_for("view_ticket", ticket_id=ticket_id))


@app.route("/ticket/<int:ticket_id>/status", methods=["POST"])
def update_status(ticket_id):
    new_status = request.form.get("status", "")

    if new_status not in VALID_STATUSES:
        flash("Invalid status.", "error")
        return redirect(url_for("view_ticket", ticket_id=ticket_id))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tickets SET status = %s WHERE ticket_id = %s",
                (new_status, ticket_id),
            )

    flash(f"Status updated to '{new_status}'.", "success")
    return redirect(url_for("view_ticket", ticket_id=ticket_id))


@app.route("/ticket/<int:ticket_id>/delete", methods=["POST"])
def delete_ticket(ticket_id):
    # bonus: delete with confirmation (confirmation happens client-side in the template)
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tickets WHERE ticket_id = %s", (ticket_id,))

    flash("Ticket deleted.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
