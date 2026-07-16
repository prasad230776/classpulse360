-- ============================================================
-- Migration : 017_create_indexes.sql
-- Project   : ClassPulse360
-- Purpose   : Create Essential Performance Indexes
-- ============================================================

-- Users
CREATE INDEX IF NOT EXISTS idx_users_institution_id
ON users (institution_id);

-- Questions
CREATE INDEX IF NOT EXISTS idx_questions_topic_id
ON questions (topic_id);

-- Sessions
CREATE INDEX IF NOT EXISTS idx_sessions_room_code
ON sessions (room_code);

-- Participants
CREATE INDEX IF NOT EXISTS idx_participants_session_id
ON participants (session_id);

-- Responses
CREATE INDEX IF NOT EXISTS idx_responses_participant_id
ON responses (participant_id);