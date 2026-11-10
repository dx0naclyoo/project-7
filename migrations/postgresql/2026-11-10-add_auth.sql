-- Пароль пользователя: хэш scrypt в формате "соль$хэш" (hex).
-- У старых пользователей пароля нет, войти они не смогут.
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- Вход по имени, поэтому имя должно быть уникальным.
-- Дубликаты имён не удаляем (пропали бы данные), а переименовываем:
-- самый старый аккаунт сохраняет имя, остальные получают суффикс "_<id>",
-- имя обрезается так, чтобы влезть в 18 символов (UserCreate).
UPDATE users u
SET username = left(u.username, 18 - length('_' || u.id)) || '_' || u.id
WHERE EXISTS (
    SELECT 1 FROM users older
    WHERE older.username = u.username AND older.id < u.id
);

CREATE UNIQUE INDEX IF NOT EXISTS users_username_key ON users (username);

-- Сессии входа: токен живёт SESSION_TTL (settings.py), потом нужен новый вход
CREATE TABLE IF NOT EXISTS sessions (
    token       TEXT PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at  TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS sessions_user_id_idx ON sessions (user_id);
