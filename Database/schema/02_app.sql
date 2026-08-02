CREATE TABLE app.conversations (
    id varchar PRIMARY KEY,
    user_sub varchar NOT NULL,
    surface varchar NOT NULL,
    title varchar,
    status varchar NOT NULL DEFAULT 'active',
    deleted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);
CREATE INDEX ix_conversations_user_sub ON app.conversations (user_sub);

CREATE TABLE app.messages (
    id varchar PRIMARY KEY,
    conversation_id varchar NOT NULL,
    role varchar NOT NULL,
    content text NOT NULL,
    metadata jsonb,
    job_id varchar,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT uq_message_job UNIQUE (job_id),
    CONSTRAINT fk_messages_conversation_id_conversations
        FOREIGN KEY (conversation_id) REFERENCES app.conversations (id) ON DELETE CASCADE
);
CREATE INDEX ix_messages_conversation_id ON app.messages (conversation_id);

CREATE TABLE app.tickets (
    id varchar PRIMARY KEY,
    jira_key varchar NOT NULL,
    type varchar NOT NULL,
    title varchar NOT NULL,
    summary text,
    status varchar,
    conversation_id varchar,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT uq_ticket_jira_key UNIQUE (jira_key)
);

CREATE TABLE app.ticket_reporters (
    id varchar PRIMARY KEY,
    ticket_id varchar NOT NULL,
    user_sub varchar NOT NULL,
    user_name varchar,
    added_at timestamp with time zone DEFAULT now(),
    CONSTRAINT uq_ticket_reporter UNIQUE (ticket_id, user_sub),
    CONSTRAINT fk_ticket_reporters_ticket_id_tickets
        FOREIGN KEY (ticket_id) REFERENCES app.tickets (id) ON DELETE CASCADE
);

CREATE TABLE app.jobs (
    id varchar PRIMARY KEY,
    type varchar NOT NULL DEFAULT 'create_ticket',
    status varchar NOT NULL DEFAULT 'queued',
    conversation_id varchar NOT NULL,
    user_sub varchar NOT NULL,
    payload jsonb NOT NULL,
    jira_key varchar,
    action varchar,
    attempts integer NOT NULL DEFAULT 0,
    last_error text,
    locked_at timestamp with time zone,
    locked_by varchar,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);
CREATE INDEX ix_jobs_status ON app.jobs (status);

CREATE TABLE app.notifications (
    id varchar PRIMARY KEY,
    user_sub varchar NOT NULL,
    conversation_id varchar,
    type varchar NOT NULL,
    title varchar NOT NULL,
    body text NOT NULL,
    jira_key varchar,
    job_id varchar,
    delivered_at timestamp with time zone,
    read_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT uq_notification_job UNIQUE (job_id)
);
CREATE INDEX ix_notifications_user_created ON app.notifications (user_sub, created_at DESC);
CREATE INDEX ix_notifications_unread ON app.notifications (user_sub, created_at DESC)
    WHERE read_at IS NULL;
CREATE INDEX ix_notifications_undelivered ON app.notifications (user_sub)
    WHERE delivered_at IS NULL;
