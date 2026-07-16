-- ============================================================
-- Migration : 015_create_room_code_function.sql
-- Project   : ClassPulse360
-- Purpose   : Auto generate unique room code
-- ============================================================

CREATE OR REPLACE FUNCTION fn_generate_room_code()
RETURNS TRIGGER AS $$
DECLARE
    new_code VARCHAR(10);
BEGIN
    IF NEW.room_code IS NULL THEN
        LOOP
            new_code := LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0');

            EXIT WHEN NOT EXISTS (
                SELECT 1
                FROM sessions
                WHERE room_code = new_code
            );
        END LOOP;

        NEW.room_code := new_code;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;