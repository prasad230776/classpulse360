-- ============================================================
-- Migration : 014_create_question_order_trigger.sql
-- Project   : ClassPulse360
-- Purpose   : Trigger for auto assigning question order
-- ============================================================

CREATE TRIGGER trg_set_question_order
BEFORE INSERT ON quiz_questions
FOR EACH ROW
EXECUTE FUNCTION fn_set_question_order();