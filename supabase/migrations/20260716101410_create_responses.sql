-- ============================================================
-- Migration : 012_create_responses.sql
-- Project   : ClassPulse360
-- Purpose   : Create Responses table
-- ============================================================

CREATE TABLE IF NOT EXISTS responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id UUID NOT NULL,
    question_id UUID NOT NULL,
    visited BOOLEAN NOT NULL DEFAULT FALSE,
    is_marked_for_review BOOLEAN NOT NULL DEFAULT FALSE,
    selected_answer JSONB,
    is_correct BOOLEAN,
    score_awarded NUMERIC(5,2) NOT NULL DEFAULT 0,
    response_time_ms BIGINT,
    submitted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_responses_participant
        FOREIGN KEY (participant_id)
        REFERENCES participants(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_responses_question
        FOREIGN KEY (question_id)
        REFERENCES questions(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_response
        UNIQUE (participant_id, question_id),

    CONSTRAINT chk_score_awarded
        CHECK (score_awarded >= 0),

    CONSTRAINT chk_response_time
        CHECK (response_time_ms IS NULL OR response_time_ms >= 0)
);