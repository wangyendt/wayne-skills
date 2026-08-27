-- Run once as the database administrator in personal_knowledge.
-- No nested schemas: topic relationships live in rows.
CREATE SCHEMA IF NOT EXISTS learning;
CREATE TABLE IF NOT EXISTS learning.assets (
    asset_id uuid PRIMARY KEY,
    profile text NOT NULL,
    topic_id uuid NOT NULL,
    topic_key text NOT NULL,
    session_id uuid,
    caption text NOT NULL,
    alt_text text NOT NULL,
    provenance jsonb NOT NULL DEFAULT '{}',
    mime_type text NOT NULL CHECK (mime_type IN ('image/png','image/jpeg','image/webp')),
    width integer NOT NULL CHECK (width > 0),
    height integer NOT NULL CHECK (height > 0),
    byte_size bigint NOT NULL CHECK (byte_size BETWEEN 1 AND 26214400),
    sha256 text NOT NULL CHECK (sha256 ~ '^[a-f0-9]{64}$'),
    payload_hash text NOT NULL,
    bucket text NOT NULL,
    oss_key text NOT NULL UNIQUE,
    etag text,
    version_id text,
    state text NOT NULL DEFAULT 'pending' CHECK (state IN ('pending','ready','deleted')),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS assets_topic ON learning.assets(profile, topic_id, created_at, asset_id);
CREATE TABLE IF NOT EXISTS learning.asset_tombstones (
    asset_id uuid PRIMARY KEY,
    profile text NOT NULL,
    deleted_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE learning.assets IS 'Teaching image index. Bytes are private OSS objects; never store credentials or signed URLs here.';
COMMENT ON COLUMN learning.assets.provenance IS 'Generator/tool/model/prompt/source attribution; omit secrets and private host paths.';
