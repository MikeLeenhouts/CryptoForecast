import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import DataTable from '@/components/DataTable';
import { cryptoQueriesApi, surveysApi, assetsApi, schedulesApi, queryTypesApi } from '@/services/api';
import type { CryptoQuery, Survey, Asset, Schedule, QueryType, TableColumn } from '@/types';
import { useState } from 'react';

export default function QueriesPage() {
  const [viewingItem, setViewingItem] = useState<CryptoQuery | null>(null);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  
  const queryClient = useQueryClient();

  // Fetch queries
  const { data: queries = [], isLoading } = useQuery({
    queryKey: ['cryptoQueries'],
    queryFn: async () => {
      const response = await cryptoQueriesApi.getAll();
      return response.data;
    },
  });

  // Fetch related data for display
  const { data: surveys = [] } = useQuery({
    queryKey: ['surveys'],
    queryFn: async () => {
      const response = await surveysApi.getAll();
      return response.data;
    },
  });

  const { data: assets = [] } = useQuery({
    queryKey: ['assets'],
    queryFn: async () => {
      const response = await assetsApi.getAll();
      return response.data;
    },
  });

  const { data: schedules = [] } = useQuery({
    queryKey: ['schedules'],
    queryFn: async () => {
      const response = await schedulesApi.getAll();
      return response.data;
    },
  });

  const { data: queryTypes = [] } = useQuery({
    queryKey: ['queryTypes'],
    queryFn: async () => {
      const response = await queryTypesApi.getAll();
      return response.data;
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => cryptoQueriesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cryptoQueries'] });
    },
  });

  const handleView = (item: CryptoQuery) => {
    setViewingItem(item);
    setIsViewDialogOpen(true);
  };

  const handleDelete = (item: CryptoQuery) => {
    if (confirm('Are you sure you want to delete this query?')) {
      deleteMutation.mutate(item.query_id);
    }
  };

  const getSurveyInfo = (surveyId: number) => {
    const survey = surveys.find((s: Survey) => s.survey_id === surveyId);
    if (!survey) return { assetName: 'Unknown', scheduleName: 'Unknown' };
    
    const asset = assets.find((a: Asset) => a.asset_id === survey.asset_id);
    const schedule = schedules.find((s: Schedule) => s.schedule_id === survey.schedule_id);
    
    return {
      assetName: asset?.asset_name || 'Unknown',
      scheduleName: schedule?.schedule_name || 'Unknown'
    };
  };

  const getQueryTypeName = (queryTypeId: number) => {
    const queryType = queryTypes.find((qt: QueryType) => qt.query_type_id === queryTypeId);
    return queryType?.query_type_name || `Type ${queryTypeId}`;
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PLANNED': return 'bg-gray-100 text-gray-800';
      case 'RUNNING': return 'bg-blue-100 text-blue-800';
      case 'SUCCEEDED': return 'bg-green-100 text-green-800';
      case 'FAILED': return 'bg-red-100 text-red-800';
      case 'CANCELLED': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const columns: TableColumn<CryptoQuery>[] = [
    {
      key: 'query_id',
      title: 'ID',
    },
    {
      key: 'survey_id',
      title: 'Asset',
      render: (value) => {
        const { assetName } = getSurveyInfo(value as number);
        return assetName;
      },
    },
    {
      key: 'schedule_id',
      title: 'Schedule',
      render: (value, record) => {
        const { scheduleName } = getSurveyInfo(record.survey_id);
        return scheduleName;
      },
    },
    {
      key: 'query_type_id',
      title: 'Type',
      render: (value) => getQueryTypeName(value as number),
    },
    {
      key: 'status',
      title: 'Status',
      render: (value) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(value as string)}`}>
          {value as string}
        </span>
      ),
    },
    {
      key: 'scheduled_for_utc',
      title: 'Scheduled For',
      render: (value) => formatTimestamp(value as string),
    },
    {
      key: 'executed_at_utc',
      title: 'Executed At',
      render: (value) => value ? formatTimestamp(value as string) : '-',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Queries</h2>
          <p className="text-gray-600 mt-2">View and manage crypto forecast queries</p>
        </div>
      </div>

      <DataTable
        title="Crypto Queries"
        data={queries}
        columns={columns}
        loading={isLoading}
        onView={handleView}
        onDelete={handleDelete}
        searchPlaceholder="Search queries..."
      />

      {/* View Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Query Details</DialogTitle>
          </DialogHeader>
          {viewingItem && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Query ID</label>
                  <p className="text-lg font-semibold">#{viewingItem.query_id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Type</label>
                  <p className="text-lg">{getQueryTypeName(viewingItem.query_type_id)}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Asset</label>
                  <p className="text-lg">{getSurveyInfo(viewingItem.survey_id).assetName}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Schedule</label>
                  <p className="text-lg">{getSurveyInfo(viewingItem.survey_id).scheduleName}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Status</label>
                  <p className="text-lg">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(viewingItem.status)}`}>
                      {viewingItem.status}
                    </span>
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Target Delay Hours</label>
                  <p className="text-lg">{viewingItem.target_delay_hours || '-'}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Scheduled For</label>
                  <p className="text-lg">{formatTimestamp(viewingItem.scheduled_for_utc)}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Executed At</label>
                  <p className="text-lg">{viewingItem.executed_at_utc ? formatTimestamp(viewingItem.executed_at_utc) : 'Not executed'}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Survey ID</label>
                  <p className="text-lg">#{viewingItem.survey_id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Schedule ID</label>
                  <p className="text-lg">#{viewingItem.schedule_id}</p>
                </div>
              </div>

              {viewingItem.result_json && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Result JSON</label>
                  <pre className="mt-1 p-3 bg-gray-100 rounded-md text-sm overflow-auto max-h-40">
                    {JSON.stringify(viewingItem.result_json, null, 2)}
                  </pre>
                </div>
              )}

              {viewingItem.error_text && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Error</label>
                  <p className="mt-1 p-3 bg-red-50 text-red-800 rounded-md text-sm">
                    {viewingItem.error_text}
                  </p>
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
