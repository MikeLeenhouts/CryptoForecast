import { useQuery } from '@tanstack/react-query';
import DataTable from '@/components/DataTable';
import { queriesApi, surveysApi, assetsApi, schedulesApi, queryTypesApi, assetTypesApi } from '@/services/api';
import type { CryptoQuery, Survey, Asset, Schedule, QueryType, AssetType, TableColumn } from '@/types';

export default function QueriesPage() {

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

  const { data: queryTypes = [] } = useQuery({
    queryKey: ['queryTypes'],
    queryFn: async () => {
      const response = await queryTypesApi.getAll();
      return response.data;
    },
  });

  const { data: assetTypes = [] } = useQuery({
    queryKey: ['assetTypes'],
    queryFn: async () => {
      const response = await assetTypesApi.getAll();
      return response.data;
    },
  });


  const getSurveyInfo = (surveyId: number) => {
    const survey = surveys.find((s: Survey) => s.survey_id === surveyId);
    if (!survey) return { assetName: 'Unknown', assetTypeName: 'Unknown', scheduleName: 'Unknown' };
    
    const asset = assets.find((a: Asset) => a.asset_id === survey.asset_id);
    const schedule = schedules.find((s: Schedule) => s.schedule_id === survey.schedule_id);
    const assetType = asset ? assetTypes.find((at: AssetType) => at.asset_type_id === asset.asset_type_id) : null;
    
    return {
      assetName: asset?.asset_name || 'Unknown',
      assetTypeName: assetType?.asset_type_name || 'Unknown',
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
      key: 'asset_type' as keyof CryptoQuery,
      title: 'Asset_Type',
      render: (value, record) => {
        const { assetTypeName } = getSurveyInfo(record.survey_id);
        return assetTypeName;
      },
    },
    {
      key: 'query_type_id',
      title: 'Query_Type',
      render: (value) => getQueryTypeName(value as number),
    },
    {
      key: 'scheduled_for_utc',
      title: 'Scheduled_For',
      render: (value) => formatTimestamp(value as string),
    },
    {
      key: 'executed_at_utc',
      title: 'Executed_At',
      render: (value) => value ? formatTimestamp(value as string) : '-',
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
      key: 'recommendation',
      title: 'Recommendation',
      render: (value) => {
        if (!value) return '-';
        const str = value as string;
        return str.length > 30 ? str.substring(0, 30) + '...' : str;
      },
    },
    {
      key: 'confidence',
      title: 'Confidence',
      render: (value) => value !== null && value !== undefined ? `${(value as number * 100).toFixed(1)}%` : '-',
    },
    {
      key: 'rationale',
      title: 'Rationale',
      render: (value) => {
        if (!value) return '-';
        const str = value as string;
        return str.length > 40 ? str.substring(0, 40) + '...' : str;
      },
    },
    {
      key: 'source',
      title: 'Source',
      render: (value) => (value as string) || '-',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Queries</h2>
        </div>
      </div>

      <DataTable
        title="Crypto Queries"
        data={queries}
        columns={columns}
        loading={isLoading}
        searchPlaceholder="Search queries..."
      />

    </div>
  );
}
