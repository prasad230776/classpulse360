-- ============================================================
-- Migration : 013_create_question_order_function.sql
-- Project   : ClassPulse360
-- Purpose   : Auto assign question order within a quiz
-- ============================================================

CREATE OR REPLACE FUNCTION fn_set_question_order()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.question_order IS NULL THEN
        SELECT COALESCE(MAX(question_order), 0) + 1
        INTO NEW.question_order
        FROM quiz_questions
        WHERE quiz_id = NEW.quiz_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;