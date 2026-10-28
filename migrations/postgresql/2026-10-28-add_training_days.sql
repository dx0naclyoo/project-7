ALTER TABLE training_settings
ADD COLUMN IF NOT EXISTS training_days INTEGER[] DEFAULT '{}';