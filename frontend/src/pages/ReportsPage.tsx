import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { cryptoForecastsApi, cryptoQueriesApi } from '@/services/api';
import DataTable from '@/components/DataTable';
import type { CryptoForecast, CryptoQuery, TableColumn } from '@/types';

export default function ReportsPage() {
  const [viewingItem, setViewingItem] = useState<CryptoForecast | null>(null);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);

  // Fetch forecasts (reports)
  const { data: forecasts = [], isLoading } = useQuery({
    queryKey: ['cryptoForecasts'],
    queryFn: async () => {
      const response = await cryptoForecastsApi.getAll();
      return response.data;
    },
  });

  // Fetch queries for reference
  const { data: queries = [] } = useQuery({
    queryKey: ['cryptoQueries'],
    queryFn: async () => {
      const response = await cryptoQueriesApi.getAll();
      return response.data;
    },
  });

  const getQueryInfo = (queryId: number) => {
    const query = queries.find((q: CryptoQuery) => q.query_id === queryId);
    return query || null;
  };

  const formatForecastValue = (value: Record<string, unknown> | null | undefined) => {
    if (!value) return '-';
    
    // Check if it's a forecast payload structure
    if (typeof value === 'object' && 'action' in value) {
      const action = value.action as string;
      const confidence = value.confidence as number | undefined;
      const reason = value.reason as string | undefined;
      
      return (
        <div className="space-y-1">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            action === 'BUY' ? 'bg-green-100 text-green-800' :
            action === 'SELL' ? 'bg-red-100 text-red-800' :
            'bg-yellow-100 text-yellow-800'
          }`}>
            {action}
          </span>
          {confidence && <div className="text-xs text-gray-500">Confidence: {(confidence * 100).toFixed(1)}%</div>}
          {reason && <div className="text-xs text-gray-600 truncate max-w-32" title={reason}>{reason}</div>}
        </div>
      );
    }
    
    return JSON.stringify(value);
  };

  const columns: TableColumn<CryptoForecast>[] = [
    {
      key: 'forecast_id',
      title: 'ID',
    },
    {
      key: 'query_id',
      title: 'Query ID',
      render: (value) => `#${value}`,
    },
    {
      key: 'horizon_type',
      title: 'Horizon Type',
    },
    {
      key: 'forecast_value',
      title: 'Forecast',
      render: (value) => formatForecastValue(value as Record<string, unknown>),
    },
  ];

  const handleView = (forecast: CryptoForecast) => {
    setViewingItem(forecast);
    setIsViewDialogOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">Reports</h2>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Forecasts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{forecasts.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Buy Signals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {forecasts.filter(f => 
                f.forecast_value && 
                typeof f.forecast_value === 'object' && 
                'action' in f.forecast_value && 
                f.forecast_value.action === 'BUY'
              ).length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Sell Signals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {forecasts.filter(f => 
                f.forecast_value && 
                typeof f.forecast_value === 'object' && 
                'action' in f.forecast_value && 
                f.forecast_value.action === 'SELL'
              ).length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Hold Signals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {forecasts.filter(f => 
                f.forecast_value && 
                typeof f.forecast_value === 'object' && 
                'action' in f.forecast_value && 
                f.forecast_value.action === 'HOLD'
              ).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Forecasts Table */}
      <DataTable
        title="Crypto Forecasts"
        data={forecasts}
        columns={columns}
        loading={isLoading}
        onView={handleView}
        searchPlaceholder="Search forecasts..."
      />

      {/* View Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Forecast Details</DialogTitle>
          </DialogHeader>
          {viewingItem && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Forecast ID</label>
                  <p className="text-lg font-semibold">#{viewingItem.forecast_id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Query ID</label>
                  <p className="text-lg">#{viewingItem.query_id}</p>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Horizon Type</label>
                <p className="text-lg">{viewingItem.horizon_type}</p>
              </div>

              {viewingItem.forecast_value && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Forecast Value</label>
                  <div className="mt-1 p-3 bg-gray-100 rounded-md">
                    {typeof viewingItem.forecast_value === 'object' && 'action' in viewingItem.forecast_value ? (
                      <div className="space-y-2">
                        <div>
                          <span className="text-sm font-medium">Action: </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            viewingItem.forecast_value.action === 'BUY' ? 'bg-green-100 text-green-800' :
                            viewingItem.forecast_value.action === 'SELL' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {viewingItem.forecast_value.action as string}
                          </span>
                        </div>
                        {viewingItem.forecast_value.confidence && (
                          <div>
                            <span className="text-sm font-medium">Confidence: </span>
                            <span>{((viewingItem.forecast_value.confidence as number) * 100).toFixed(1)}%</span>
                          </div>
                        )}
                        {viewingItem.forecast_value.reason && (
                          <div>
                            <span className="text-sm font-medium">Reason: </span>
                            <p className="text-sm text-gray-700 mt-1">{String(viewingItem.forecast_value.reason)}</p>
                          </div>
                        )}
                      </div>
                    ) : (
                      <pre className="text-sm overflow-auto">
                        {JSON.stringify(viewingItem.forecast_value, null, 2)}
                      </pre>
                    )}
                  </div>
                </div>
              )}

              {getQueryInfo(viewingItem.query_id) && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Related Query Info</label>
                  <div className="mt-1 p-3 bg-blue-50 rounded-md text-sm">
                    <p><strong>Status:</strong> {getQueryInfo(viewingItem.query_id)?.status}</p>
                    <p><strong>Scheduled:</strong> {getQueryInfo(viewingItem.query_id)?.scheduled_for_utc}</p>
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-2 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setIsViewDialogOpen(false)}
                >
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
