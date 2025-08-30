-- =====================================================================
-- Session defaults (recommended)
-- =====================================================================
SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- =====================================================================
-- 1) asset_types
-- =====================================================================
CREATE TABLE asset_types (
    asset_type_id   INT AUTO_INCREMENT PRIMARY KEY,
    asset_type_name VARCHAR(255) NOT NULL UNIQUE,
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_asset_type_name (asset_type_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- 2) assets
-- =====================================================================
CREATE TABLE assets (
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
CREATE TABLE llms (
    llm_id          INT AUTO_INCREMENT PRIMARY KEY,
    llm_name        VARCHAR(255) NOT NULL UNIQUE,
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
CREATE TABLE prompts (
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
CREATE TABLE query_type (
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
CREATE TABLE schedules (
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
CREATE TABLE query_schedules (
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

    -- Allow multiple T0 rows that differ by paired_followup_delay_hours,
    -- and prevent duplicates of the same step.
    UNIQUE INDEX ux_schedule_step (schedule_id, query_type_id, delay_hours, paired_followup_delay_hours),

    -- Helpful lookups
    INDEX idx_schedule_id (schedule_id),
    INDEX idx_delay (delay_hours),
    INDEX idx_paired (paired_followup_delay_hours)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- 8) surveys   (simplified: no llm_id; rely on prompts.llm_id)
-- Unique identity: (asset_id, schedule_id, prompt_id)
-- =====================================================================
CREATE TABLE surveys (
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
-- 9) crypto_queries
-- Planner writes one row per planned run (status=PLANNED);
-- Worker updates status/executed_at_utc and stores results/error.
-- =====================================================================
CREATE TABLE crypto_queries (
    query_id            INT AUTO_INCREMENT PRIMARY KEY,
    survey_id           INT NOT NULL,
    schedule_id         INT NOT NULL,
    query_type_id       INT NOT NULL,
    scheduled_for_utc   DATETIME NOT NULL,
    status              ENUM('PLANNED','RUNNING','SUCCEEDED','FAILED','CANCELLED')
                        NOT NULL DEFAULT 'PLANNED',
    executed_at_utc     DATETIME NULL,
    result_json         JSON NULL,
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
    -- Prevent duplicate planning of the same instant/type for a survey
    UNIQUE INDEX ux_cq_plan (survey_id, scheduled_for_utc, query_type_id),
    INDEX idx_cq_scheduled (scheduled_for_utc),
    INDEX idx_cq_status (status),
    INDEX idx_survey_id (survey_id),
    INDEX idx_schedule_id (schedule_id),
    INDEX idx_type_id (query_type_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;









-- ============================================================
-- Seed data for Crypto_Forecasts schema (mock scenario)
-- Scenario:
--   - Survey active and executed on 2025-08-20 and 2025-08-21
--   - Deactivated on 2025-08-22 and remains inactive through Day 8
--   - Snapshot assumed at 2025-08-27 12:00 America/Chicago (17:00 UTC)
-- ============================================================

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
INSERT INTO llms (llm_name, api_url, api_key_secret)
VALUES ('OpenAI GPT-4', 'https://api.openai.example/v1/chat/completions', 'DO_NOT_USE_IN_PROD')
ON DUPLICATE KEY UPDATE api_url = VALUES(api_url);

-- 4) prompts (versioned)
INSERT INTO prompts (llm_id, prompt_text, prompt_version)
SELECT l.llm_id,
    'Given the asset context, provide a baseline market analysis.',
    1
FROM llms l
WHERE l.llm_name = 'OpenAI GPT-4'
ON DUPLICATE KEY UPDATE prompt_text = VALUES(prompt_text);

-- 5) query_type (ensure present; ignore if already inserted)
INSERT IGNORE INTO query_type (query_type_name, description) VALUES
    ('Initial Baseline', 'T0: Initial baseline query at the survey start time'),
    ('Baseline Forecast', 'T0: Baseline forecast query at the survey start time, includes forecast horizon'),
    ('Follow-up', 'T(x): Follow-up query scheduled after T0 by defined delay');

-- 6) schedules (T0 at 01:00 local; America/Chicago)
INSERT INTO schedules (schedule_name, schedule_version, initial_query_time, timezone, description)
VALUES ('Daily-1AM', 1, '01:00:00', 'America/Chicago', 'Baseline at 1AM local (CDT)')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- 7) query_schedules (follow-up steps; plus baseline rows at delay 0)
--    Assumption mapping:
--      'OneHour' = 1h, 'SixHour' = 6h, 'ElevenHour' = 11h,
--      'OneDay' = 24h, 'FiveDay' = 120h, 'TenDay' = 240h
--    Also include two T0 types at 0h: Initial Baseline & Baseline Forecast.
INSERT IGNORE INTO query_schedules (schedule_id, query_type_id, delay_hours)
SELECT s.schedule_id, qt.query_type_id, d.h
FROM schedules s
JOIN (
    SELECT 'Initial Baseline' AS q, 0 AS h UNION ALL
    SELECT 'Baseline Forecast', 0   UNION ALL -- OneHour
    SELECT 'Baseline Forecast', 0   UNION ALL -- SixHour
    SELECT 'Baseline Forecast', 0  UNION ALL -- ElevenHour
    SELECT 'Baseline Forecast', 0  UNION ALL -- OneDay
    SELECT 'Baseline Forecast', 0 UNION ALL -- FiveDay
    SELECT 'Baseline Forecast', 0 UNION ALL -- TenDay
    SELECT 'Follow-up', 1   UNION ALL -- OneHour
    SELECT 'Follow-up', 6   UNION ALL -- SixHour
    SELECT 'Follow-up', 11  UNION ALL -- ElevenHour
    SELECT 'Follow-up', 24  UNION ALL -- OneDay
    SELECT 'Follow-up', 120 UNION ALL -- FiveDay
    SELECT 'Follow-up', 240           -- TenDay
) d
JOIN query_type qt ON qt.query_type_name = d.q
WHERE s.schedule_name = 'Daily-1AM';

-- 8) surveys
-- Create the survey and set it INACTIVE now (since we’re at Day 8 snapshot).
-- It was active on Days 1 & 2, then deactivated on Day 3.
INSERT INTO surveys (asset_id, schedule_id, prompt_id, is_active)
SELECT a.asset_id, s.schedule_id, p.prompt_id, FALSE
FROM assets a
JOIN schedules s ON s.schedule_name = 'Daily-1AM'
JOIN prompts p   ON p.prompt_version = 1
WHERE a.asset_name = 'Bitcoin'
LIMIT 1;

-- Capture IDs for convenience (use variables)
SET @asset_id = (SELECT asset_id FROM assets WHERE asset_name='Bitcoin' LIMIT 1);
SET @schedule_id = (SELECT schedule_id FROM schedules WHERE schedule_name='Daily-1AM' LIMIT 1);
SET @prompt_id = (SELECT prompt_id FROM prompts p JOIN llms l ON l.llm_id=p.llm_id WHERE p.prompt_version=1 AND l.llm_name='OpenAI GPT-4' LIMIT 1);
SET @survey_id = (SELECT survey_id FROM surveys WHERE asset_id=@asset_id AND schedule_id=@schedule_id AND prompt_id=@prompt_id LIMIT 1);

-- Helper: find query_type_ids
SET @qt_baseline = (SELECT query_type_id FROM query_type WHERE query_type_name='Initial Baseline');
SET @qt_base_fore = (SELECT query_type_id FROM query_type WHERE query_type_name='Baseline Forecast');
SET @qt_followup  = (SELECT query_type_id FROM query_type WHERE query_type_name='Follow-up');

-- ============================================================
-- 9) crypto_queries (planned & executed rows for two active days)
-- Days:
--   Day 1 T0 local:  2025-08-20 01:00 America/Chicago = 2025-08-20 06:00:00 UTC
--   Day 2 T0 local:  2025-08-21 01:00 America/Chicago = 2025-08-21 06:00:00 UTC
-- Snapshot time (midday Day 8 local): 2025-08-27 12:00 America/Chicago = 2025-08-27 17:00:00 UTC
-- Status logic:
--   scheduled_for_utc <= '2025-08-27 17:00:00' => SUCCEEDED (one FAILED example)
--   scheduled_for_utc  > '2025-08-27 17:00:00' => PLANNED
-- ============================================================

-- Day 1 base UTC
SET @d1_t0_utc = '2025-08-20 06:00:00';
-- Day 2 base UTC
SET @d2_t0_utc = '2025-08-21 06:00:00';
-- Snapshot UTC (for reference)
SET @snapshot_utc = '2025-08-27 17:00:00';

-- Utility inserts (baseline + forecast at 0h)
INSERT IGNORE INTO crypto_queries
(survey_id, schedule_id, query_type_id, scheduled_for_utc, status, executed_at_utc, result_json, error_text)
VALUES
-- Day 1 (2025-08-20)
(@survey_id, @schedule_id, @qt_baseline,   @d1_t0_utc, 'SUCCEEDED', '2025-08-20 06:01:00',
 JSON_OBJECT('summary','Baseline OK','asset','BTC','score',0.72), NULL),
(@survey_id, @schedule_id, @qt_base_fore,  @d1_t0_utc, 'SUCCEEDED', '2025-08-20 06:02:00',
 JSON_OBJECT('forecast','Short-term up','horizon','T0','price',65000), NULL),

-- Day 2 (2025-08-21)
(@survey_id, @schedule_id, @qt_baseline,   @d2_t0_utc, 'SUCCEEDED', '2025-08-21 06:01:00',
 JSON_OBJECT('summary','Baseline OK','asset','BTC','score',0.70), NULL),
(@survey_id, @schedule_id, @qt_base_fore,  @d2_t0_utc, 'SUCCEEDED', '2025-08-21 06:02:00',
 JSON_OBJECT('forecast','Short-term flat','horizon','T0','price',64850), NULL);

-- Follow-ups for Day 1 (1h, 6h, 11h, 1d, 5d, 10d)
INSERT IGNORE INTO crypto_queries
(survey_id, schedule_id, query_type_id, scheduled_for_utc, status, executed_at_utc, result_json, error_text)
VALUES
-- +1h (OneHour) => 2025-08-20 07:00:00 UTC
(@survey_id, @schedule_id, @qt_followup, TIMESTAMPADD(HOUR,  1, @d1_t0_utc), 'SUCCEEDED', '2025-08-20 07:00:30',
 JSON_OBJECT('delta','small up','h','+1h','price',65120), NULL),
-- +6h (SixHour) => 2025-08-20 12:00:00 UTC
(@survey_id, @schedule_id, @qt_followup, TIMESTAMPADD(HOUR,  6, @d1_t0_utc), 'SUCCEEDED', '2025-08-20 12:01:20',
 JSON_OBJECT('delta','flat','h','+6h','price',65080), NULL),
-- +11h (ElevenHour) => 2025-08-20 17:00:00 UTC
(@survey_id, @schedule_id, @qt_followup, TIMESTAMPADD(HOUR, 11, @d1_t0_utc), 'SUCCEEDED', '2025-08-20 17:00:45',
 JSON_OBJECT('delta','down','h','+11h','price',64890), NULL),
-- +24h (OneDay) => 2025-08-21 06:00:00 UTC
(@survey_id, @schedule_id, @qt_followup, TIMESTAMPADD(HOUR, 24, @d1_t0_utc), 'SUCCEEDED', '2025-08-21 06:00:50',
 JSON_OBJECT('delta','recovering','h','+1d','price',64990), NULL),
-- +120h (FiveDay) => 2025-08-25 06:00:00 UTC  (<= snapshot -> SUCCEEDED)
(@survey_id, @schedule_id, @qt_followup, TIMESTAMPADD(HOUR,120, @d1_t0_utc), 'SUCCEEDED', '2025-08-25 06:01:10',
 JSON_OBJECT('delta','up','h','+5d','price',65550), NULL),
-- +240h (TenDay) => 2025-08-30 06:00:00 UTC  (> snapshot -> PLANNED)
(@survey_id, @schedule_id, @qt_followup, TIMESTAMPADD(HOUR,240, @d1_t0_utc), 'PLANNED', NULL, NULL, NULL);

-- Follow-ups for Day 2 (1h, 6h, 11h, 1d, 5d, 10d)
-- Mark the +11h as FAILED to demonstrate error handling
INSERT IGNORE INTO crypto_queries
(survey_id, schedule_id, query_type_id, scheduled_for_utc, status, executed_at_utc, result_json, error_text)
VALUES
-- +1h (OneHour) => 2025-08-21 07:00:00 UTC
(@survey_id, @schedule_id, @qt_followup, TIMESTAMPADD(HOUR,  1, @d2_t0_utc), 'SUCCEEDED', '2025-08-21 07:00:30',
 JSON_OBJECT('delta','small up','h','+1h','price',64910), NULL),
-- +6h (SixHour) => 2025-08-21 12:00:00 UTC
(@survey_id, @schedule_id, @qt_followup, TIMESTAMPADD(HOUR,  6, @d2_t0_utc), 'SUCCEEDED', '2025-08-21 12:00:50',
 JSON_OBJECT('delta','flat','h','+6h','price',64900), NULL),
-- +11h (ElevenHour) => 2025-08-21 17:00:00 UTC  (FAILED)
(@survey_id, @schedule_id, @qt_followup, TIMESTAMPADD(HOUR, 11, @d2_t0_utc), 'FAILED', '2025-08-21 17:05:10',
 NULL, 'OpenAI API timeout'),
-- +24h (OneDay) => 2025-08-22 06:00:00 UTC
(@survey_id, @schedule_id, @qt_followup, TIMESTAMPADD(HOUR, 24, @d2_t0_utc), 'SUCCEEDED', '2025-08-22 06:01:00',
 JSON_OBJECT('delta','down','h','+1d','price',64620), NULL),
-- +120h (FiveDay) => 2025-08-26 06:00:00 UTC  (<= snapshot -> SUCCEEDED)
(@survey_id, @schedule_id, @qt_followup, TIMESTAMPADD(HOUR,120, @d2_t0_utc), 'SUCCEEDED', '2025-08-26 06:00:40',
 JSON_OBJECT('delta','up','h','+5d','price',65400), NULL),
-- +240h (TenDay) => 2025-08-31 06:00:00 UTC  (> snapshot -> PLANNED)
(@survey_id, @schedule_id, @qt_followup, TIMESTAMPADD(HOUR,240, @d2_t0_utc), 'PLANNED', NULL, NULL, NULL);
