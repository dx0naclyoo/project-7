  CREATE TABLE IF NOT EXISTS training_settings (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    level       VARCHAR(20) NOT NULL,
    days        SMALLINT[] NOT NULL,

    CONSTRAINT training_settings_days_check CHECK (
        cardinality(days) BETWEEN 1 AND 7
        AND days <@ ARRAY[1, 2, 3, 4, 5, 6, 7]::SMALLINT[]
    )
);

CREATE INDEX IF NOT EXISTS idx_training_settings_user_id
    ON training_settings(user_id);