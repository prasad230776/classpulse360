-- ============================================================
-- Migration : 011_create_participants.sql
-- Project   : ClassPulse360
-- Purpose   : Create Participants table
-- ============================================================

CREATE TABLE IF NOT EXISTS participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    user_id UUID NOT NULL,
    status participant_status NOT NULL DEFAULT 'JOINED',
    score NUMERIC(8,2) NOT NULL DEFAULT 0,
    correct_answers INTEGER NOT NULL DEFAULT 0,
    wrong_answers INTEGER NOT NULL DEFAULT 0,
    unanswered_questions INTEGER NOT NULL DEFAULT 0,
    total_time_ms BIGINT NOT NULL DEFAULT 0,
    rank INTEGER,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_participants_session
        FOREIGN KEY (session_id)
        REFERENCES sessions(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_participants_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_participant_session
        UNIQUE (session_id, user_id),

    CONSTRAINT chk_score
        CHECK (score >= 0),

    CONSTRAINT chk_correct_answers
        CHECK (correct_answers >= 0),

    CONSTRAINT chk_wrong_answers
        CHECK (wrong_answers >= 0),

    CONSTRAINT chk_unanswered_questions
        CHECK (unanswered_questions >= 0),

    CONSTRAINT chk_total_time
        CHECK (total_time_ms >= 0)
);