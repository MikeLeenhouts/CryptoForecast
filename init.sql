-- Schema for Crypto_Forecasts Database (Updated for MySQL 5.7 compatibility)
-- Supports full survey cycle: 7 queries (1 initial + 6 follow-ups), 13 BUY/SELL/HOLD recommendations

-- 1. asset_types Table
CREATE TABLE asset_types (
    asset_type_id INT AUTO_INCREMENT PRIMARY KEY,
    asset_type_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_asset_type_name (asset_type_name)
) ENGINE=InnoDB;

-- 2. assets Table
CREATE TABLE assets (
    asset_id INT AUTO_INCREMENT PRIMARY KEY,
    asset_type_id INT NOT NULL,
    asset_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_type_id) REFERENCES asset_types(asset_type_id) ON DELETE RESTRICT,
    UNIQUE INDEX idx_asset_name (asset_name),
    INDEX idx_asset_type_id (asset_type_id)
) ENGINE=InnoDB;

-- 3. llms Table
CREATE TABLE llms (
    llm_id INT AUTO_INCREMENT PRIMARY KEY,
    llm_name VARCHAR(255) NOT NULL UNIQUE,
    api_url VARCHAR(255) NOT NULL,
    api_key_secret VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_llm_name (llm_name)
) ENGINE=InnoDB;

-- 4. prompts Table
CREATE TABLE prompts (
    prompt_id INT AUTO_INCREMENT PRIMARY KEY,
    llm_id INT NOT NULL,
    prompt_text TEXT NOT NULL,
    prompt_version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (llm_id) REFERENCES llms(llm_id) ON DELETE RESTRICT,
    UNIQUE INDEX unique_prompt (llm_id, prompt_text(255), prompt_version),
    INDEX idx_llm_id (llm_id)
) ENGINE=InnoDB;

-- 5. schedules Table
CREATE TABLE schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_name VARCHAR(255) NOT NULL,
    schedule_version INT NOT NULL DEFAULT 1,
    initial_query_time TIME NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE INDEX unique_schedule (schedule_name, schedule_version),
    INDEX idx_schedule_name (schedule_name)
) ENGINE=InnoDB;

-- 6. schedule_followups Table
CREATE TABLE schedule_followups (
    followup_id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NOT NULL,
    followup_type VARCHAR(50) NOT NULL,
    delay_hours INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON DELETE CASCADE,
    UNIQUE INDEX unique_followup (schedule_id, followup_type),
    INDEX idx_schedule_id (schedule_id)
) ENGINE=InnoDB;

-- 7. surveys Table
CREATE TABLE surveys (
    survey_id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    schedule_id INT NOT NULL,
    prompt_id INT NOT NULL,
    llm_id INT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE RESTRICT,
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON DELETE RESTRICT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(prompt_id) ON DELETE RESTRICT,
    FOREIGN KEY (llm_id) REFERENCES llms(llm_id) ON DELETE RESTRICT,
    UNIQUE INDEX unique_survey (asset_id, schedule_id, prompt_id, llm_id),
    INDEX idx_asset_id (asset_id),
    INDEX idx_schedule_id (schedule_id),
    INDEX idx_prompt_id (prompt_id),
    INDEX idx_llm_id (llm_id)
) ENGINE=InnoDB;

-- 8. crypto_queries Table
CREATE TABLE crypto_queries (
    query_id INT AUTO_INCREMENT PRIMARY KEY,
    survey_id INT NOT NULL,
    query_type VARCHAR(50) NOT NULL,
    query_timestamp TIMESTAMP NOT NULL,
    initial_query_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (survey_id) REFERENCES surveys(survey_id) ON DELETE RESTRICT,
    FOREIGN KEY (initial_query_id) REFERENCES crypto_queries(query_id) ON DELETE RESTRICT,
    UNIQUE INDEX unique_query (survey_id, query_timestamp, query_type),
    INDEX idx_survey_id (survey_id),
    INDEX idx_initial_query_id (initial_query_id)
) ENGINE=InnoDB;

-- 9. crypto_forecasts Table (Updated: forecast_value changed to JSON)
CREATE TABLE crypto_forecasts (
    forecast_id INT AUTO_INCREMENT PRIMARY KEY,
    query_id INT NOT NULL,
    horizon_type VARCHAR(50) NOT NULL,
    forecast_value JSON,  -- Changed from TEXT to JSON for structured BUY/SELL/HOLD
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES crypto_queries(query_id) ON DELETE CASCADE,
    UNIQUE INDEX unique_forecast (query_id, horizon_type),
    INDEX idx_query_id (query_id)
) ENGINE=InnoDB;

-- Test Data for Full Survey Cycle

-- 1. asset_types
INSERT INTO asset_types (asset_type_name, description)
VALUES
    ('Cryptocurrency', 'Digital Assets, Decentralized digital tokens (e.g., Bitcoin, Ethereum)'),
    ('Equities', 'Stocks, Shares, Ownership in a company, Potential for dividends + capital appreciation');

-- 2. assets
INSERT INTO assets (asset_type_id, asset_name, description)
VALUES
    (1, 'Crypto', 'Cryptocurrencies like Bitcoin and Ethereum'),
    (2, 'US Stocks', 'US-based company stocks');

-- 3. llms
INSERT INTO llms (llm_name, api_url, api_key_secret)
VALUES ('gpt-4o', 'https://api.openai.com/v1/completions', 'arn:aws:secretsmanager:us-east-1:123456789012:secret:myapp/llm-api-key-gpt4o');

-- 4. prompts
INSERT INTO prompts (llm_id, prompt_text, prompt_version)
VALUES (1, 'Forecast Bitcoin price for multiple horizons with BUY/SELL/HOLD recommendations', 1);

-- 5. schedules
INSERT INTO schedules (schedule_name, schedule_version, initial_query_time, description)
VALUES ('Daily Crypto', 1, '09:00:00', 'Daily forecasts with follow-ups at 1, 6, 11 hours, 1 day, 5 days, 10 days');

-- 6. schedule_followups
INSERT INTO schedule_followups (schedule_id, followup_type, delay_hours)
VALUES
    (1, 'OneHour', 1),
    (1, 'SixHour', 6),
    (1, 'ElevenHour', 11),
    (1, 'OneDay', 24),
    (1, 'FiveDay', 120),
    (1, 'TenDay', 240);

-- 7. surveys
INSERT INTO surveys (asset_id, schedule_id, prompt_id, llm_id, is_active)
VALUES (1, 1, 1, 1, TRUE);

-- 8. crypto_queries (Full survey cycle: 1 initial + 6 follow-ups)
INSERT INTO crypto_queries (survey_id, query_type, query_timestamp, initial_query_id)
VALUES
    (1, 'Initial', '2025-08-20 09:00:00', NULL),          -- query_id=1
    (1, 'FollowUp', '2025-08-20 10:00:00', 1),            -- query_id=2, OneHour
    (1, 'FollowUp', '2025-08-20 15:00:00', 1),            -- query_id=3, SixHour
    (1, 'FollowUp', '2025-08-20 20:00:00', 1),            -- query_id=4, ElevenHour
    (1, 'FollowUp', '2025-08-21 09:00:00', 1),            -- query_id=5, OneDay
    (1, 'FollowUp', '2025-08-25 09:00:00', 1),            -- query_id=6, FiveDay
    (1, 'FollowUp', '2025-08-30 09:00:00', 1);            -- query_id=7, TenDay

-- 9. crypto_forecasts (13 recommendations: 7 initial + 6 follow-up)
INSERT INTO crypto_forecasts (query_id, horizon_type, forecast_value)
VALUES
    -- Initial query (query_id=1): 7 recommendations (current + 6 predicted)
    (1, 'Initial', '{"action": "BUY"}'),
    (1, 'OneHour', '{"action": "HOLD"}'),
    (1, 'SixHour', '{"action": "HOLD"}'),
    (1, 'ElevenHour', '{"action": "SELL"}'),
    (1, 'OneDay', '{"action": "HOLD"}'),
    (1, 'FiveDay', '{"action": "BUY"}'),
    (1, 'TenDay', '{"action": "HOLD"}'),
    -- Follow-up queries: 1 actual recommendation each
    (2, 'OneHour', '{"action": "BUY"}'),
    (3, 'SixHour', '{"action": "SELL"}'),
    (4, 'ElevenHour', '{"action": "HOLD"}'),
    (5, 'OneDay', '{"action": "BUY"}'),
    (6, 'FiveDay', '{"action": "HOLD"}'),
    (7, 'TenDay', '{"action": "BUY"}');