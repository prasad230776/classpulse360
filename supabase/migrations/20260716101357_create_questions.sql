-- ============================================================
-- Migration : 007_create_questions.sql
-- Project   : ClassPulse360
-- Purpose   : Create Questions table
-- ============================================================

CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID NOT NULL,
    created_by UUID NOT NULL,
    visibility visibility_type NOT NULL DEFAULT 'PRIVATE',
    question_text TEXT NOT NULL,
    question_type question_type NOT NULL DEFAULT 'MCQ_SINGLE',
    options JSONB NOT NULL,
    correct_answer JSONB NOT NULL,
    explanation TEXT,
    difficulty_level difficulty_level NOT NULL DEFAULT 'MEDIUM',
    default_marks NUMERIC(5,2) NOT NULL DEFAULT 1,
    default_time_limit_seconds INTEGER NOT NULL DEFAULT 30,
    tags JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_questions_topic
        FOREIGN KEY (topic_id)
        REFERENCES topics(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_questions_created_by
        FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_default_marks
        CHECK (default_marks > 0),

    CONSTRAINT chk_default_time
        CHECK (default_time_limit_seconds > 0)
);