-- ============================================================
-- Migration : 002_create_enums.sql
-- Project   : ClassPulse360
-- Purpose   : Create all application enums
-- ============================================================

---------------------------------------------------------------
-- User Role
---------------------------------------------------------------

CREATE TYPE user_role AS ENUM (
    'SUPER_ADMIN',
    'ADMIN',
    'TEACHER',
    'STUDENT'
);

---------------------------------------------------------------
-- User Status
---------------------------------------------------------------

CREATE TYPE user_status AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED',
    'BLOCKED'
);

---------------------------------------------------------------
-- Institution Type
---------------------------------------------------------------

CREATE TYPE institution_type AS ENUM (
    'COLLEGE',
    'UNIVERSITY',
    'SCHOOL',
    'TRAINING_INSTITUTE',
    'CORPORATE'
);

---------------------------------------------------------------
-- Question Difficulty
---------------------------------------------------------------

CREATE TYPE difficulty_level AS ENUM (
    'EASY',
    'MEDIUM',
    'HARD'
);

---------------------------------------------------------------
-- Question Type
---------------------------------------------------------------

CREATE TYPE question_type AS ENUM (
    'MCQ_SINGLE',
    'MCQ_MULTIPLE',
    'TRUE_FALSE',
    'SHORT_ANSWER',
    'WORD_CLOUD'
);

---------------------------------------------------------------
-- Session Delivery Mode
---------------------------------------------------------------

CREATE TYPE delivery_mode AS ENUM (
    'INTERACTIVE',
    'CLASSROOM_EXAM',
    'SELF_PRACTICE'
);

---------------------------------------------------------------
-- Question Visibility
---------------------------------------------------------------

CREATE TYPE visibility_type AS ENUM (
    'PRIVATE',
    'INSTITUTION',
    'PUBLIC'
);

---------------------------------------------------------------
-- Session Status
---------------------------------------------------------------

CREATE TYPE session_status AS ENUM (
    'DRAFT',
    'WAITING',
    'LIVE',
    'PAUSED',
    'COMPLETED',
    'CANCELLED'
);

---------------------------------------------------------------
-- Participant Status
---------------------------------------------------------------

CREATE TYPE participant_status AS ENUM (
    'JOINED',
    'IN_PROGRESS',
    'SUBMITTED',
    'DISCONNECTED',
    'ABSENT'
);

---------------------------------------------------------------
-- Answer Status
---------------------------------------------------------------

CREATE TYPE answer_status AS ENUM (
    'ANSWERED',
    'SKIPPED',
    'TIMEOUT'
);