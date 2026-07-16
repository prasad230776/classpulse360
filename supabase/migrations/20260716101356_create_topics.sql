-- ============================================================
-- Migration : 006_create_topics.sql
-- Project   : ClassPulse360
-- Purpose   : Create Topics table
-- ============================================================

CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_topics_subject
        FOREIGN KEY (subject_id)
        REFERENCES subjects(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_topics_subject_name
        UNIQUE (subject_id, name),

    CONSTRAINT uq_topics_subject_code
        UNIQUE (subject_id, code),

    CONSTRAINT chk_topic_name
        CHECK (char_length(trim(name)) > 0)
);