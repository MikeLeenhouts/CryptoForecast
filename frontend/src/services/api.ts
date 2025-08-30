import axios from 'axios';
import type {
  AssetType,
  Asset,
  LLM,
  Prompt,
  QueryType,
  Schedule,
  QuerySchedule,
  Survey,
  CryptoQuery,
  CryptoForecast,
  AssetTypeForm,
  AssetForm,
  LLMForm,
  PromptForm,
  QueryTypeForm,
  ScheduleForm,
  QueryScheduleForm,
  SurveyForm,
  CryptoQueryForm,
  CryptoForecastForm,
  QueryCreateInitial,
  QueryCreateFollowUp,
} from '@/types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8080',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Asset Types API
export const assetTypesApi = {
  getAll: () => api.get<AssetType[]>('/asset-types'),
  getById: (id: number) => api.get<AssetType>(`/asset-types/${id}`),
  create: (data: AssetTypeForm) => api.post<AssetType>('/asset-types', data),
  update: (id: number, data: Partial<AssetTypeForm>) => api.patch<AssetType>(`/asset-types/${id}`, data),
  delete: (id: number) => api.delete(`/asset-types/${id}`),
};

// Assets API
export const assetsApi = {
  getAll: (filters?: { asset_type_id?: number }) => {
    const params = new URLSearchParams();
    if (filters?.asset_type_id) {
      params.append('asset_type_id', filters.asset_type_id.toString());
    }
    return api.get<Asset[]>(`/assets?${params.toString()}`);
  },
  getById: (id: number) => api.get<Asset>(`/assets/${id}`),
  create: (data: AssetForm) => api.post<Asset>('/assets', data),
  update: (id: number, data: Partial<AssetForm>) => api.patch<Asset>(`/assets/${id}`, data),
  delete: (id: number) => api.delete(`/assets/${id}`),
};

// LLMs API
export const llmsApi = {
  getAll: () => api.get<LLM[]>('/llms'),
  getById: (id: number) => api.get<LLM>(`/llms/${id}`),
  create: (data: LLMForm) => api.post<LLM>('/llms', data),
  update: (id: number, data: Partial<LLMForm>) => api.patch<LLM>(`/llms/${id}`, data),
  delete: (id: number) => api.delete(`/llms/${id}`),
};

// Prompts API
export const promptsApi = {
  getAll: (filters?: { llm_id?: number; prompt_version?: number }) => {
    const params = new URLSearchParams();
    if (filters?.llm_id) {
      params.append('llm_id', filters.llm_id.toString());
    }
    if (filters?.prompt_version) {
      params.append('prompt_version', filters.prompt_version.toString());
    }
    return api.get<Prompt[]>(`/prompts?${params.toString()}`);
  },
  getById: (id: number) => api.get<Prompt>(`/prompts/${id}`),
  create: (data: PromptForm) => api.post<Prompt>('/prompts', data),
  update: (id: number, data: Partial<PromptForm>) => api.patch<Prompt>(`/prompts/${id}`, data),
  delete: (id: number) => api.delete(`/prompts/${id}`),
};

// Query Types API
export const queryTypesApi = {
  getAll: () => api.get<QueryType[]>('/query-types'),
  getById: (id: number) => api.get<QueryType>(`/query-types/${id}`),
  create: (data: QueryTypeForm) => api.post<QueryType>('/query-types', data),
  update: (id: number, data: Partial<QueryTypeForm>) => api.patch<QueryType>(`/query-types/${id}`, data),
  delete: (id: number) => api.delete(`/query-types/${id}`),
};

// Schedules API
export const schedulesApi = {
  getAll: () => api.get<Schedule[]>('/schedules'),
  getById: (id: number) => api.get<Schedule>(`/schedules/${id}`),
  create: (data: ScheduleForm) => api.post<Schedule>('/schedules', data),
  update: (id: number, data: Partial<ScheduleForm>) => api.patch<Schedule>(`/schedules/${id}`, data),
  delete: (id: number) => api.delete(`/schedules/${id}`),
};

// Query Schedules API
export const querySchedulesApi = {
  getAll: (filters?: { schedule_id?: number }) => {
    const params = new URLSearchParams();
    if (filters?.schedule_id) {
      params.append('schedule_id', filters.schedule_id.toString());
    }
    return api.get<QuerySchedule[]>(`/query-schedules?${params.toString()}`);
  },
  getById: (id: number) => api.get<QuerySchedule>(`/query-schedules/${id}`),
  create: (data: QueryScheduleForm) => api.post<QuerySchedule>('/query-schedules', data),
  update: (id: number, data: Partial<QueryScheduleForm>) => api.patch<QuerySchedule>(`/query-schedules/${id}`, data),
  delete: (id: number) => api.delete(`/query-schedules/${id}`),
};

// Surveys API
export const surveysApi = {
  getAll: (filters?: { asset_id?: number; schedule_id?: number; prompt_id?: number; is_active?: boolean }) => {
    const params = new URLSearchParams();
    if (filters?.asset_id) {
      params.append('asset_id', filters.asset_id.toString());
    }
    if (filters?.schedule_id) {
      params.append('schedule_id', filters.schedule_id.toString());
    }
    if (filters?.prompt_id) {
      params.append('prompt_id', filters.prompt_id.toString());
    }
    if (filters?.is_active !== undefined) {
      params.append('is_active', filters.is_active.toString());
    }
    return api.get<Survey[]>(`/surveys?${params.toString()}`);
  },
  getById: (id: number) => api.get<Survey>(`/surveys/${id}`),
  create: (data: SurveyForm) => api.post<Survey>('/surveys', data),
  update: (id: number, data: Partial<SurveyForm>) => api.patch<Survey>(`/surveys/${id}`, data),
  delete: (id: number) => api.delete(`/surveys/${id}`),
};

// Crypto Queries API
export const cryptoQueriesApi = {
  getAll: (filters?: { 
    survey_id?: number; 
    schedule_id?: number; 
    query_type_id?: number; 
    status?: string;
    limit?: number;
    offset?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.survey_id) {
      params.append('survey_id', filters.survey_id.toString());
    }
    if (filters?.schedule_id) {
      params.append('schedule_id', filters.schedule_id.toString());
    }
    if (filters?.query_type_id) {
      params.append('query_type_id', filters.query_type_id.toString());
    }
    if (filters?.status) {
      params.append('status', filters.status);
    }
    if (filters?.limit) {
      params.append('limit', filters.limit.toString());
    }
    if (filters?.offset) {
      params.append('offset', filters.offset.toString());
    }
    return api.get<CryptoQuery[]>(`/crypto-queries?${params.toString()}`);
  },
  getById: (id: number) => api.get<CryptoQuery>(`/crypto-queries/${id}`),
  create: (data: CryptoQueryForm) => api.post<CryptoQuery>('/crypto-queries', data),
  update: (id: number, data: Partial<CryptoQueryForm>) => api.patch<CryptoQuery>(`/crypto-queries/${id}`, data),
  delete: (id: number) => api.delete(`/crypto-queries/${id}`),
};

// Crypto Forecasts API
export const cryptoForecastsApi = {
  getAll: (filters?: { 
    query_id?: number; 
    horizon_type?: string;
    limit?: number;
    offset?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.query_id) {
      params.append('query_id', filters.query_id.toString());
    }
    if (filters?.horizon_type) {
      params.append('horizon_type', filters.horizon_type);
    }
    if (filters?.limit) {
      params.append('limit', filters.limit.toString());
    }
    if (filters?.offset) {
      params.append('offset', filters.offset.toString());
    }
    return api.get<CryptoForecast[]>(`/crypto-forecasts?${params.toString()}`);
  },
  getById: (id: number) => api.get<CryptoForecast>(`/crypto-forecasts/${id}`),
  create: (data: CryptoForecastForm) => api.post<CryptoForecast>('/crypto-forecasts', data),
  update: (id: number, data: Partial<CryptoForecastForm>) => api.patch<CryptoForecast>(`/crypto-forecasts/${id}`, data),
  delete: (id: number) => api.delete(`/crypto-forecasts/${id}`),
};

// Legacy aliases for backward compatibility
export const queriesApi = cryptoQueriesApi;
export const reportsApi = cryptoForecastsApi;

// Runtime write-path APIs (for the provisioning endpoints)
export const runtimeApi = {
  createInitialQuery: (data: QueryCreateInitial) => 
    api.post('/queries/initial', data),
  createFollowUpQuery: (data: QueryCreateFollowUp) => 
    api.post('/queries/followup', data),
};

// Health check
export const healthApi = {
  check: () => api.get('/healthz'),
};

export default api;
