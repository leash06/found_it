-- migrate:up

CREATE TABLE users (
    id_user uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    email text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Emails are unique regardless of capitalisation.
CREATE UNIQUE INDEX users_email_lower_key ON users (lower(email));

CREATE TABLE reports (
    id_report uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES users (id_user) ON DELETE RESTRICT,
    type text NOT NULL CHECK (type IN ('lost', 'found')),
    description text NOT NULL,
    category text NOT NULL
        CHECK (category IN ('electronics', 'clothing', 'personal_items', 'other')),
    location varchar(255) NOT NULL,
    occurred_on date,
    status text NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'returned')),
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Stores photos associated with reports.
-- Composite primary key: photo_path + report_id.
CREATE TABLE report_photos (
    photo_path text NOT NULL,
    report_id uuid NOT NULL REFERENCES reports (id_report),
    PRIMARY KEY (photo_path, report_id)
);

-- One row per claim event: which user, which report, when.
CREATE TABLE claim_audit (
    id_audit uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES users (id_user),
    report_id uuid NOT NULL REFERENCES reports (id_report),
    created_at timestamptz NOT NULL DEFAULT now()
);

-- migrate:down

DROP TABLE IF EXISTS claim_audit;
DROP TABLE IF EXISTS report_photos;
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS users;
