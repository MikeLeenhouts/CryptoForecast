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
    asset_symbol    VARCHAR(64) NOT NULL,
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
-- =====================================================================
CREATE TABLE IF NOT EXISTS prompts (
    prompt_id       INT AUTO_INCREMENT PRIMARY KEY,
    llm_id          INT NOT NULL,
    prompt_name     VARCHAR(255) DEFAULT NULL,
    prompt_text     TEXT NOT NULL,
    followup_llm    INT NOT NULL,
    attribute_1     TEXT,
    attribute_2     TEXT,
    attribute_3     TEXT,
    prompt_version  INT NOT NULL DEFAULT 1,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_prompts_llms
        FOREIGN KEY (llm_id) REFERENCES llms(llm_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_prompts_followup_llms
        FOREIGN KEY (followup_llm) REFERENCES llms(llm_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    -- prefix index on TEXT required for uniqueness with TEXT in MySQL
    UNIQUE INDEX unique_prompt (llm_id, prompt_text(255), prompt_version),
    INDEX idx_llm_id (llm_id),
    INDEX idx_followup_llm_id (followup_llm)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- 5) query_type
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
-- 8) surveys
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
-- 9) queries
-- =====================================================================
CREATE TABLE IF NOT EXISTS queries (
    query_id            INT AUTO_INCREMENT PRIMARY KEY,
    survey_id           INT NOT NULL,
    schedule_id         INT NOT NULL,
    query_schedule_id   INT NOT NULL,  -- New foreign key to query_schedules
    query_type_id       INT NOT NULL,
    paired_query_id     INT NULL,  -- For Baseline Forecast to link to its Follow-up
    scheduled_for_utc   DATETIME NOT NULL,
    status              ENUM('PLANNED','RUNNING','SUCCEEDED','FAILED','CANCELLED') NOT NULL DEFAULT 'PLANNED',
    executed_at_utc     DATETIME NULL,
    result_json         JSON NULL,  -- Stores results from get_asset_recommendation
    recommendation      ENUM('BUY','SELL','HOLD') NULL,
    confidence          DECIMAL(3,2) NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    rationale           TEXT NULL,
    source              TEXT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cq_surveys
        FOREIGN KEY (survey_id)
        REFERENCES surveys(survey_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cq_schedules
        FOREIGN KEY (schedule_id)
        REFERENCES schedules(schedule_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cq_query_schedule
        FOREIGN KEY (query_schedule_id)
        REFERENCES query_schedules(query_schedule_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cq_query_type
        FOREIGN KEY (query_type_id)
        REFERENCES query_type(query_type_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Updated unique constraint to use query_schedule_id
    UNIQUE INDEX ux_cq_plan4 (survey_id, scheduled_for_utc, query_type_id, query_schedule_id),

    INDEX idx_cq_scheduled (scheduled_for_utc),
    INDEX idx_cq_status (status),
    INDEX idx_survey_id (survey_id),
    INDEX idx_schedule_id (schedule_id),
    INDEX idx_type_id (query_type_id),
    INDEX idx_cq_query_schedule (query_schedule_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;







-- =====================================================================
-- Seed data  (drop-in replacement)
-- Assumptions:
--   - schedules.timezone exists (IANA tz)
--   - queries has query_schedule_id + updated unique index
--   - This snapshot represents data that exists by T0+10 days after Day 2
-- =====================================================================

SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- 1) asset_types
INSERT INTO asset_types (asset_type_name, description)
VALUES ('Cryptocurrency', 'Digital assets like BTC, ETH')
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO asset_types (asset_type_name, description)
VALUES ('Equities', 'Stocks, Shares,Ownership in a company')
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO asset_types (asset_type_name, description)
VALUES ('Fixed_Income', 'Bonds, Treasuries, Debt instruments issued by governments, corporations, municipalities')
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO asset_types (asset_type_name, description)
VALUES ('Real Estate', 'Residential, commercial, land, indirect via REITs (Real Estate Investment Trusts')
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO asset_types (asset_type_name, description)
VALUES ('Precious_Metals', 'Commodity (gold, silver, platinum,…)')
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO asset_types (asset_type_name, description)
VALUES ('Energy', 'Commodity(oil, natural gas,…)')
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO asset_types (asset_type_name, description)
VALUES ('Agriculture', 'Commodity (corn, wheat, coffee,…)')
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO asset_types (asset_type_name, description)
VALUES ('Collectibles', 'Art, Luxury Assets, Fine art, rare wines, classic cars, jewelry')
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO asset_types (asset_type_name, description)
VALUES ('Foreign Exchange', 'Trading in global currencies')
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO asset_types (asset_type_name, description)
VALUES ('Derivatives', 'Options, Futures, Swaps,Contracts based on underlying assets (stocks, commodities, interest rates)')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- 2) assets (Bitcoin)
INSERT INTO assets (asset_type_id, asset_name, description, asset_symbol)
SELECT at.asset_type_id, 'Bitcoin', 'BTC', 'BTC-USD'
FROM asset_types at
WHERE at.asset_type_name = 'Cryptocurrency'
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO assets (asset_type_id, asset_name, description, asset_symbol)
SELECT at.asset_type_id, 'Ethereum', 'ETH', 'ETH-USD'
FROM asset_types at
WHERE at.asset_type_name = 'Cryptocurrency'
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO assets (asset_type_id, asset_name, description, asset_symbol)
SELECT at.asset_type_id, 'Gold', 'XAU', 'GC=F'
FROM asset_types at
WHERE at.asset_type_name = 'Precious_Metals'
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- 3) llms (mock)
INSERT INTO llms (llm_name, llm_model, api_url, api_key_secret)
VALUES ('OpenAI', 'gpt-4', 'https://api.openai.com/v1', 'OPENAI_API_KEY')
ON DUPLICATE KEY UPDATE api_url = VALUES(api_url);

INSERT INTO llms (llm_name, llm_model, api_url, api_key_secret)
VALUES ('Anthropic', 'claude-opus-4-1-20250805', 'https://api.anthropic.com/v1/', 'ANTHROPIC_API_KEY')
ON DUPLICATE KEY UPDATE api_url = VALUES(api_url);

INSERT INTO llms (llm_name, llm_model, api_url, api_key_secret)
VALUES ('Grok', 'grok-4-0709', 'https://docs.x.ai/', 'GROK_API_KEY')
ON DUPLICATE KEY UPDATE api_url = VALUES(api_url);

INSERT INTO llms (llm_name, llm_model, api_url, api_key_secret)
VALUES ('Gemini', 'gemini-2.5-pro', 'https://generativelanguage.googleapis.com', 'GEMINI_API_KEY')
ON DUPLICATE KEY UPDATE api_url = VALUES(api_url);

-- 4) prompts (versioned)
INSERT INTO prompts (llm_id, prompt_name, prompt_text, followup_llm, attribute_1, attribute_2, attribute_3, prompt_version)
SELECT l.llm_id, 'OpenAI',
    'Given the asset context, provide a baseline market analysis.', l.llm_id, '', '', '',
    1
FROM llms l
WHERE l.llm_name = 'OpenAI'
ON DUPLICATE KEY UPDATE prompt_text = VALUES(prompt_text);

INSERT INTO prompts (llm_id, prompt_name, prompt_text, followup_llm, attribute_1, attribute_2, attribute_3, prompt_version)
SELECT l.llm_id, 'Anthropic',
    'Given the asset context, provide a baseline market analysis.', l.llm_id, '', '', '',
    1
FROM llms l
WHERE l.llm_name = 'Anthropic'
ON DUPLICATE KEY UPDATE prompt_text = VALUES(prompt_text);

INSERT INTO prompts (llm_id, prompt_name, prompt_text, followup_llm, attribute_1, attribute_2, attribute_3, prompt_version)
SELECT l.llm_id, 'Grok',
    'Given the asset context, provide a baseline market analysis.', l.llm_id, '', '', '',
    1
FROM llms l
WHERE l.llm_name = 'Grok'
ON DUPLICATE KEY UPDATE prompt_text = VALUES(prompt_text);

INSERT INTO prompts (llm_id, prompt_name, prompt_text, followup_llm, attribute_1, attribute_2, attribute_3, prompt_version)
SELECT l.llm_id, 'Gemini',
    'Given the asset context, provide a baseline market analysis.', l.llm_id, '', '', '',
    1
FROM llms l
WHERE l.llm_name = 'Gemini'
ON DUPLICATE KEY UPDATE prompt_text = VALUES(prompt_text);

-- 5) query_type
INSERT IGNORE INTO query_type (query_type_name, description) VALUES
    ('Initial Baseline', 'T0: Initial baseline query at the survey start time'),
    ('Baseline Forecast', 'T0: Baseline forecast query, each paired with a follow-up query'),
    ('Follow-up', 'T(x): Follow-up query scheduled after T0 by defined delay');

-- 6) schedules (T0 at 01:00 local; America/Chicago)
INSERT INTO schedules (schedule_name, schedule_version, initial_query_time, timezone, description)
VALUES ('10-Day_6-Follow-ups', 1, '01:00:00', 'America/Chicago', '10 day survey schedule with 6 follow-up queries')
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO schedules (schedule_name, schedule_version, initial_query_time, timezone, description)
VALUES ('14-Day_7-Follow-ups', 1, '01:00:00', 'America/Chicago', '14 day survey schedule with 7 follow-up queries')
ON DUPLICATE KEY UPDATE description = VALUES(description);


-- 7) query_schedules (paired Baseline Forecast rows at T0)
--    Clear prior steps for this schedule to avoid duplicates.
DELETE qs FROM query_schedules qs
JOIN schedules s ON s.schedule_id = qs.schedule_id
WHERE s.schedule_name = '10-Day_6-Follow-ups';


-- Schedule ID=1, 10-Day_6-Follow-ups query_schedules
--    Initial Baseline @ T0
INSERT IGNORE INTO query_schedules (schedule_id, query_type_id, delay_hours, paired_followup_delay_hours)
SELECT s.schedule_id, qt.query_type_id, 0, NULL
FROM schedules s
JOIN query_type qt ON qt.query_type_name = 'Initial Baseline'
WHERE s.schedule_name = '10-Day_6-Follow-ups';

--    Baseline Forecast @ T0, one per follow-up target
INSERT IGNORE INTO query_schedules (schedule_id, query_type_id, delay_hours, paired_followup_delay_hours)
SELECT s.schedule_id, qt.query_type_id, 0, d.h
FROM schedules s
JOIN (SELECT 1 h UNION ALL SELECT 6 UNION ALL SELECT 11
    UNION ALL SELECT 24 UNION ALL SELECT 120 UNION ALL SELECT 240) d
JOIN query_type qt ON qt.query_type_name = 'Baseline Forecast'
WHERE s.schedule_name = '10-Day_6-Follow-ups';

--    Follow-ups at their delays
INSERT IGNORE INTO query_schedules (schedule_id, query_type_id, delay_hours, paired_followup_delay_hours)
SELECT s.schedule_id, qt.query_type_id, d.h, NULL
FROM schedules s
JOIN (SELECT 1 h UNION ALL SELECT 6 UNION ALL SELECT 11
    UNION ALL SELECT 24 UNION ALL SELECT 120 UNION ALL SELECT 240) d
JOIN query_type qt ON qt.query_type_name = 'Follow-up'
WHERE s.schedule_name = '10-Day_6-Follow-ups';



-- Schedule ID=2, 14-Day_7-Follow-ups query_schedules
--    Initial Baseline @ T0
INSERT IGNORE INTO query_schedules (schedule_id, query_type_id, delay_hours, paired_followup_delay_hours)
SELECT s.schedule_id, qt.query_type_id, 0, NULL
FROM schedules s
JOIN query_type qt ON qt.query_type_name = 'Initial Baseline'
WHERE s.schedule_name = '14-Day_7-Follow-ups';

--    Baseline Forecast @ T0, one per follow-up target
INSERT IGNORE INTO query_schedules (schedule_id, query_type_id, delay_hours, paired_followup_delay_hours)
SELECT s.schedule_id, qt.query_type_id, 0, d.h
FROM schedules s
JOIN (SELECT 1 h UNION ALL SELECT 6 UNION ALL SELECT 11
    UNION ALL SELECT 24 UNION ALL SELECT 120 UNION ALL SELECT 240 UNION ALL SELECT 336) d
JOIN query_type qt ON qt.query_type_name = 'Baseline Forecast'
WHERE s.schedule_name = '14-Day_7-Follow-ups';

--    Follow-ups at their delays
INSERT IGNORE INTO query_schedules (schedule_id, query_type_id, delay_hours, paired_followup_delay_hours)
SELECT s.schedule_id, qt.query_type_id, d.h, NULL
FROM schedules s
JOIN (SELECT 1 h UNION ALL SELECT 6 UNION ALL SELECT 11
    UNION ALL SELECT 24 UNION ALL SELECT 120 UNION ALL SELECT 240 UNION ALL SELECT 336) d
JOIN query_type qt ON qt.query_type_name = 'Follow-up'
WHERE s.schedule_name = '14-Day_7-Follow-ups';


-- 8) surveys (activate for two days, then could be deactivated later; seed leaves TRUE)
INSERT INTO surveys (asset_id, schedule_id, prompt_id, is_active)
SELECT a.asset_id, s.schedule_id, p.prompt_id, TRUE
FROM assets a
JOIN schedules s ON s.schedule_name = '10-Day_6-Follow-ups'
JOIN prompts p   ON p.prompt_version = 1
WHERE a.asset_name = 'Bitcoin'
ON DUPLICATE KEY UPDATE is_active = VALUES(is_active);

INSERT INTO surveys (asset_id, schedule_id, prompt_id, is_active)
SELECT a.asset_id, s.schedule_id, p.prompt_id, TRUE
FROM assets a
JOIN schedules s ON s.schedule_name = '10-Day_6-Follow-ups'
JOIN prompts p   ON p.prompt_version = 1
WHERE a.asset_name = 'Ethereum'
ON DUPLICATE KEY UPDATE is_active = VALUES(is_active);

INSERT INTO surveys (asset_id, schedule_id, prompt_id, is_active)
SELECT a.asset_id, s.schedule_id, p.prompt_id, TRUE
FROM assets a
JOIN schedules s ON s.schedule_name = '14-Day_7-Follow-ups'
JOIN prompts p   ON p.prompt_version = 1
WHERE a.asset_name = 'Gold'
ON DUPLICATE KEY UPDATE is_active = VALUES(is_active);


-- Convenience IDs
SET @asset_id = (SELECT asset_id FROM assets WHERE asset_name='Bitcoin' LIMIT 1);
SET @schedule_id = (SELECT schedule_id FROM schedules WHERE schedule_name='10-Day_6-Follow-ups' LIMIT 1);
SET @prompt_id = (
    SELECT p.prompt_id
    FROM prompts p JOIN llms l ON l.llm_id = p.llm_id
    WHERE p.prompt_version = 1 AND l.llm_name = 'OpenAI'
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
-- 9) queries (two active days; snapshot at Day2 T0 + 10 days)
--    America/Chicago 01:00 → UTC 06:00 (CDT assumed)
-- ============================================================
SET @d1_t0_utc = '2025-08-20 06:00:00';
SET @d2_t0_utc = '2025-08-21 06:00:00';
SET @snapshot_utc = '2025-08-31 06:00:00';  -- Day2 + 10d

-- Clean out any prior rows for this survey to make seed idempotent
DELETE FROM queries WHERE survey_id = @survey_id;

-- --------------------------
-- Day 1: Initial Baseline @ T0
-- --------------------------
INSERT INTO queries
(survey_id, schedule_id, query_schedule_id, query_type_id, scheduled_for_utc, status, executed_at_utc, result_json,recommendation, confidence, rationale, source)
SELECT @survey_id, @schedule_id, qs.query_schedule_id, @qt_baseline, @d1_t0_utc, 'SUCCEEDED', DATE_ADD(@d1_t0_utc, INTERVAL 1 MINUTE),
JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.7, 'rationale', 'Price is stable', 'source', 'model'), 'HOLD', 0.7, 'Price is stable', 'model'
FROM query_schedules qs
WHERE qs.schedule_id = @schedule_id 
  AND qs.query_type_id = @qt_baseline 
  AND qs.delay_hours = 0 
  AND qs.paired_followup_delay_hours IS NULL;

-- Day 1: Baseline Forecast @ T0 (one per follow-up target)
INSERT INTO queries
(survey_id, schedule_id, query_schedule_id, query_type_id, scheduled_for_utc, status, executed_at_utc, result_json, recommendation, confidence, rationale, source)
SELECT @survey_id, @schedule_id, qs.query_schedule_id, @qt_base_fore, @d1_t0_utc, 'SUCCEEDED', DATE_ADD(@d1_t0_utc, INTERVAL 1 MINUTE),
CASE 
    WHEN qs.paired_followup_delay_hours = 1 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.paired_followup_delay_hours = 6 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.7, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.paired_followup_delay_hours = 11 THEN JSON_OBJECT('recommendation', 'SELL', 'confidence', 0.6, 'rationale', 'Price is declining', 'source', 'model')
    WHEN qs.paired_followup_delay_hours = 24 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.paired_followup_delay_hours = 120 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.paired_followup_delay_hours = 240 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
END,
CASE 
    WHEN qs.paired_followup_delay_hours = 1 THEN 'HOLD'
    WHEN qs.paired_followup_delay_hours = 6 THEN 'HOLD'
    WHEN qs.paired_followup_delay_hours = 11 THEN 'SELL'
    WHEN qs.paired_followup_delay_hours = 24 THEN 'HOLD'
    WHEN qs.paired_followup_delay_hours = 120 THEN 'HOLD'
    WHEN qs.paired_followup_delay_hours = 240 THEN 'HOLD'
END,
CASE 
    WHEN qs.paired_followup_delay_hours = 1 THEN 0.8
    WHEN qs.paired_followup_delay_hours = 6 THEN 0.7
    WHEN qs.paired_followup_delay_hours = 11 THEN 0.6
    WHEN qs.paired_followup_delay_hours = 24 THEN 0.8
    WHEN qs.paired_followup_delay_hours = 120 THEN 0.8
    WHEN qs.paired_followup_delay_hours = 240 THEN 0.8
END,
CASE 
    WHEN qs.paired_followup_delay_hours = 11 THEN 'Price is declining'
    ELSE 'Price is stable'
END,
'model'
FROM query_schedules qs
WHERE qs.schedule_id = @schedule_id 
  AND qs.query_type_id = @qt_base_fore 
  AND qs.delay_hours = 0 
  AND qs.paired_followup_delay_hours IS NOT NULL
ORDER BY qs.paired_followup_delay_hours;

-- Day 1: Follow-ups @ +1h, +6h, +11h, +1d, +5d, +10d (all done by snapshot)
INSERT INTO queries
(survey_id, schedule_id, query_schedule_id, query_type_id, scheduled_for_utc, status, executed_at_utc, result_json, recommendation, confidence, rationale, source)
SELECT @survey_id, @schedule_id, qs.query_schedule_id, @qt_followup, 
DATE_ADD(@d1_t0_utc, INTERVAL qs.delay_hours HOUR), 'SUCCEEDED', 
DATE_ADD(DATE_ADD(@d1_t0_utc, INTERVAL qs.delay_hours HOUR), INTERVAL 1 MINUTE),
CASE 
    WHEN qs.delay_hours = 1 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.delay_hours = 6 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.7, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.delay_hours = 11 THEN JSON_OBJECT('recommendation', 'SELL', 'confidence', 0.6, 'rationale', 'Price is declining', 'source', 'model')
    WHEN qs.delay_hours = 24 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.delay_hours = 120 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.delay_hours = 240 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
END,
CASE 
    WHEN qs.delay_hours = 1 THEN 'HOLD'
    WHEN qs.delay_hours = 6 THEN 'HOLD'
    WHEN qs.delay_hours = 11 THEN 'SELL'
    WHEN qs.delay_hours = 24 THEN 'HOLD'
    WHEN qs.delay_hours = 120 THEN 'HOLD'
    WHEN qs.delay_hours = 240 THEN 'HOLD'
END,
CASE 
    WHEN qs.delay_hours = 1 THEN 0.8
    WHEN qs.delay_hours = 6 THEN 0.7
    WHEN qs.delay_hours = 11 THEN 0.6
    WHEN qs.delay_hours = 24 THEN 0.8
    WHEN qs.delay_hours = 120 THEN 0.8
    WHEN qs.delay_hours = 240 THEN 0.8
END,
CASE 
    WHEN qs.delay_hours = 11 THEN 'Price is declining'
    ELSE 'Price is stable'
END,
'model'
FROM query_schedules qs
WHERE qs.schedule_id = @schedule_id 
  AND qs.query_type_id = @qt_followup 
  AND qs.paired_followup_delay_hours IS NULL
ORDER BY qs.delay_hours;

-- --------------------------
-- Day 2: Initial Baseline @ T0
-- --------------------------
INSERT INTO queries
(survey_id, schedule_id, query_schedule_id, query_type_id, scheduled_for_utc, status, executed_at_utc, result_json,recommendation, confidence, rationale, source)
SELECT @survey_id, @schedule_id, qs.query_schedule_id, @qt_baseline, @d2_t0_utc, 'SUCCEEDED', DATE_ADD(@d2_t0_utc, INTERVAL 1 MINUTE),
JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model'), 'HOLD', 0.8, 'Price is stable', 'model'
FROM query_schedules qs
WHERE qs.schedule_id = @schedule_id 
  AND qs.query_type_id = @qt_baseline 
  AND qs.delay_hours = 0 
  AND qs.paired_followup_delay_hours IS NULL;

-- Day 2: Baseline Forecast @ T0 (one per follow-up target)
INSERT INTO queries
(survey_id, schedule_id, query_schedule_id, query_type_id, scheduled_for_utc, status, executed_at_utc, result_json, recommendation, confidence, rationale, source)
SELECT @survey_id, @schedule_id, qs.query_schedule_id, @qt_base_fore, @d2_t0_utc, 'SUCCEEDED', DATE_ADD(@d2_t0_utc, INTERVAL 1 MINUTE),
CASE 
    WHEN qs.paired_followup_delay_hours = 1 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.paired_followup_delay_hours = 6 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.7, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.paired_followup_delay_hours = 11 THEN JSON_OBJECT('recommendation', 'SELL', 'confidence', 0.6, 'rationale', 'Price is declining', 'source', 'model')
    WHEN qs.paired_followup_delay_hours = 24 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.paired_followup_delay_hours = 120 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.paired_followup_delay_hours = 240 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
END,
CASE 
    WHEN qs.paired_followup_delay_hours = 1 THEN 'HOLD'
    WHEN qs.paired_followup_delay_hours = 6 THEN 'HOLD'
    WHEN qs.paired_followup_delay_hours = 11 THEN 'SELL'
    WHEN qs.paired_followup_delay_hours = 24 THEN 'HOLD'
    WHEN qs.paired_followup_delay_hours = 120 THEN 'HOLD'
    WHEN qs.paired_followup_delay_hours = 240 THEN 'HOLD'
END,
CASE 
    WHEN qs.paired_followup_delay_hours = 1 THEN 0.8
    WHEN qs.paired_followup_delay_hours = 6 THEN 0.7
    WHEN qs.paired_followup_delay_hours = 11 THEN 0.6
    WHEN qs.paired_followup_delay_hours = 24 THEN 0.8
    WHEN qs.paired_followup_delay_hours = 120 THEN 0.8
    WHEN qs.paired_followup_delay_hours = 240 THEN 0.8
END,
CASE 
    WHEN qs.paired_followup_delay_hours = 11 THEN 'Price is declining'
    ELSE 'Price is stable'
END,
'model'
FROM query_schedules qs
WHERE qs.schedule_id = @schedule_id 
  AND qs.query_type_id = @qt_base_fore 
  AND qs.delay_hours = 0 
  AND qs.paired_followup_delay_hours IS NOT NULL
ORDER BY qs.paired_followup_delay_hours;


-- Day 2: Follow-ups @ +1h, +6h, +11h, +1d, +5d, +10d (all done by snapshot)
INSERT INTO queries
(survey_id, schedule_id, query_schedule_id, query_type_id, scheduled_for_utc, status, executed_at_utc, result_json, recommendation, confidence, rationale, source)
SELECT @survey_id, @schedule_id, qs.query_schedule_id, @qt_followup, 
DATE_ADD(@d2_t0_utc, INTERVAL qs.delay_hours HOUR), 'SUCCEEDED', 
DATE_ADD(DATE_ADD(@d2_t0_utc, INTERVAL qs.delay_hours HOUR), INTERVAL 1 MINUTE),
CASE 
    WHEN qs.delay_hours = 1 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.delay_hours = 6 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.7, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.delay_hours = 11 THEN JSON_OBJECT('recommendation', 'SELL', 'confidence', 0.6, 'rationale', 'Price is declining', 'source', 'model')
    WHEN qs.delay_hours = 24 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.delay_hours = 120 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
    WHEN qs.delay_hours = 240 THEN JSON_OBJECT('recommendation', 'HOLD', 'confidence', 0.8, 'rationale', 'Price is stable', 'source', 'model')
END,
CASE 
    WHEN qs.delay_hours = 1 THEN 'HOLD'
    WHEN qs.delay_hours = 6 THEN 'HOLD'
    WHEN qs.delay_hours = 11 THEN 'SELL'
    WHEN qs.delay_hours = 24 THEN 'HOLD'
    WHEN qs.delay_hours = 120 THEN 'HOLD'
    WHEN qs.delay_hours = 240 THEN 'HOLD'
END,
CASE 
    WHEN qs.delay_hours = 1 THEN 0.8
    WHEN qs.delay_hours = 6 THEN 0.7
    WHEN qs.delay_hours = 11 THEN 0.6
    WHEN qs.delay_hours = 24 THEN 0.8
    WHEN qs.delay_hours = 120 THEN 0.8
    WHEN qs.delay_hours = 240 THEN 0.8
END,
CASE 
    WHEN qs.delay_hours = 11 THEN 'Price is declining'
    ELSE 'Price is stable'
END,
'model'
FROM query_schedules qs
WHERE qs.schedule_id = @schedule_id 
  AND qs.query_type_id = @qt_followup 
  AND qs.paired_followup_delay_hours IS NULL
ORDER BY qs.delay_hours;




-- =====================================================================
-- Mock Data for queries Table (All 12 Surveys, 30 Days)
-- Drop-in replacement for generate_all_surveys_mock_queries.sql
-- Generates mock queries for all surveys, covering Initial Baseline, Baseline Forecast, and Follow-up queries
-- Covers 30 days (2025-11-01 to 2025-11-30)
-- Custom recommendation rules per survey ID, random confidence, generated rationale and source
-- Avoids modifying existing data (e.g., Bitcoin survey on 2025-08-20/21)
-- Fixes Error 1137 by using LEFT JOIN instead of multiple subqueries
-- Updated to include paired_query_id for Baseline Forecast and Follow-up queries
-- =====================================================================

SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- Helper: Query type IDs
SET @qt_baseline = (SELECT query_type_id FROM query_type WHERE query_type_name = 'Initial Baseline');
SET @qt_base_fore = (SELECT query_type_id FROM query_type WHERE query_type_name = 'Baseline Forecast');
SET @qt_followup = (SELECT query_type_id FROM query_type WHERE query_type_name = 'Follow-up');

-- Temporary table to store Initial Baseline predictions for accuracy-based follow-ups
DROP TEMPORARY TABLE IF EXISTS temp_initial_predictions;
CREATE TEMPORARY TABLE temp_initial_predictions (
    survey_id INT,
    day_offset INT,
    delay_hours INT,
    recommendation VARCHAR(50),
    PRIMARY KEY (survey_id, day_offset, delay_hours)
);

-- Temporary table to store Baseline Forecast query IDs for paired_query_id linking
DROP TEMPORARY TABLE IF EXISTS temp_base_forecast_queries;
CREATE TEMPORARY TABLE temp_base_forecast_queries (
    survey_id INT,
    day_offset INT,
    paired_followup_delay_hours INT,
    query_id INT,
    scheduled_for_utc DATETIME,
    PRIMARY KEY (survey_id, day_offset, paired_followup_delay_hours)
);

-- Stored procedure to generate mock queries
DELIMITER $$

DROP PROCEDURE IF EXISTS generate_all_surveys_mock_queries $$
CREATE PROCEDURE generate_all_surveys_mock_queries()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_survey_id INT;
    DECLARE v_schedule_id INT;
    DECLARE v_followup_count INT;
    DECLARE v_day_offset INT;
    DECLARE v_base_time DATETIME;

    -- Cursor for all surveys
    DECLARE survey_cursor CURSOR FOR
        SELECT survey_id, schedule_id
        FROM surveys
        WHERE is_active = TRUE
        AND survey_id IN (1, 2, 3, 4, 8, 9, 10, 11, 15, 16, 17, 18);

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN survey_cursor;

    read_loop: LOOP
        FETCH survey_cursor INTO v_survey_id, v_schedule_id;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Determine number of follow-ups based on schedule
        SET v_followup_count = (
            SELECT COUNT(*) 
            FROM query_schedules qs 
            JOIN query_type qt ON qs.query_type_id = qt.query_type_id
            WHERE qs.schedule_id = v_schedule_id 
            AND qt.query_type_name = 'Follow-up'
        );

        -- Loop over 30 days (2025-11-01 to 2025-11-30)
        SET v_day_offset = 0;
        WHILE v_day_offset <= 29 DO
            SET v_base_time = DATE_ADD('2025-11-01 06:00:00', INTERVAL v_day_offset DAY);

            -- Store Initial Baseline predictions for accuracy-based follow-ups
            INSERT INTO temp_initial_predictions (survey_id, day_offset, delay_hours, recommendation)
            SELECT 
                v_survey_id, 
                v_day_offset, 
                qs.paired_followup_delay_hours,
                ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
            FROM query_schedules qs
            WHERE qs.schedule_id = v_schedule_id
            AND qs.query_type_id = @qt_base_fore
            AND qs.delay_hours = 0
            AND qs.paired_followup_delay_hours IS NOT NULL;

            -- Insert Initial Baseline Query @ T0
            INSERT IGNORE INTO queries (
                survey_id, schedule_id, query_schedule_id, query_type_id, 
                paired_query_id, scheduled_for_utc, status, executed_at_utc, 
                result_json, recommendation, confidence, rationale, source
            )
            SELECT 
                v_survey_id, 
                v_schedule_id, 
                qs.query_schedule_id, 
                @qt_baseline, 
                NULL,  -- No paired query for Initial Baseline
                v_base_time, 
                'SUCCEEDED', 
                DATE_ADD(v_base_time, INTERVAL 1 MINUTE),
                JSON_OBJECT(
                    'recommendation', ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD'),
                    'confidence', ROUND(0.60 + RAND() * 0.35, 2),
                    'rationale', CASE 
                        WHEN ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD') = 'BUY' THEN 'Bullish trend detected'
                        WHEN ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD') = 'SELL' THEN 'Bearish market signals'
                        ELSE 'Stable market conditions'
                    END,
                    'source', ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
                ),
                ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD'),
                ROUND(0.60 + RAND() * 0.35, 2),
                CASE 
                    WHEN ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD') = 'BUY' THEN 'Bullish trend detected'
                    WHEN ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD') = 'SELL' THEN 'Bearish market signals'
                    ELSE 'Stable market conditions'
                END,
                ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
            FROM query_schedules qs
            WHERE qs.schedule_id = v_schedule_id
            AND qs.query_type_id = @qt_baseline
            AND qs.delay_hours = 0
            AND qs.paired_followup_delay_hours IS NULL;

            -- Insert Baseline Forecast Queries @ T0 (one per follow-up)
            INSERT IGNORE INTO queries (
                survey_id, schedule_id, query_schedule_id, query_type_id, 
                paired_query_id, scheduled_for_utc, status, executed_at_utc, 
                result_json, recommendation, confidence, rationale, source
            )
            SELECT 
                v_survey_id, 
                v_schedule_id, 
                qs.query_schedule_id, 
                @qt_base_fore, 
                NULL,  -- paired_query_id set later via UPDATE
                v_base_time, 
                'SUCCEEDED', 
                DATE_ADD(v_base_time, INTERVAL 1 MINUTE),
                JSON_ARRAY(
                    JSON_OBJECT(
                        'delay_hour', qs.paired_followup_delay_hours,
                        'recommendation', ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD'),
                        'confidence', ROUND(0.60 + RAND() * 0.35, 2),
                        'rationale', CASE 
                            WHEN ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD') = 'BUY' THEN 'Predicted bullish trend'
                            WHEN ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD') = 'SELL' THEN 'Predicted bearish signals'
                            ELSE 'Predicted stable conditions'
                        END,
                        'source', ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
                    )
                ),
                ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD'),
                ROUND(0.60 + RAND() * 0.35, 2),
                CASE 
                    WHEN ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD') = 'BUY' THEN 'Predicted bullish trend'
                    WHEN ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD') = 'SELL' THEN 'Predicted bearish signals'
                    ELSE 'Predicted stable conditions'
                END,
                ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
            FROM query_schedules qs
            WHERE qs.schedule_id = v_schedule_id
            AND qs.query_type_id = @qt_base_fore
            AND qs.delay_hours = 0
            AND qs.paired_followup_delay_hours IS NOT NULL
            ORDER BY qs.paired_followup_delay_hours;

            -- Store Baseline Forecast query IDs for linking
            INSERT INTO temp_base_forecast_queries (survey_id, day_offset, paired_followup_delay_hours, query_id, scheduled_for_utc)
            SELECT 
                v_survey_id, 
                v_day_offset, 
                qs.paired_followup_delay_hours, 
                LAST_INSERT_ID() + ROW_NUMBER() OVER (PARTITION BY v_survey_id, v_day_offset ORDER BY qs.paired_followup_delay_hours) - 1,
                v_base_time
            FROM query_schedules qs
            WHERE qs.schedule_id = v_schedule_id
            AND qs.query_type_id = @qt_base_fore
            AND qs.delay_hours = 0
            AND qs.paired_followup_delay_hours IS NOT NULL
            ORDER BY qs.paired_followup_delay_hours;

            -- Insert Follow-up Queries for Surveys 1, 2, 4, 18 (Random)
            INSERT IGNORE INTO queries (
                survey_id, schedule_id, query_schedule_id, query_type_id, 
                paired_query_id, scheduled_for_utc, status, executed_at_utc, 
                result_json, recommendation, confidence, rationale, source
            )
            SELECT 
                v_survey_id, 
                v_schedule_id, 
                qs.query_schedule_id, 
                @qt_followup, 
                (SELECT query_id FROM temp_base_forecast_queries tbf 
                 WHERE tbf.survey_id = v_survey_id 
                 AND tbf.day_offset = v_day_offset 
                 AND tbf.paired_followup_delay_hours = qs.delay_hours),  -- Link to Baseline Forecast
                DATE_ADD(v_base_time, INTERVAL qs.delay_hours HOUR), 
                'SUCCEEDED', 
                DATE_ADD(DATE_ADD(v_base_time, INTERVAL qs.delay_hours HOUR), INTERVAL 1 MINUTE),
                JSON_OBJECT(
                    'recommendation', ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD'),
                    'confidence', ROUND(0.60 + RAND() * 0.35, 2),
                    'rationale', CASE 
                        WHEN ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD') = 'BUY' THEN 'Bullish trend detected'
                        WHEN ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD') = 'SELL' THEN 'Bearish market signals'
                        ELSE 'Stable market conditions'
                    END,
                    'source', ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
                ),
                ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD'),
                ROUND(0.60 + RAND() * 0.35, 2),
                CASE 
                    WHEN ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD') = 'BUY' THEN 'Bullish trend detected'
                    WHEN ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD') = 'SELL' THEN 'Bearish market signals'
                    ELSE 'Stable market conditions'
                END,
                ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
            FROM query_schedules qs
            WHERE qs.schedule_id = v_schedule_id
            AND qs.query_type_id = @qt_followup
            AND qs.paired_followup_delay_hours IS NULL
            AND v_survey_id IN (1, 2, 4, 18)
            ORDER BY qs.delay_hours;

            -- Insert Follow-up Queries for Survey 3 (Day 1: Random, Day 2+: 75% accurate)
            INSERT IGNORE INTO queries (
                survey_id, schedule_id, query_schedule_id, query_type_id, 
                paired_query_id, scheduled_for_utc, status, executed_at_utc, 
                result_json, recommendation, confidence, rationale, source
            )
            SELECT 
                v_survey_id, 
                v_schedule_id, 
                qs.query_schedule_id, 
                @qt_followup, 
                (SELECT query_id FROM temp_base_forecast_queries tbf 
                 WHERE tbf.survey_id = v_survey_id 
                 AND tbf.day_offset = v_day_offset 
                 AND tbf.paired_followup_delay_hours = qs.delay_hours),  -- Link to Baseline Forecast
                DATE_ADD(v_base_time, INTERVAL qs.delay_hours HOUR), 
                'SUCCEEDED', 
                DATE_ADD(DATE_ADD(v_base_time, INTERVAL qs.delay_hours HOUR), INTERVAL 1 MINUTE),
                JSON_OBJECT(
                    'recommendation', COALESCE(
                        CASE WHEN v_day_offset > 0 AND RAND() < 0.75 THEN tip.recommendation END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ),
                    'confidence', ROUND(0.60 + RAND() * 0.35, 2),
                    'rationale', CASE 
                        WHEN COALESCE(
                            CASE WHEN v_day_offset > 0 AND RAND() < 0.75 THEN tip.recommendation END,
                            ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                        ) = 'BUY' THEN 'Bullish trend detected'
                        WHEN COALESCE(
                            CASE WHEN v_day_offset > 0 AND RAND() < 0.75 THEN tip.recommendation END,
                            ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                        ) = 'SELL' THEN 'Bearish market signals'
                        ELSE 'Stable market conditions'
                    END,
                    'source', ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
                ),
                COALESCE(
                    CASE WHEN v_day_offset > 0 AND RAND() < 0.75 THEN tip.recommendation END,
                    ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                ),
                ROUND(0.60 + RAND() * 0.35, 2),
                CASE 
                    WHEN COALESCE(
                        CASE WHEN v_day_offset > 0 AND RAND() < 0.75 THEN tip.recommendation END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ) = 'BUY' THEN 'Bullish trend detected'
                    WHEN COALESCE(
                        CASE WHEN v_day_offset > 0 AND RAND() < 0.75 THEN tip.recommendation END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ) = 'SELL' THEN 'Bearish market signals'
                    ELSE 'Stable market conditions'
                END,
                ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
            FROM query_schedules qs
            LEFT JOIN temp_initial_predictions tip 
                ON tip.survey_id = v_survey_id 
                AND tip.day_offset = v_day_offset 
                AND tip.delay_hours = qs.delay_hours
            WHERE qs.schedule_id = v_schedule_id
            AND qs.query_type_id = @qt_followup
            AND qs.paired_followup_delay_hours IS NULL
            AND v_survey_id = 3
            ORDER BY qs.delay_hours;

            -- Insert Follow-up Queries for Surveys 8, 9, 10 (Day 1: Weighted BUY, Day 2+: 75% accurate)
            INSERT IGNORE INTO queries (
                survey_id, schedule_id, query_schedule_id, query_type_id, 
                paired_query_id, scheduled_for_utc, status, executed_at_utc, 
                result_json, recommendation, confidence, rationale, source
            )
            SELECT 
                v_survey_id, 
                v_schedule_id, 
                qs.query_schedule_id, 
                @qt_followup, 
                (SELECT query_id FROM temp_base_forecast_queries tbf 
                 WHERE tbf.survey_id = v_survey_id 
                 AND tbf.day_offset = v_day_offset 
                 AND tbf.paired_followup_delay_hours = qs.delay_hours),  -- Link to Baseline Forecast
                DATE_ADD(v_base_time, INTERVAL qs.delay_hours HOUR), 
                'SUCCEEDED', 
                DATE_ADD(DATE_ADD(v_base_time, INTERVAL qs.delay_hours HOUR), INTERVAL 1 MINUTE),
                JSON_OBJECT(
                    'recommendation', COALESCE(
                        CASE WHEN v_day_offset = 0 AND v_survey_id IN (8, 9) AND RAND() < 0.6 THEN 'BUY' 
                             WHEN v_day_offset = 0 AND v_survey_id = 10 AND RAND() < 0.8 THEN 'BUY'
                             WHEN v_day_offset > 0 AND RAND() < 0.75 THEN tip.recommendation 
                             WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'SELL', 'HOLD') END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ),
                    'confidence', ROUND(0.60 + RAND() * 0.35, 2),
                    'rationale', CASE 
                        WHEN COALESCE(
                            CASE WHEN v_day_offset = 0 AND v_survey_id IN (8, 9) AND RAND() < 0.6 THEN 'BUY' 
                                 WHEN v_day_offset = 0 AND v_survey_id = 10 AND RAND() < 0.8 THEN 'BUY'
                                 WHEN v_day_offset > 0 AND RAND() < 0.75 THEN tip.recommendation 
                                 WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'SELL', 'HOLD') END,
                            ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                        ) = 'BUY' THEN 'Bullish trend detected'
                        WHEN COALESCE(
                            CASE WHEN v_day_offset = 0 AND v_survey_id IN (8, 9) AND RAND() < 0.6 THEN 'BUY' 
                                 WHEN v_day_offset = 0 AND v_survey_id = 10 AND RAND() < 0.8 THEN 'BUY'
                                 WHEN v_day_offset > 0 AND RAND() < 0.75 THEN tip.recommendation 
                                 WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'SELL', 'HOLD') END,
                            ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                        ) = 'SELL' THEN 'Bearish market signals'
                        ELSE 'Stable market conditions'
                    END,
                    'source', ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
                ),
                COALESCE(
                    CASE WHEN v_day_offset = 0 AND v_survey_id IN (8, 9) AND RAND() < 0.6 THEN 'BUY' 
                         WHEN v_day_offset = 0 AND v_survey_id = 10 AND RAND() < 0.8 THEN 'BUY'
                         WHEN v_day_offset > 0 AND RAND() < 0.75 THEN tip.recommendation 
                         WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'SELL', 'HOLD') END,
                    ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                ),
                ROUND(0.60 + RAND() * 0.35, 2),
                CASE 
                    WHEN COALESCE(
                        CASE WHEN v_day_offset = 0 AND v_survey_id IN (8, 9) AND RAND() < 0.6 THEN 'BUY' 
                             WHEN v_day_offset = 0 AND v_survey_id = 10 AND RAND() < 0.8 THEN 'BUY'
                             WHEN v_day_offset > 0 AND RAND() < 0.75 THEN tip.recommendation 
                             WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'SELL', 'HOLD') END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ) = 'BUY' THEN 'Bullish trend detected'
                    WHEN COALESCE(
                        CASE WHEN v_day_offset = 0 AND v_survey_id IN (8, 9) AND RAND() < 0.6 THEN 'BUY' 
                             WHEN v_day_offset = 0 AND v_survey_id = 10 AND RAND() < 0.8 THEN 'BUY'
                             WHEN v_day_offset > 0 AND RAND() < 0.75 THEN tip.recommendation 
                             WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'SELL', 'HOLD') END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ) = 'SELL' THEN 'Bearish market signals'
                    ELSE 'Stable market conditions'
                END,
                ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
            FROM query_schedules qs
            LEFT JOIN temp_initial_predictions tip 
                ON tip.survey_id = v_survey_id 
                AND tip.day_offset = v_day_offset 
                AND tip.delay_hours = qs.delay_hours
            WHERE qs.schedule_id = v_schedule_id
            AND qs.query_type_id = @qt_followup
            AND qs.paired_followup_delay_hours IS NULL
            AND v_survey_id IN (8, 9, 10)
            ORDER BY qs.delay_hours;

            -- Insert Follow-up Queries for Survey 11 (Day 1: 40% BUY, Day 2+: 50% accurate)
            INSERT IGNORE INTO queries (
                survey_id, schedule_id, query_schedule_id, query_type_id, 
                paired_query_id, scheduled_for_utc, status, executed_at_utc, 
                result_json, recommendation, confidence, rationale, source
            )
            SELECT 
                v_survey_id, 
                v_schedule_id, 
                qs.query_schedule_id, 
                @qt_followup, 
                (SELECT query_id FROM temp_base_forecast_queries tbf 
                 WHERE tbf.survey_id = v_survey_id 
                 AND tbf.day_offset = v_day_offset 
                 AND tbf.paired_followup_delay_hours = qs.delay_hours),  -- Link to Baseline Forecast
                DATE_ADD(v_base_time, INTERVAL qs.delay_hours HOUR), 
                'SUCCEEDED', 
                DATE_ADD(DATE_ADD(v_base_time, INTERVAL qs.delay_hours HOUR), INTERVAL 1 MINUTE),
                JSON_OBJECT(
                    'recommendation', COALESCE(
                        CASE WHEN v_day_offset = 0 AND RAND() < 0.4 THEN 'BUY' 
                             WHEN v_day_offset > 0 AND RAND() < 0.5 THEN tip.recommendation 
                             WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'SELL', 'HOLD') END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ),
                    'confidence', ROUND(0.60 + RAND() * 0.35, 2),
                    'rationale', CASE 
                        WHEN COALESCE(
                            CASE WHEN v_day_offset = 0 AND RAND() < 0.4 THEN 'BUY' 
                                 WHEN v_day_offset > 0 AND RAND() < 0.5 THEN tip.recommendation 
                                 WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'SELL', 'HOLD') END,
                            ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                        ) = 'BUY' THEN 'Bullish trend detected'
                        WHEN COALESCE(
                            CASE WHEN v_day_offset = 0 AND RAND() < 0.4 THEN 'BUY' 
                                 WHEN v_day_offset > 0 AND RAND() < 0.5 THEN tip.recommendation 
                                 WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'SELL', 'HOLD') END,
                            ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                        ) = 'SELL' THEN 'Bearish market signals'
                        ELSE 'Stable market conditions'
                    END,
                    'source', ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
                ),
                COALESCE(
                    CASE WHEN v_day_offset = 0 AND RAND() < 0.4 THEN 'BUY' 
                         WHEN v_day_offset > 0 AND RAND() < 0.5 THEN tip.recommendation 
                         WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'SELL', 'HOLD') END,
                    ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                ),
                ROUND(0.60 + RAND() * 0.35, 2),
                CASE 
                    WHEN COALESCE(
                        CASE WHEN v_day_offset = 0 AND RAND() < 0.4 THEN 'BUY' 
                             WHEN v_day_offset > 0 AND RAND() < 0.5 THEN tip.recommendation 
                             WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'SELL', 'HOLD') END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ) = 'BUY' THEN 'Bullish trend detected'
                    WHEN COALESCE(
                        CASE WHEN v_day_offset = 0 AND RAND() < 0.4 THEN 'BUY' 
                             WHEN v_day_offset > 0 AND RAND() < 0.5 THEN tip.recommendation 
                             WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'SELL', 'HOLD') END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ) = 'SELL' THEN 'Bearish market signals'
                    ELSE 'Stable market conditions'
                END,
                ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
            FROM query_schedules qs
            LEFT JOIN temp_initial_predictions tip 
                ON tip.survey_id = v_survey_id 
                AND tip.day_offset = v_day_offset 
                AND tip.delay_hours = qs.delay_hours
            WHERE qs.schedule_id = v_schedule_id
            AND qs.query_type_id = @qt_followup
            AND qs.paired_followup_delay_hours IS NULL
            AND v_survey_id = 11
            ORDER BY qs.delay_hours;

            -- Insert Follow-up Queries for Surveys 15, 16 (Day 1: 90% HOLD, Day 2+: 90% accurate)
            INSERT IGNORE INTO queries (
                survey_id, schedule_id, query_schedule_id, query_type_id, 
                paired_query_id, scheduled_for_utc, status, executed_at_utc, 
                result_json, recommendation, confidence, rationale, source
            )
            SELECT 
                v_survey_id, 
                v_schedule_id, 
                qs.query_schedule_id, 
                @qt_followup, 
                (SELECT query_id FROM temp_base_forecast_queries tbf 
                 WHERE tbf.survey_id = v_survey_id 
                 AND tbf.day_offset = v_day_offset 
                 AND tbf.paired_followup_delay_hours = qs.delay_hours),  -- Link to Baseline Forecast
                DATE_ADD(v_base_time, INTERVAL qs.delay_hours HOUR), 
                'SUCCEEDED', 
                DATE_ADD(DATE_ADD(v_base_time, INTERVAL qs.delay_hours HOUR), INTERVAL 1 MINUTE),
                JSON_OBJECT(
                    'recommendation', COALESCE(
                        CASE WHEN v_day_offset = 0 AND RAND() < 0.9 THEN 'HOLD' 
                             WHEN v_day_offset > 0 AND RAND() < 0.9 THEN tip.recommendation 
                             WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'BUY', 'SELL') END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ),
                    'confidence', ROUND(0.60 + RAND() * 0.35, 2),
                    'rationale', CASE 
                        WHEN COALESCE(
                            CASE WHEN v_day_offset = 0 AND RAND() < 0.9 THEN 'HOLD' 
                                 WHEN v_day_offset > 0 AND RAND() < 0.9 THEN tip.recommendation 
                                 WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'BUY', 'SELL') END,
                            ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                        ) = 'BUY' THEN 'Bullish trend detected'
                        WHEN COALESCE(
                            CASE WHEN v_day_offset = 0 AND RAND() < 0.9 THEN 'HOLD' 
                                 WHEN v_day_offset > 0 AND RAND() < 0.9 THEN tip.recommendation 
                                 WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'BUY', 'SELL') END,
                            ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                        ) = 'SELL' THEN 'Bearish market signals'
                        ELSE 'Stable market conditions'
                    END,
                    'source', ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
                ),
                COALESCE(
                    CASE WHEN v_day_offset = 0 AND RAND() < 0.9 THEN 'HOLD' 
                         WHEN v_day_offset > 0 AND RAND() < 0.9 THEN tip.recommendation 
                         WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'BUY', 'SELL') END,
                    ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                ),
                ROUND(0.60 + RAND() * 0.35, 2),
                CASE 
                    WHEN COALESCE(
                        CASE WHEN v_day_offset = 0 AND RAND() < 0.9 THEN 'HOLD' 
                             WHEN v_day_offset > 0 AND RAND() < 0.9 THEN tip.recommendation 
                             WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'BUY', 'SELL') END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ) = 'BUY' THEN 'Bullish trend detected'
                    WHEN COALESCE(
                        CASE WHEN v_day_offset = 0 AND RAND() < 0.9 THEN 'HOLD' 
                             WHEN v_day_offset > 0 AND RAND() < 0.9 THEN tip.recommendation 
                             WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'BUY', 'SELL') END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ) = 'SELL' THEN 'Bearish market signals'
                    ELSE 'Stable market conditions'
                END,
                ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
            FROM query_schedules qs
            LEFT JOIN temp_initial_predictions tip 
                ON tip.survey_id = v_survey_id 
                AND tip.day_offset = v_day_offset 
                AND tip.delay_hours = qs.delay_hours
            WHERE qs.schedule_id = v_schedule_id
            AND qs.query_type_id = @qt_followup
            AND qs.paired_followup_delay_hours IS NULL
            AND v_survey_id IN (15, 16)
            ORDER BY qs.delay_hours;

            -- Insert Follow-up Queries for Survey 17 (Day 1: 60% HOLD, Day 2+: 80% accurate)
            INSERT IGNORE INTO queries (
                survey_id, schedule_id, query_schedule_id, query_type_id, 
                paired_query_id, scheduled_for_utc, status, executed_at_utc, 
                result_json, recommendation, confidence, rationale, source
            )
            SELECT 
                v_survey_id, 
                v_schedule_id, 
                qs.query_schedule_id, 
                @qt_followup, 
                (SELECT query_id FROM temp_base_forecast_queries tbf 
                 WHERE tbf.survey_id = v_survey_id 
                 AND tbf.day_offset = v_day_offset 
                 AND tbf.paired_followup_delay_hours = qs.delay_hours),  -- Link to Baseline Forecast
                DATE_ADD(v_base_time, INTERVAL qs.delay_hours HOUR), 
                'SUCCEEDED', 
                DATE_ADD(DATE_ADD(v_base_time, INTERVAL qs.delay_hours HOUR), INTERVAL 1 MINUTE),
                JSON_OBJECT(
                    'recommendation', COALESCE(
                        CASE WHEN v_day_offset = 0 AND RAND() < 0.6 THEN 'HOLD' 
                             WHEN v_day_offset > 0 AND RAND() < 0.8 THEN tip.recommendation 
                             WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'BUY', 'SELL') END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ),
                    'confidence', ROUND(0.60 + RAND() * 0.35, 2),
                    'rationale', CASE 
                        WHEN COALESCE(
                            CASE WHEN v_day_offset = 0 AND RAND() < 0.6 THEN 'HOLD' 
                                 WHEN v_day_offset > 0 AND RAND() < 0.8 THEN tip.recommendation 
                                 WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'BUY', 'SELL') END,
                            ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                        ) = 'BUY' THEN 'Bullish trend detected'
                        WHEN COALESCE(
                            CASE WHEN v_day_offset = 0 AND RAND() < 0.6 THEN 'HOLD' 
                                 WHEN v_day_offset > 0 AND RAND() < 0.8 THEN tip.recommendation 
                                 WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'BUY', 'SELL') END,
                            ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                        ) = 'SELL' THEN 'Bearish market signals'
                        ELSE 'Stable market conditions'
                    END,
                    'source', ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
                ),
                COALESCE(
                    CASE WHEN v_day_offset = 0 AND RAND() < 0.6 THEN 'HOLD' 
                         WHEN v_day_offset > 0 AND RAND() < 0.8 THEN tip.recommendation 
                         WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'BUY', 'SELL') END,
                    ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                ),
                ROUND(0.60 + RAND() * 0.35, 2),
                CASE 
                    WHEN COALESCE(
                        CASE WHEN v_day_offset = 0 AND RAND() < 0.6 THEN 'HOLD' 
                             WHEN v_day_offset > 0 AND RAND() < 0.8 THEN tip.recommendation 
                             WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'BUY', 'SELL') END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ) = 'BUY' THEN 'Bullish trend detected'
                    WHEN COALESCE(
                        CASE WHEN v_day_offset = 0 AND RAND() < 0.6 THEN 'HOLD' 
                             WHEN v_day_offset > 0 AND RAND() < 0.8 THEN tip.recommendation 
                             WHEN v_day_offset = 0 THEN ELT(FLOOR(1 + RAND() * 2), 'BUY', 'SELL') END,
                        ELT(FLOOR(1 + RAND() * 3), 'BUY', 'SELL', 'HOLD')
                    ) = 'SELL' THEN 'Bearish market signals'
                    ELSE 'Stable market conditions'
                END,
                ELT(FLOOR(1 + RAND() * 4), 'Grok Analysis', 'Market Analyst', 'External Feed', 'AI Model')
            FROM query_schedules qs
            LEFT JOIN temp_initial_predictions tip 
                ON tip.survey_id = v_survey_id 
                AND tip.day_offset = v_day_offset 
                AND tip.delay_hours = qs.delay_hours
            WHERE qs.schedule_id = v_schedule_id
            AND qs.query_type_id = @qt_followup
            AND qs.paired_followup_delay_hours IS NULL
            AND v_survey_id = 17
            ORDER BY qs.delay_hours;

            SET v_day_offset = v_day_offset + 1;
        END WHILE;
    END LOOP;

    CLOSE survey_cursor;

    -- Update paired_query_id for Baseline Forecast queries
    UPDATE queries q
    JOIN query_schedules qs ON q.query_schedule_id = qs.query_schedule_id
    JOIN queries q_followup ON q_followup.survey_id = q.survey_id
        AND q_followup.query_type_id = @qt_followup
        AND q_followup.scheduled_for_utc = DATE_ADD(q.scheduled_for_utc, INTERVAL qs.paired_followup_delay_hours HOUR)
    SET q.paired_query_id = q_followup.query_id
    WHERE q.query_type_id = @qt_base_fore
    AND qs.paired_followup_delay_hours IS NOT NULL;

    -- Clean up temporary tables
    DROP TEMPORARY TABLE IF EXISTS temp_initial_predictions;
    DROP TEMPORARY TABLE IF EXISTS temp_base_forecast_queries;
END $$

DELIMITER ;

-- Execute the procedure
CALL generate_all_surveys_mock_queries();

-- Clean up
DROP PROCEDURE IF EXISTS generate_all_surveys_mock_queries;
