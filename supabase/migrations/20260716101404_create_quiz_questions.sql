-- ============================================================
-- Migration : 009_create_quiz_questions.sql
-- Project   : ClassPulse360
-- Purpose   : Create Quiz Questions table
-- ============================================================

CREATE TABLE IF NOT EXISTS quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL,
    question_id UUID NOT NULL,
    question_order INTEGER,
    marks NUMERIC(5,2),
    negative_marks NUMERIC(5,2),
    time_limit_seconds INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_quiz_questions_quiz
        FOREIGN KEY (quiz_id)
        REFERENCES quizzes(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_quiz_questions_question
        FOREIGN KEY (question_id)
        REFERENCES questions(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_quiz_question
        UNIQUE (quiz_id, question_id),

    CONSTRAINT uq_quiz_question_order
        UNIQUE (quiz_id, question_order),

    CONSTRAINT chk_marks
        CHECK (marks IS NULL OR marks > 0),

    CONSTRAINT chk_negative_marks
        CHECK (negative_marks IS NULL OR negative_marks >= 0),

    CONSTRAINT chk_time_limit
        CHECK (time_limit_seconds IS NULL OR time_limit_seconds > 0)
);