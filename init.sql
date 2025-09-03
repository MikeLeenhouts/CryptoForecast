-- =====================================================================
-- Session defaults (recommended)
-- =====================================================================
SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- =====================================================================
-- 1) asset_types
-- =====================================================================
CREATE TABLE IF NOT EXISTS asset_types (
    asset_type_id   INT AUTO_INCREMENT PRIMARY KEY,
    asset_type_name VARCHAR(255) NOT NULL UNIQUE,
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_asset_type_name (asset_type_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- 2) assets
-- =====================================================================
CREATE TABLE IF NOT EXISTS assets (
    asset_id        INT AUTO_INCREMENT PRIMARY KEY,
    asset_type_id   INT NOT NULL,
    asset_name      VARCHAR(255) NOT NULL UNIQUE,
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_assets_asset_types
        FOREIGN KEY (asset_type_id) REFERENCES asset_types(asset_type_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_asset_type_id (asset_type_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- 3) llms
-- =====================================================================
CREATE TABLE IF NOT EXISTS llms (
    llm_id          INT AUTO_INCREMENT PRIMARY KEY,
    llm_name        VARCHAR(255) NOT NULL UNIQUE,
    llm_model       VARCHAR(255) NOT NULL,
    api_url         VARCHAR(255) NOT NULL,
    api_key_secret  VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_llm_name (llm_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- 4) prompts
-- Notes:
--   T0: Baseline Query (LLM-specific prompt + Asset)
--   T0: Baseline Forecast Query (Baseline + Forecast template + Forecast Time)
--   T(x): Follow-up Query at time x after T0
-- =====================================================================
CREATE TABLE IF NOT EXISTS prompts (
    prompt_id       INT AUTO_INCREMENT PRIMARY KEY,
    llm_id          INT NOT NULL,
    prompt_text     TEXT NOT NULL,
    prompt_version  INT NOT NULL DEFAULT 1,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_prompts_llms
        FOREIGN KEY (llm_id) REFERENCES llms(llm_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    -- prefix index on TEXT required for uniqueness with TEXT in MySQL
    UNIQUE INDEX unique_prompt (llm_id, prompt_text(255), prompt_version),
    INDEX idx_llm_id (llm_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- 5) query_type
-- (Examples: 'Initial Baseline', 'Baseline Forecast', 'Follow-up')
-- =====================================================================
CREATE TABLE IF NOT EXISTS query_type (
    query_type_id   INT AUTO_INCREMENT PRIMARY KEY,
    query_type_name VARCHAR(255) NOT NULL UNIQUE,
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_query_type_name (query_type_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- 6) schedules
-- schedule_id is used to link to query_schedules
-- =====================================================================
CREATE TABLE IF NOT EXISTS schedules (
    schedule_id         INT AUTO_INCREMENT PRIMARY KEY,
    schedule_name       VARCHAR(255) NOT NULL,
    schedule_version    INT NOT NULL DEFAULT 1,
    initial_query_time  TIME NOT NULL,        -- local time-of-day for T0
    timezone            VARCHAR(64) NOT NULL DEFAULT 'UTC', -- IANA TZ (e.g., 'America/Chicago')
    description         TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE INDEX unique_schedule (schedule_name, schedule_version),
    INDEX idx_schedule_name (schedule_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- 7) query_schedules  (revised)
-- One row per query to be executed:
--   - Initial Baseline @ T0:        delay_hours = 0,   paired_followup_delay_hours = NULL
--   - Baseline Forecast @ T0:       delay_hours = 0,   paired_followup_delay_hours = <follow-up delay>
--   - Follow-up @ +d hours:         delay_hours = <d>, paired_followup_delay_hours = NULL
-- =====================================================================
CREATE TABLE IF NOT EXISTS query_schedules (
    query_schedule_id              INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id                    INT NOT NULL,
    query_type_id                  INT NOT NULL,
    delay_hours                    INT NOT NULL,               -- offset from T0 (hours)
    paired_followup_delay_hours    INT NULL,                   -- for T0 Baseline Forecast rows only
    created_at                     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_qs_schedule
        FOREIGN KEY (schedule_id)
        REFERENCES schedules(schedule_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_qs_query_type
        FOREIGN KEY (query_type_id)
        REFERENCES query_type(query_type_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    UNIQUE INDEX ux_schedule_step (schedule_id, query_type_id, delay_hours, paired_followup_delay_hours),

    INDEX idx_schedule_id (schedule_id),
    INDEX idx_delay (delay_hours),
    INDEX idx_paired (paired_followup_delay_hours)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- 8) surveys   (simplified: no llm_id; rely on prompts.llm_id)
-- Unique identity: (asset_id, schedule_id, prompt_id)
-- =====================================================================
CREATE TABLE IF NOT EXISTS surveys (
    survey_id     INT AUTO_INCREMENT PRIMARY KEY,
    asset_id      INT NOT NULL,
    schedule_id   INT NOT NULL,
    prompt_id     INT NOT NULL,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_surveys_assets
        FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_surveys_schedules
        FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_surveys_prompts
        FOREIGN KEY (prompt_id) REFERENCES prompts(prompt_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE INDEX unique_survey (asset_id, schedule_id, prompt_id),
    INDEX idx_asset_id (asset_id),
    INDEX idx_schedule_id (schedule_id),
    INDEX idx_prompt_id (prompt_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- 9) crypto_queries  (revised)
-- Planner writes one row per planned run (status=PLANNED);
-- Worker updates status/executed_at_utc and stores results/error.
-- Baseline Forecast @ T0 uses target_delay_hours to distinguish horizons.
-- =====================================================================
CREATE TABLE IF NOT EXISTS crypto_queries (
    query_id            INT AUTO_INCREMENT PRIMARY KEY,
    survey_id           INT NOT NULL,
    schedule_id         INT NOT NULL,
    query_type_id       INT NOT NULL,
    -- NEW: pairing to the follow-up horizon (NULL for Initial/Follow-up)
    target_delay_hours  INT NULL,

    scheduled_for_utc   DATETIME NOT NULL,
    status              ENUM('PLANNED','RUNNING','SUCCEEDED','FAILED','CANCELLED')
                        NOT NULL DEFAULT 'PLANNED',
    executed_at_utc     DATETIME NULL,
    result_json         JSON NULL,  -- NOTE:  To be enhanced to include the four fields from results from get_asset_recommendation_OpenAI(..) call
    error_text          TEXT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cq_surveys
        FOREIGN KEY (survey_id) REFERENCES surveys(survey_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cq_schedules
        FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cq_query_type
        FOREIGN KEY (query_type_id) REFERENCES query_type(query_type_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    -- UPDATED: include target_delay_hours so multiple BF@T0 rows are allowed
    UNIQUE INDEX ux_cq_plan4 (survey_id, scheduled_for_utc, query_type_id, target_delay_hours),

    INDEX idx_cq_scheduled (scheduled_for_utc),
    INDEX idx_cq_status (status),
    INDEX idx_survey_id (survey_id),
    INDEX idx_schedule_id (schedule_id),
    INDEX idx_type_id (query_type_id),
    INDEX idx_cq_target_delay (target_delay_hours)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;








-- =====================================================================
-- Seed data  (drop-in replacement)
-- Assumptions:
--   - schedules.timezone exists (IANA tz)
--   - crypto_queries has target_delay_hours + updated unique index
--   - This snapshot represents data that exists by T0+10 days after Day 2
-- =====================================================================

SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- 1) asset_types
INSERT INTO asset_types (asset_type_name, description)
VALUES ('Cryptocurrency', 'Digital assets like BTC, ETH')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- 2) assets (Bitcoin)
INSERT INTO assets (asset_type_id, asset_name, description)
SELECT at.asset_type_id, 'Bitcoin', 'BTC'
FROM asset_types at
WHERE at.asset_type_name = 'Cryptocurrency'
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- 3) llms (mock)
INSERT INTO llms (llm_name, llm_model, api_url, api_key_secret)
VALUES ('OpenAI GPT-4', 'gpt-4o-2024-08-06', 'https://api.openai.example/v1/chat/completions', 'DO_NOT_USE_IN_PROD')
ON DUPLICATE KEY UPDATE api_url = VALUES(api_url);

-- 4) prompts (versioned)
INSERT INTO prompts (llm_id, prompt_text, prompt_version)
SELECT l.llm_id,
       'Given the asset context, provide a baseline market analysis.',
       1
FROM llms l
WHERE l.llm_name = 'OpenAI GPT-4'
ON DUPLICATE KEY UPDATE prompt_text = VALUES(prompt_text);

-- 5) query_type
INSERT IGNORE INTO query_type (query_type_name, description) VALUES
    ('Initial Baseline', 'T0: Initial baseline query at the survey start time'),
    ('Baseline Forecast', 'T0: Baseline forecast for each follow-up horizon'),
    ('Follow-up', 'T(x): Follow-up query scheduled after T0 by defined delay');

-- 6) schedules (T0 at 01:00 local; America/Chicago)
INSERT INTO schedules (schedule_name, schedule_version, initial_query_time, timezone, description)
VALUES ('Daily-1AM', 1, '01:00:00', 'America/Chicago', 'Baseline at 1AM local (CDT)')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- 7) query_schedules (paired Baseline Forecast rows at T0)
--    Clear prior steps for this schedule to avoid duplicates.
DELETE qs FROM query_schedules qs
JOIN schedules s ON s.schedule_id = qs.schedule_id
WHERE s.schedule_name = 'Daily-1AM';

--    Initial Baseline @ T0
INSERT IGNORE INTO query_schedules (schedule_id, query_type_id, delay_hours, paired_followup_delay_hours)
SELECT s.schedule_id, qt.query_type_id, 0, NULL
FROM schedules s
JOIN query_type qt ON qt.query_type_name = 'Initial Baseline'
WHERE s.schedule_name = 'Daily-1AM';

--    Baseline Forecast @ T0, one per follow-up target
INSERT IGNORE INTO query_schedules (schedule_id, query_type_id, delay_hours, paired_followup_delay_hours)
SELECT s.schedule_id, qt.query_type_id, 0, d.h
FROM schedules s
JOIN (SELECT 1 h UNION ALL SELECT 6 UNION ALL SELECT 11
      UNION ALL SELECT 24 UNION ALL SELECT 120 UNION ALL SELECT 240) d
JOIN query_type qt ON qt.query_type_name = 'Baseline Forecast'
WHERE s.schedule_name = 'Daily-1AM';

--    Follow-ups at their delays
INSERT IGNORE INTO query_schedules (schedule_id, query_type_id, delay_hours, paired_followup_delay_hours)
SELECT s.schedule_id, qt.query_type_id, d.h, NULL
FROM schedules s
JOIN (SELECT 1 h UNION ALL SELECT 6 UNION ALL SELECT 11
      UNION ALL SELECT 24 UNION ALL SELECT 120 UNION ALL SELECT 240) d
JOIN query_type qt ON qt.query_type_name = 'Follow-up'
WHERE s.schedule_name = 'Daily-1AM';

-- 8) surveys (activate for two days, then could be deactivated later; seed leaves TRUE)
INSERT INTO surveys (asset_id, schedule_id, prompt_id, is_active)
SELECT a.asset_id, s.schedule_id, p.prompt_id, TRUE
FROM assets a
JOIN schedules s ON s.schedule_name = 'Daily-1AM'
JOIN prompts p   ON p.prompt_version = 1
WHERE a.asset_name = 'Bitcoin'
ON DUPLICATE KEY UPDATE is_active = VALUES(is_active);

-- Convenience IDs
SET @asset_id = (SELECT asset_id FROM assets WHERE asset_name='Bitcoin' LIMIT 1);
SET @schedule_id = (SELECT schedule_id FROM schedules WHERE schedule_name='Daily-1AM' LIMIT 1);
SET @prompt_id = (
  SELECT p.prompt_id
  FROM prompts p JOIN llms l ON l.llm_id = p.llm_id
  WHERE p.prompt_version = 1 AND l.llm_name = 'OpenAI GPT-4'
  LIMIT 1
);
SET @survey_id = (
  SELECT survey_id FROM surveys
  WHERE asset_id=@asset_id AND schedule_id=@schedule_id AND prompt_id=@prompt_id
  LIMIT 1
);

-- Helper: type ids
SET @qt_baseline  = (SELECT query_type_id FROM query_type WHERE query_type_name='Initial Baseline');
SET @qt_base_fore = (SELECT query_type_id FROM query_type WHERE query_type_name='Baseline Forecast');
SET @qt_followup  = (SELECT query_type_id FROM query_type WHERE query_type_name='Follow-up');

-- ============================================================
-- 9) crypto_queries (two active days; snapshot at Day2 T0 + 10 days)
--    America/Chicago 01:00 → UTC 06:00 (CDT assumed)
-- ============================================================
SET @d1_t0_utc = '2025-08-20 06:00:00';
SET @d2_t0_utc = '2025-08-21 06:00:00';
SET @snapshot_utc = '2025-08-31 06:00:00';  -- Day2 + 10d

-- Clean out any prior rows for this survey to make seed idempotent
DELETE FROM crypto_queries WHERE survey_id = @survey_id;

-- --------------------------
-- Day 1: Initial Baseline @ T0
-- --------------------------
INSERT INTO crypto_queries
(survey_id, schedule_id, query_type_id, target_delay_hours, scheduled_for_utc, status, executed_at_utc, result_json, error_text)
VALUES
(@survey_id, @schedule_id, @qt_baseline, NULL, @d1_t0_utc, 'SUCCEEDED', DATE_ADD(@d1_t0_utc, INTERVAL 1 MINUTE),
 JSON_OBJECT('summary','Baseline OK','asset','BTC','score',0.72), NULL);

-- Day 1: Baseline Forecast @ T0 (one per follow-up target)
INSERT INTO crypto_queries
(survey_id, schedule_id, query_type_id, target_delay_hours, scheduled_for_utc, status, executed_at_utc, result_json, error_text)
SELECT
  @survey_id, @schedule_id, @qt_base_fore,
  qs.paired_followup_delay_hours AS target_delay_hours,
  @d1_t0_utc AS scheduled_for_utc,
  'SUCCEEDED' AS status,
  DATE_ADD(@d1_t0_utc, INTERVAL 2 MINUTE) AS executed_at_utc,
  JSON_OBJECT('forecast','BF@T0','target_delay_hours', qs.paired_followup_delay_hours),
  NULL
FROM query_schedules qs
WHERE qs.schedule_id = @schedule_id
  AND qs.query_type_id = @qt_base_fore
  AND qs.delay_hours = 0;

-- Day 1: Follow-ups @ +1h, +6h, +11h, +1d, +5d, +10d (all done by snapshot)
INSERT INTO crypto_queries
(survey_id, schedule_id, query_type_id, target_delay_hours, scheduled_for_utc, status, executed_at_utc, result_json, error_text)
VALUES
(@survey_id, @schedule_id, @qt_followup, NULL, DATE_ADD(@d1_t0_utc, INTERVAL   1 HOUR), 'SUCCEEDED', DATE_ADD(@d1_t0_utc, INTERVAL   1 HOUR  + 30 SECOND),
 JSON_OBJECT('h','+1h',  'delta','small up','price',65120), NULL),
(@survey_id, @schedule_id, @qt_followup, NULL, DATE_ADD(@d1_t0_utc, INTERVAL   6 HOUR), 'SUCCEEDED', DATE_ADD(@d1_t0_utc, INTERVAL   6 HOUR  + 50 SECOND),
 JSON_OBJECT('h','+6h',  'delta','flat',    'price',65080), NULL),
(@survey_id, @schedule_id, @qt_followup, NULL, DATE_ADD(@d1_t0_utc, INTERVAL  11 HOUR), 'SUCCEEDED', DATE_ADD(@d1_t0_utc, INTERVAL  11 HOUR  + 45 SECOND),
 JSON_OBJECT('h','+11h', 'delta','down',    'price',64890), NULL),
(@survey_id, @schedule_id, @qt_followup, NULL, DATE_ADD(@d1_t0_utc, INTERVAL  24 HOUR), 'SUCCEEDED', DATE_ADD(@d1_t0_utc, INTERVAL  24 HOUR  + 50 SECOND),
 JSON_OBJECT('h','+1d',  'delta','recover','price',64990), NULL),
(@survey_id, @schedule_id, @qt_followup, NULL, DATE_ADD(@d1_t0_utc, INTERVAL 120 HOUR), 'SUCCEEDED', DATE_ADD(@d1_t0_utc, INTERVAL 120 HOUR + 40 SECOND),
 JSON_OBJECT('h','+5d',  'delta','up',      'price',65550), NULL),
(@survey_id, @schedule_id, @qt_followup, NULL, DATE_ADD(@d1_t0_utc, INTERVAL 240 HOUR), 'SUCCEEDED', DATE_ADD(@d1_t0_utc, INTERVAL 240 HOUR + 40 SECOND),
 JSON_OBJECT('h','+10d', 'delta','steady',  'price',65620), NULL);

-- --------------------------
-- Day 2: Initial Baseline @ T0
-- --------------------------
INSERT INTO crypto_queries
(survey_id, schedule_id, query_type_id, target_delay_hours, scheduled_for_utc, status, executed_at_utc, result_json, error_text)
VALUES
(@survey_id, @schedule_id, @qt_baseline, NULL, @d2_t0_utc, 'SUCCEEDED', DATE_ADD(@d2_t0_utc, INTERVAL 1 MINUTE),
 JSON_OBJECT('summary','Baseline OK','asset','BTC','score',0.70), NULL);

-- Day 2: Baseline Forecast @ T0 (one per follow-up target)
INSERT INTO crypto_queries
(survey_id, schedule_id, query_type_id, target_delay_hours, scheduled_for_utc, status, executed_at_utc, result_json, error_text)
SELECT
  @survey_id, @schedule_id, @qt_base_fore,
  qs.paired_followup_delay_hours AS target_delay_hours,
  @d2_t0_utc AS scheduled_for_utc,
  'SUCCEEDED' AS status,
  DATE_ADD(@d2_t0_utc, INTERVAL 2 MINUTE) AS executed_at_utc,
  JSON_OBJECT('forecast','BF@T0','target_delay_hours', qs.paired_followup_delay_hours),
  NULL
FROM query_schedules qs
WHERE qs.schedule_id = @schedule_id
  AND qs.query_type_id = @qt_base_fore
  AND qs.delay_hours = 0;

-- Day 2: Follow-ups @ +1h, +6h, +11h, +1d, +5d, +10d (all done by snapshot)
INSERT INTO crypto_queries
(survey_id, schedule_id, query_type_id, target_delay_hours, scheduled_for_utc, status, executed_at_utc, result_json, error_text)
VALUES
(@survey_id, @schedule_id, @qt_followup, NULL, DATE_ADD(@d2_t0_utc, INTERVAL   1 HOUR), 'SUCCEEDED', DATE_ADD(@d2_t0_utc, INTERVAL   1 HOUR  + 30 SECOND),
 JSON_OBJECT('h','+1h',  'delta','small up','price',64910), NULL),
(@survey_id, @schedule_id, @qt_followup, NULL, DATE_ADD(@d2_t0_utc, INTERVAL   6 HOUR), 'SUCCEEDED', DATE_ADD(@d2_t0_utc, INTERVAL   6 HOUR  + 50 SECOND),
 JSON_OBJECT('h','+6h',  'delta','flat',    'price',64900), NULL),
(@survey_id, @schedule_id, @qt_followup, NULL, DATE_ADD(@d2_t0_utc, INTERVAL  11 HOUR), 'SUCCEEDED', DATE_ADD(@d2_t0_utc, INTERVAL  11 HOUR  + 45 SECOND),
 JSON_OBJECT('h','+11h', 'delta','down',    'price',64780), NULL),
(@survey_id, @schedule_id, @qt_followup, NULL, DATE_ADD(@d2_t0_utc, INTERVAL  24 HOUR), 'SUCCEEDED', DATE_ADD(@d2_t0_utc, INTERVAL  24 HOUR  + 50 SECOND),
 JSON_OBJECT('h','+1d',  'delta','down',    'price',64620), NULL),
(@survey_id, @schedule_id, @qt_followup, NULL, DATE_ADD(@d2_t0_utc, INTERVAL 120 HOUR), 'SUCCEEDED', DATE_ADD(@d2_t0_utc, INTERVAL 120 HOUR + 40 SECOND),
 JSON_OBJECT('h','+5d',  'delta','up',      'price',65400), NULL),
(@survey_id, @schedule_id, @qt_followup, NULL, DATE_ADD(@d2_t0_utc, INTERVAL 240 HOUR), 'SUCCEEDED', DATE_ADD(@d2_t0_utc, INTERVAL 240 HOUR + 40 SECOND),
 JSON_OBJECT('h','+10d', 'delta','steady',  'price',65510), NULL);

-- =====================================================================
-- Sanity checks (optional; comment out for production)
-- =====================================================================
-- Expected: 13 schedule steps per schedule (1 initial + 6 BF@T0 + 6 follow-ups)
-- SELECT qt.query_type_name, qs.delay_hours, qs.paired_followup_delay_hours
-- FROM query_schedules qs JOIN query_type qt ON qt.query_type_id = qs.query_type_id
-- WHERE qs.schedule_id = @schedule_id
-- ORDER BY qs.delay_hours, qt.query_type_name, qs.paired_followup_delay_hours;

-- Expected: for each T0, 6 BF rows (target_delay_hours in {1,6,11,24,120,240})
-- SELECT scheduled_for_utc, COUNT(*) AS bf_cnt
-- FROM crypto_queries
-- WHERE query_type_id = @qt_base_fore
-- GROUP BY scheduled_for_utc;

-- Expected: all follow-ups up to +10d are SUCCEEDED by @snapshot_utc
-- SELECT query_type_id, scheduled_for_utc, status
-- FROM crypto_queries
-- WHERE scheduled_for_utc <= @snapshot_utc
-- ORDER BY scheduled_for_utc;
