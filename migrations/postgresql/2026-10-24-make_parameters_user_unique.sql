DELETE FROM parameters a
USING parameters b
WHERE a.user_id = b.user_id AND a.id < b.id;

CREATE UNIQUE INDEX IF NOT EXISTS parameters_user_id_key ON parameters (user_id);
