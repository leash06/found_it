# Schema Design Decisions

Source of truth: `db/migrations/20261104110000_create_initial_schema.sql`
(applied with dbmate; changed only through migrations).

## Decisions

- **`type`, `category`, `status` are CHECK-constrained `text`, not enums.**
  Changing the allowed values later is a one-line migration instead of a
  type alteration (`ALTER TYPE` is not transactional); sqlc also maps them
  as plain strings.
  Current CHECKs: `type IN ('lost', 'found')`,
  `category IN ('electronics', 'clothing', 'personal_items', 'other')`,
  `status IN ('open', 'returned')`.

- **`users.email` is unique case-insensitively** via
  `CREATE UNIQUE INDEX users_email_lower_key ON users (lower(email))`.
  Application code relies on this index for conflict detection
  (`app/services/users.py` translates the integrity error to HTTP 409).

- **`reports.user_id` is `ON DELETE RESTRICT`** — a report never disappears
  silently because its author was deleted. The delete rules for
  `report_photos` and `claim_audit` are **intentionally undecided** until the
  claim/return workflow exists.

- **`report_photos` uses the composite primary key `(photo_path, report_id)`.**
  A photo path identifies one image within one report; some photos may belong
  to several people's stored copies, so there is no separate id.

- **`claim_audit` is a plain log**: `user_id`, `report_id`, `created_at` —
  one row per claim event, append-only, no status column.

- **`occurred_on` is an optional `date`.** `NULL` means the date is unknown
  (e.g. a found item whose sighting time wasn't recorded).

- **Contact info lives only in `users`.** Public report responses must never
  include e-mails, phone numbers, password hashes, or other credentials.
  If reports ever need a contact channel, it points at `users.id_user`.
