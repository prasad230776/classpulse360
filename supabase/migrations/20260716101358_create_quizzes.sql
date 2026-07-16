-- ============================================================
-- Migration : 008_create_quizzes.sql
-- Project   : ClassPulse360
-- Purpose   : Create Quizzes table
-- ============================================================

CREATE TABLE IF NOT EXISTS quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by UUID NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    instructions TEXT,
    visibility visibility_type NOT NULL DEFAULT 'PRIVATE',
    shuffle_questions BOOLEAN NOT NULL DEFAULT FALSE,
    shuffle_options BOOLEAN NOT NULL DEFAULT FALSE,
    allow_answer_change BOOLEAN NOT NULL DEFAULT TRUE,
    show_results_after_each_question BOOLEAN NOT NULL DEFAULT TRUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_quizzes_created_by
        FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_quiz_title
        CHECK (char_length(trim(title)) > 0)
);