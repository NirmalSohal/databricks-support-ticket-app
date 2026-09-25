-- Run this AFTER 01_setup_role.sql, in the same Lakebase SQL Editor.
-- Replace <DATABRICKS_CLIENT_ID> with the same value used in step 1.

-- ---------- Schema ----------

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id   SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'open',          -- open | in_progress | resolved
    priority    TEXT NOT NULL DEFAULT 'medium',        -- low | medium | high   (bonus: priority)
    category    TEXT,                                   -- bonus: category
    created_by  TEXT NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ticket_messages (
    message_id    SERIAL PRIMARY KEY,
    ticket_id     INTEGER NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    message_text  TEXT NOT NULL,
    author        TEXT NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket_id ON ticket_messages(ticket_id);

-- ---------- Permissions for the app's service principal ----------
-- Service principals don't inherit default schema permissions, so grant explicitly.

GRANT SELECT, INSERT, UPDATE, DELETE ON tickets TO "<DATABRICKS_CLIENT_ID>";
GRANT SELECT, INSERT, UPDATE, DELETE ON ticket_messages TO "<DATABRICKS_CLIENT_ID>";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "<DATABRICKS_CLIENT_ID>";

-- ---------- Sample data ----------

INSERT INTO tickets (title, status, priority, category, created_by) VALUES
    ('Cannot log into VPN', 'open', 'high', 'network', 'alice@company.com'),
    ('Laptop fan making noise', 'in_progress', 'low', 'hardware', 'bob@company.com'),
    ('Need access to Finance dashboard', 'resolved', 'medium', 'access', 'carol@company.com');

-- Two+ messages per ticket
INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES
    (1, 'I get a timeout error every time I try to connect.', 'alice@company.com'),
    (1, 'Can you confirm which VPN client version you are using?', 'support@company.com'),
    (2, 'The fan spins loudly on startup, then quiets down.', 'bob@company.com'),
    (2, 'Sending you a replacement laptop, tracking to follow.', 'support@company.com'),
    (3, 'Requesting read access to the Finance dashboard for Q3 reporting.', 'carol@company.com'),
    (3, 'Access granted, please confirm you can see it.', 'support@company.com');
