import axios from 'axios';
import type {
  ApiResponse,
  AssetType,
  Asset,
  LLM,
  Prompt,
  Survey,
  Schedule,
  Query,
  Report,
  AssetTypeForm,
  AssetForm,
  LLMForm,
  PromptForm,
  SurveyForm,
  ScheduleForm,
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
  getAll: () => api.get<AssetType[]>('/asset-types', { params: { kwargs: '{}' } }),
  getById: (id: number) => api.get<AssetType>(`/asset-types/${id}`),
  create: (data: AssetTypeForm) => api.post<AssetType>('/asset-types', data),
  update: (id: number, data: AssetTypeForm) => api.put<AssetType>(`/asset-types/${id}`, data),
  delete: (id: number) => api.delete(`/asset-types/${id}`),
};

// Assets API
export const assetsApi = {
  getAll: () => api.get<Asset[]>('/assets', { params: { kwargs: '{}' } }),
  getById: (id: number) => api.get<Asset>(`/assets/${id}`),
  create: (data: AssetForm) => api.post<Asset>('/assets', data),
  update: (id: number, data: AssetForm) => api.put<Asset>(`/assets/${id}`, data),
  delete: (id: number) => api.delete(`/assets/${id}`),
};

// LLMs API
export const llmsApi = {
  getAll: () => api.get<LLM[]>('/llms', { params: { kwargs: '{}' } }),
  getById: (id: number) => api.get<LLM>(`/llms/${id}`),
  create: (data: LLMForm) => api.post<LLM>('/llms', data),
  update: (id: number, data: LLMForm) => api.put<LLM>(`/llms/${id}`, data),
  delete: (id: number) => api.delete(`/llms/${id}`),
};

// Prompts API
export const promptsApi = {
  getAll: () => api.get<Prompt[]>('/prompts', { params: { kwargs: '{}' } }),
  getById: (id: number) => api.get<Prompt>(`/prompts/${id}`),
  create: (data: PromptForm) => api.post<Prompt>('/prompts', data),
  update: (id: number, data: PromptForm) => api.put<Prompt>(`/prompts/${id}`, data),
  delete: (id: number) => api.delete(`/prompts/${id}`),
};

// Surveys API
export const surveysApi = {
  getAll: () => api.get<Survey[]>('/surveys'),
  getById: (id: number) => api.get<Survey>(`/surveys/${id}`),
  create: (data: SurveyForm) => api.post<Survey>('/surveys', data),
  update: (id: number, data: SurveyForm) => api.put<Survey>(`/surveys/${id}`, data),
  delete: (id: number) => api.delete(`/surveys/${id}`),
};

// Schedules API
export const schedulesApi = {
  getAll: () => api.get<Schedule[]>('/schedules', { params: { kwargs: '{}' } }),
  getById: (id: number) => api.get<Schedule>(`/schedules/${id}`),
  create: (data: ScheduleForm) => api.post<Schedule>('/schedules', data),
  update: (id: number, data: ScheduleForm) => api.put<Schedule>(`/schedules/${id}`, data),
  delete: (id: number) => api.delete(`/schedules/${id}`),
};

// Queries API
export const queriesApi = {
  getAll: () => api.get<Query[]>('/crypto-queries', { params: { kwargs: '{}' } }),
  getById: (id: number) => api.get<Query>(`/crypto-queries/${id}`),
  delete: (id: number) => api.delete(`/crypto-queries/${id}`),
};

// Reports API
export const reportsApi = {
  getAll: () => api.get<Report[]>('/crypto-forecasts', { params: { kwargs: '{}' } }),
  getById: (id: number) => api.get<Report>(`/crypto-forecasts/${id}`),
  delete: (id: number) => api.delete(`/crypto-forecasts/${id}`),
};

// Health check
export const healthApi = {
  check: () => api.get('/healthz'),
};

export default api;
