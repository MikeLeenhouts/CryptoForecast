import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import DataTable from '@/components/DataTable';
import { queriesApi, surveysApi, assetsApi, schedulesApi } from '@/services/api';
import type { Query, Survey, Asset, Schedule, TableColumn } from '@/types';
import { useState } from 'react';

export default function QueriesPage() {
  const [viewingItem, setViewingItem] = useState<Query | null>(null);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  
  const queryClient = useQueryClient();

  // Fetch queries
  const { data: queries = [], isLoading } = useQuery({
    queryKey: ['queries'],
    queryFn: async () => {
      const response = await queriesApi.getAll();
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

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => queriesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['queries'] });
    },
  });

  const handleView = (item: Query) => {
    setViewingItem(item);
    setIsViewDialogOpen(true);
  };

  const handleDelete = (item: Query) => {
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

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const columns: TableColumn<Query>[] = [
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
      key: 'survey_id',
      title: 'Schedule',
      render: (value, record) => {
        const { scheduleName } = getSurveyInfo(record.survey_id);
        return scheduleName;
      },
    },
    {
      key: 'query_type',
      title: 'Type',
      render: (value) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          value === 'Initial' 
            ? 'bg-blue-100 text-blue-800' 
            : 'bg-green-100 text-green-800'
        }`}>
          {value as string}
        </span>
      ),
    },
    {
      key: 'query_timestamp',
      title: 'Timestamp',
      render: (value) => formatTimestamp(value as string),
    },
    {
      key: 'initial_query_id',
      title: 'Parent Query',
      render: (value) => value ? `#${value}` : '-',
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
                  <p className="text-lg">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      viewingItem.query_type === 'Initial' 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {viewingItem.query_type}
                    </span>
                  </p>
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

              <div>
                <label className="text-sm font-medium text-gray-500">Timestamp</label>
                <p className="text-lg">{formatTimestamp(viewingItem.query_timestamp)}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Survey ID</label>
                  <p className="text-lg">#{viewingItem.survey_id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Parent Query</label>
                  <p className="text-lg">
                    {viewingItem.initial_query_id ? `#${viewingItem.initial_query_id}` : 'None (Initial Query)'}
                  </p>
                </div>
              </div>

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
