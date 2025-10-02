import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider, useQuery } from '@tanstack/react-query';
import { queryClient } from '@/services/queryClient';
import { assetsApi, schedulesApi, surveysApi, promptsApi, llmsApi, assetTypesApi } from '@/services/api';
import Layout from '@/components/Layout';
import AssetTypesPage from '@/pages/AssetTypesPage';
import AssetsPage from '@/pages/AssetsPage';
import LLMsPage from '@/pages/LLMsPage';
import PromptsPage from '@/pages/PromptsPage';
import QueryTypesPage from '@/pages/QueryTypesPage';
import SchedulesPage from '@/pages/SchedulesPage';
import QuerySchedulesPage from '@/pages/QuerySchedulesPage';
import SurveysPage from '@/pages/SurveysPage';
import QueriesPage from '@/pages/QueriesPage';
import ReportsPage from '@/pages/ReportsPage';

// Dashboard component with real data
const DashboardPage = () => {
  const { data: assets = [] } = useQuery({
    queryKey: ['assets'],
    queryFn: async () => {
      try {
        const response = await assetsApi.getAll();
        return response.data;
      } catch (error) {
        console.error('Failed to fetch assets:', error);
        return [];
      }
    },
  });

  const { data: schedules = [] } = useQuery({
    queryKey: ['schedules'],
    queryFn: async () => {
      try {
        const response = await schedulesApi.getAll();
        return response.data;
      } catch (error) {
        console.error('Failed to fetch schedules:', error);
        return [];
      }
    },
  });


  const { data: surveys = [] } = useQuery({
    queryKey: ['surveys'],
    queryFn: async () => {
      try {
        const response = await surveysApi.getAll();
        return response.data;
      } catch (error) {
        console.error('Failed to fetch surveys:', error);
        return [];
      }
    },
  });

  const { data: prompts = [] } = useQuery({
    queryKey: ['prompts'],
    queryFn: async () => {
      try {
        const response = await promptsApi.getAll();
        return response.data;
      } catch (error) {
        console.error('Failed to fetch prompts:', error);
        return [];
      }
    },
  });

  const { data: llms = [] } = useQuery({
    queryKey: ['llms'],
    queryFn: async () => {
      try {
        const response = await llmsApi.getAll();
        return response.data;
      } catch (error) {
        console.error('Failed to fetch llms:', error);
        return [];
      }
    },
  });

  const { data: assetTypes = [] } = useQuery({
    queryKey: ['assetTypes'],
    queryFn: async () => {
      try {
        const response = await assetTypesApi.getAll();
        return response.data;
      } catch (error) {
        console.error('Failed to fetch asset types:', error);
        return [];
      }
    },
  });

  const activeSurveys = surveys.filter(survey => survey.is_active);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold">Dashboard</h2>
      </div>
      
      <div style={{ paddingLeft: '%' }}>
        <div className="grid grid-cols-1 gap-6" style={{ width: '70%' }}>
          <div className="bg-white pt-0 px-6 pb-3 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-gray-800 mb-4" style={{ fontWeight: 600, fontSize: '20px', lineHeight: 1.1, fontStyle: 'normal' }}>Active Surveys</div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Asset</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">LLM</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Followup LLM</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Live Prompt</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Forecast Prompt</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Schedule</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {activeSurveys.map((survey) => {
                    const asset = assets.find(a => a.asset_id === survey.asset_id);
                    const livePrompt = prompts.find(p => p.prompt_id === survey.live_prompt_id);
                    const forecastPrompt = prompts.find(p => p.prompt_id === survey.forecast_prompt_id);
                    const liveLlm = llms.find(l => l.llm_id === livePrompt?.llm_id);
                    const followupLlm = llms.find(l => l.llm_id === livePrompt?.target_llm_id);
                    const schedule = schedules.find(s => s.schedule_id === survey.schedule_id);
                    
                    return (
                      <tr key={survey.survey_id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{survey.survey_id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{asset?.asset_name || 'Unknown'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{liveLlm?.llm_name || 'Unknown'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{followupLlm?.llm_name || 'Unknown'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{livePrompt?.prompt_name || 'Unknown'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{forecastPrompt?.prompt_name || 'Unknown'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{schedule?.schedule_name || 'Unknown'}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs rounded-full ${survey.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                            {survey.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                  {activeSurveys.length === 0 && (
                    <tr>
                      <td colSpan={8} className="px-6 py-4 text-center text-sm text-gray-500">No active surveys found</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          
          <div className="bg-white pt-0 px-6 pb-3 rounded-lg shadow-sm border border-gray-200">
            <div className="text-3xl font-bold text-gray-800 mb-4" style={{ fontWeight: 600, fontSize: '20px', lineHeight: 1.1, fontStyle: 'normal' }}>LLMs</div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Model</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">API URL</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {llms.map((llm) => (
                    <tr key={llm.llm_id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{llm.llm_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{llm.llm_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{llm.llm_model}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{llm.api_url}</td>
                    </tr>
                  ))}
                  {llms.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">No LLMs found</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          
          <div className="bg-white pt-0 px-6 pb-3 rounded-lg shadow-sm border border-gray-200">
            <div className="text-3xl font-bold text-gray-800 mb-4" style={{ fontWeight: 600, fontSize: '20px', lineHeight: 1.1, fontStyle: 'normal' }}>Schedules</div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Query Time</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timezone</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {schedules.map((schedule) => (
                    <tr key={schedule.schedule_id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{schedule.schedule_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{schedule.schedule_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{schedule.schedule_version}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{schedule.initial_query_time}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{schedule.timezone}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{schedule.description || 'No description'}</td>
                    </tr>
                  ))}
                  {schedules.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-4 text-center text-sm text-gray-500">No schedules found</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          
          <div className="bg-white pt-0 px-6 pb-3 rounded-lg shadow-sm border border-gray-200">
            <div className="text-3xl font-bold text-gray-800 mb-4" style={{ fontWeight: 600, fontSize: '20px', lineHeight: 1.1, fontStyle: 'normal' }}>Assets</div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Asset Type</th>
                    <th className="px-6 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {assets.map((asset) => {
                    const assetType = assetTypes.find(type => type.asset_type_id === asset.asset_type_id);
                    
                    return (
                      <tr key={asset.asset_id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{asset.asset_id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{asset.asset_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{assetType?.asset_type_name || 'Unknown'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{asset.description || 'No description'}</td>
                      </tr>
                    );
                  })}
                  {assets.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">No assets found</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>


          <div className="bg-white pt-0 px-6 pb-3 rounded-lg shadow-sm border border-gray-200">
            <div className="text-3xl font-bold text-gray-800 mb-4" style={{ fontWeight: 600, fontSize: '20px', lineHeight: 1.1, fontStyle: 'normal' }}>System Status</div>
            <div className="overflow-x-auto">
              <table className="divide-y divide-gray-200" style={{ width: 'auto' }}>
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" style={{ width: '140px' }}>Component</th>
                    <th className="px-3 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" style={{ width: '120px' }}>Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  <tr>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">API Connection</td>
                    <td className="px-3 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                        Connected
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">Database</td>
                    <td className="px-3 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                        Online
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="asset-types" element={<AssetTypesPage />} />
            <Route path="assets" element={<AssetsPage />} />
            <Route path="llms" element={<LLMsPage />} />
            <Route path="prompts" element={<PromptsPage />} />
            <Route path="query-types" element={<QueryTypesPage />} />
            <Route path="schedules" element={<SchedulesPage />} />
            <Route path="query-schedules" element={<QuerySchedulesPage />} />
            <Route path="surveys" element={<SurveysPage />} />
            <Route path="queries" element={<QueriesPage />} />
            <Route path="reports" element={<ReportsPage />} />
          </Route>
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
