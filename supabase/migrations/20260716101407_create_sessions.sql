-- ============================================================
-- Migration : 010_create_sessions.sql
-- Project   : ClassPulse360
-- Purpose   : Create Sessions table
-- ============================================================

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL,
    created_by UUID NOT NULL,
    room_code VARCHAR(10) UNIQUE,
    delivery_mode delivery_mode NOT NULL DEFAULT 'INTERACTIVE',
    status session_status NOT NULL DEFAULT 'DRAFT',
    scheduled_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_sessions_quiz
        FOREIGN KEY (quiz_id)
        REFERENCES quizzes(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_sessions_created_by
        FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);