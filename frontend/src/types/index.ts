// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

// Shared Types
export type Action = "BUY" | "SELL" | "HOLD";
export type QueryStatus = "PLANNED" | "RUNNING" | "SUCCEEDED" | "FAILED" | "CANCELLED";

export interface ForecastPayload {
  action: Action;
  confidence?: number;
  reason?: string;
}

// Entity Types based on the backend models
export interface AssetType {
  asset_type_id: number;
  asset_type_name: string;
  description?: string;
}

export interface Asset {
  asset_id: number;
  asset_name: string;
  asset_type_id: number;
  description?: string;
}

export interface LLM {
  llm_id: number;
  llm_name: string;
  llm_model: string;
  api_url: string;
  // api_key_secret is not returned in responses for security
}

export interface Prompt {
  prompt_id: number;
  llm_id: number;
  prompt_text: string;
  prompt_version: number;
}

export interface QueryType {
  query_type_id: number;
  query_type_name: string;
  description?: string;
}

export interface Schedule {
  schedule_id: number;
  schedule_name: string;
  schedule_version: number;
  initial_query_time: string; // "HH:MM:SS" format
  timezone: string;
  description?: string;
}

export interface QuerySchedule {
  query_schedule_id: number;
  schedule_id: number;
  query_type_id: number;
  delay_hours: number;
  paired_followup_delay_hours?: number;
}

export interface Survey {
  survey_id: number;
  asset_id: number;
  schedule_id: number;
  prompt_id: number;
  is_active: boolean;
}

export interface CryptoQuery {
  query_id: number;
  survey_id: number;
  schedule_id: number;
  query_type_id: number;
  target_delay_hours?: number;
  scheduled_for_utc: string; // ISO datetime string
  status: QueryStatus;
  executed_at_utc?: string; // ISO datetime string
  result_json?: Record<string, unknown>;
  error_text?: string;
  // NEW: Four additional fields for query recommendations
  recommendation?: string;
  confidence?: number;
  rationale?: string;
  source?: string;
}

export interface CryptoForecast {
  forecast_id: number;
  query_id: number;
  horizon_type: string;
  forecast_value?: Record<string, unknown>;
}

// Legacy aliases for backward compatibility
export type Query = CryptoQuery;
export type Report = CryptoForecast;

// Form Types
export interface AssetTypeForm {
  asset_type_name: string;
  description?: string;
}

export interface AssetForm {
  asset_name: string;
  asset_type_id: number;
  description?: string;
}

export interface LLMForm {
  llm_name: string;
  llm_model: string;
  api_url: string;
  api_key_secret: string;
}

export interface PromptForm {
  llm_id: number;
  prompt_text: string;
  prompt_version?: number;
}

export interface QueryTypeForm {
  query_type_name: string;
  description?: string;
}

export interface ScheduleForm {
  schedule_name: string;
  schedule_version?: number;
  initial_query_time: string; // "HH:MM:SS" format
  timezone?: string;
  description?: string;
}

export interface QueryScheduleForm {
  schedule_id: number;
  query_type_id: number;
  delay_hours: number;
  paired_followup_delay_hours?: number;
}

export interface SurveyForm {
  asset_id: number;
  schedule_id: number;
  prompt_id: number;
  is_active?: boolean;
}

export interface CryptoQueryForm {
  survey_id: number;
  schedule_id: number;
  query_type_id: number;
  target_delay_hours?: number;
  scheduled_for_utc: string; // ISO datetime string
  status?: QueryStatus;
  executed_at_utc?: string; // ISO datetime string
  result_json?: Record<string, unknown>;
  error_text?: string;
  // NEW: Four additional fields for query recommendations
  recommendation?: string;
  confidence?: number;
  rationale?: string;
  source?: string;
}

export interface CryptoForecastForm {
  query_id: number;
  horizon_type: string;
  forecast_value?: Record<string, unknown>;
}

// Runtime write-path DTOs
export interface QueryCreateInitial {
  query_timestamp: string; // ISO datetime string
  initial_forecasts: Record<string, ForecastPayload>;
}

export interface QueryCreateFollowUp {
  query_timestamp: string; // ISO datetime string
  horizon_type: string;
  forecast: ForecastPayload;
}

// Navigation Types
export interface NavItem {
  title: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
  children?: NavItem[];
}

// Table Types
export interface TableColumn<T> {
  key: keyof T;
  title: string;
  render?: (value: T[keyof T], record: T) => React.ReactNode;
  sortable?: boolean;
}

export interface TableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  onEdit?: (record: T) => void;
  onDelete?: (record: T) => void;
  onView?: (record: T) => void;
}
