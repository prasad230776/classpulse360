-- ============================================================
-- Migration : 016_create_room_code_trigger.sql
-- Project   : ClassPulse360
-- Purpose   : Auto generate room code trigger
-- ============================================================

CREATE TRIGGER trg_generate_room_code
BEFORE INSERT ON sessions
FOR EACH ROW
EXECUTE FUNCTION fn_generate_room_code();