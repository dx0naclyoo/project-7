CREATE TABLE IF NOT EXISTS training_plans (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    level       VARCHAR(20) NOT NULL,
    goal_type   VARCHAR(20),
    days        JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
