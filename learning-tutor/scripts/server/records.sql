-- Run transactionally as database owner. Runtime role receives named-table grants.
CREATE SCHEMA IF NOT EXISTS learning;
CREATE TABLE IF NOT EXISTS learning.profiles (
    profile text PRIMARY KEY,
    server_id uuid NOT NULL,
    cursor bigint NOT NULL DEFAULT 0 CHECK(cursor >= 0)
);
CREATE TABLE IF NOT EXISTS learning.topics (
    profile text NOT NULL REFERENCES learning.profiles(profile),
    topic text NOT NULL,
    key text NOT NULL,
    title text NOT NULL,
    PRIMARY KEY(profile,topic)
);
CREATE TABLE IF NOT EXISTS learning.events (
    profile text NOT NULL REFERENCES learning.profiles(profile),
    id text NOT NULL,
    cursor bigint NOT NULL,
    topic text NOT NULL,
    session text NOT NULL,
    device text NOT NULL,
    seq bigint NOT NULL,
    kind text NOT NULL CHECK(kind IN ('topic','alias','session','message','assessment','checkpoint','delete')),
    at timestamptz NOT NULL,
    envelope text NOT NULL,
    data jsonb NOT NULL,
    projection_escaped boolean NOT NULL DEFAULT false,
    hash text NOT NULL CHECK(hash ~ '^[0-9a-f]{64}$'),
    committed_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY(profile,id),
    UNIQUE(profile,cursor),
    UNIQUE(profile,device,seq)
);
CREATE INDEX IF NOT EXISTS events_topic_cursor ON learning.events(profile,topic,cursor);
CREATE TABLE IF NOT EXISTS learning.receipts (
    profile text NOT NULL REFERENCES learning.profiles(profile),
    id text NOT NULL,
    hash text NOT NULL,
    device text NOT NULL,
    seq bigint NOT NULL,
    PRIMARY KEY(profile,id),
    UNIQUE(profile,device,seq)
);
CREATE TABLE IF NOT EXISTS learning.tombstones (
    profile text NOT NULL REFERENCES learning.profiles(profile),
    topic text NOT NULL,
    event_id text NOT NULL,
    deleted_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY(profile,topic)
);
CREATE OR REPLACE VIEW learning.messages WITH(security_invoker=true) AS
 SELECT profile,id,topic,session,at,data->>'role' AS role,data->>'text' AS text,data->'attachments' AS attachments,projection_escaped
 FROM learning.events WHERE kind='message';
CREATE OR REPLACE VIEW learning.assessments WITH(security_invoker=true) AS
 SELECT profile,id,topic,session,at,data->>'concept' AS concept,data->>'dimension' AS dimension,
 data->>'level' AS level,data->'evidence' AS evidence,data->>'reason' AS reason,data AS details
 FROM learning.events WHERE kind='assessment';
CREATE OR REPLACE VIEW learning.checkpoints WITH(security_invoker=true) AS
 SELECT profile,id,topic,session,at,data->>'next' AS next,data->'parents' AS parents,data AS details
 FROM learning.events WHERE kind='checkpoint';
CREATE OR REPLACE VIEW learning.checkpoint_heads WITH(security_invoker=true) AS
 SELECT c.* FROM learning.checkpoints c WHERE NOT EXISTS (
 SELECT 1 FROM learning.checkpoints child
 WHERE child.profile=c.profile AND child.topic=c.topic AND child.parents ? c.id
 );
COMMENT ON TABLE learning.events IS 'Immutable canonical teaching events; deletions remove source rows and keep minimal receipts/tombstones.';
COMMENT ON COLUMN learning.events.data IS 'Queryable projection only: NUL is visibly escaped for PostgreSQL JSONB. Original content and hashes always use envelope.';
COMMENT ON TABLE learning.profiles IS 'Cursor allocated while holding this profile row FOR UPDATE; no commit-order holes from concurrent writers.';
