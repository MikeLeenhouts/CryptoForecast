// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
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
  api_url: string;
  api_key_secret?: string; // Optional for security
}

export interface Prompt {
  prompt_id: number;
  llm_id: number;
  prompt_text: string;
  prompt_version: number;
}

export interface Survey {
  survey_id: number;
  asset_id: number;
  schedule_id: number;
  prompt_id: number;
  llm_id: number;
  is_active: boolean;
}

export interface Schedule {
  schedule_id: number;
  schedule_name: string;
  schedule_version: number;
  initial_query_time: string;
  description?: string;
}

export interface Query {
  query_id: number;
  survey_id: number;
  query_type: string;
  query_timestamp: string;
  initial_query_id?: number;
}

export interface Report {
  forecast_id: number;
  query_id: number;
  horizon_type: string;
  forecast_value: {
    action: "BUY" | "SELL" | "HOLD";
    confidence?: number;
    reason?: string;
  };
}

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
  api_url: string;
  api_key_secret: string;
}

export interface PromptForm {
  llm_id: number;
  prompt_text: string;
  prompt_version?: number;
}

export interface SurveyForm {
  asset_id: number;
  schedule_id: number;
  prompt_id: number;
  llm_id: number;
  is_active?: boolean;
}

export interface ScheduleForm {
  schedule_name: string;
  schedule_version?: number;
  initial_query_time: string;
  description?: string;
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
