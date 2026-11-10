-- Пароль пользователя: хэш scrypt в формате "соль$хэш" (hex).
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- Вход по имени, поэтому имя должно быть уникальным
CREATE UNIQUE INDEX IF NOT EXISTS users_username_key ON users (username);

-- Сессии входа: токен живёт SESSION_TTL (settings.py), потом нужен новый вход
CREATE TABLE IF NOT EXISTS sessions (
    token       TEXT PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at  TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS sessions_user_id_idx ON sessions (user_id);
