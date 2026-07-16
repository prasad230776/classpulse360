-- ============================================================
-- Migration : 004_create_users.sql
-- Project   : ClassPulse360
-- Purpose   : Create Users table
-- ============================================================

CREATE TABLE users (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    auth_user_id UUID,

    institution_id UUID,

    role user_role NOT NULL DEFAULT 'STUDENT',

    status user_status NOT NULL DEFAULT 'PENDING',

    name VARCHAR(150) NOT NULL,

    username VARCHAR(30) NOT NULL UNIQUE,

    email VARCHAR(255) NOT NULL UNIQUE,

    mobile_number VARCHAR(20) UNIQUE,

    roll_number VARCHAR(50),

    employee_id VARCHAR(50),

    avatar_url TEXT,

    last_login TIMESTAMPTZ,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_users_institution
        FOREIGN KEY (institution_id)
        REFERENCES institutions(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_username_length
        CHECK (char_length(username) >= 4),

    CONSTRAINT chk_username_format
        CHECK (username ~ '^[A-Za-z0-9._]+$')

);