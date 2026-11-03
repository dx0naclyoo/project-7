CREATE TABLE IF NOT EXISTS workouts (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at    TIMESTAMPTZ,
    calories    NUMERIC(7, 2),

    CONSTRAINT workouts_time_check CHECK (ended_at IS NULL OR ended_at >= started_at)
);

-- у пользователя может быть только одна незавершённая тренировка
CREATE UNIQUE INDEX IF NOT EXISTS workouts_one_active_per_user
    ON workouts(user_id) WHERE ended_at IS NULL;
