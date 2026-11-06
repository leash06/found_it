-- name: GetUserById :one
SELECT id_user, name, email, created_at
FROM users
WHERE id_user = $1;

-- name: GetUserByEmail :one
SELECT id_user, name, email, created_at
FROM users
WHERE email = $1;

-- name: CreateUser :one
INSERT INTO users (name, email)
VALUES ($1, $2)
RETURNING id_user, name, email, created_at;

-- name: ListUsers :many
SELECT id_user, name, email, created_at
FROM users
ORDER BY created_at DESC;
