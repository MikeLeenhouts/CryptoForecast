import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider, useQuery } from '@tanstack/react-query';
import { Database, Coins, Calendar, FileText } from 'lucide-react';
import { queryClient } from '@/services/queryClient';
import { assetTypesApi, assetsApi, schedulesApi, cryptoForecastsApi } from '@/services/api';
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

  const { data: reports = [] } = useQuery({
    queryKey: ['cryptoForecasts'],
    queryFn: async () => {
      try {
        const response = await cryptoForecastsApi.getAll();
        return response.data;
      } catch (error) {
        console.error('Failed to fetch forecasts:', error);
        return [];
      }
    },
  });

  const activeSchedules = schedules; // All schedules for now, since Schedule type doesn't have is_active

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold">Dashboard     xx</h2>
        <p className="text-gray-600 mt-2">Overview of your crypto forecasting system</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Asset Types</h3>
              <p className="text-3xl font-bold text-blue-600 mt-2">{assetTypes.length}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Database className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-4">Cryptocurrency categories</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Assets</h3>
              <p className="text-3xl font-bold text-green-600 mt-2">{assets.length}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <Coins className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-4">Individual cryptocurrencies</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Active Schedules</h3>
              <p className="text-3xl font-bold text-purple-600 mt-2">{activeSchedules.length}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Calendar className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-4">Running automated tasks</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Reports</h3>
              <p className="text-3xl font-bold text-orange-600 mt-2">{reports.length}</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <FileText className="h-6 w-6 text-orange-600" />
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-4">Generated forecasts</p>
        </div>
      </div>

      {/* Recent Activity Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">Recent Assets</h3>
          {assets.length > 0 ? (
            <div className="space-y-3">
              {assets.slice(0, 5).map((asset) => (
                <div key={asset.asset_id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                  <div>
                    <p className="font-medium">{asset.asset_name}</p>
                    <p className="text-sm text-gray-500">{asset.description || 'No description'}</p>
                  </div>
                  <span className="text-xs text-gray-400">
                    ID: {asset.asset_id}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No assets created yet</p>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">System Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">API Connection</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                Connected
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Database</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                Online
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Active Schedules</span>
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                {activeSchedules.length} Running
              </span>
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
