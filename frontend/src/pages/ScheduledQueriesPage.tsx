import { useQuery } from '@tanstack/react-query';
import DataTable from '@/components/DataTable';
import { scheduledQueriesApi } from '@/services/api';
import type { ScheduledQuery, TableColumn } from '@/types';

export default function ScheduledQueriesPage() {
  // Fetch scheduled queries from LocalStack EventBridge
  const { data: scheduledQueries = [], isLoading } = useQuery({
    queryKey: ['scheduledQueries'],
    queryFn: async () => {
      const response = await scheduledQueriesApi.getAll();
      return response.data;
    },
  });

  const formatDateTime = (dateTimeString: string) => {
    if (!dateTimeString) return '-';
    try {
      return new Date(dateTimeString).toLocaleString();
    } catch {
      return dateTimeString;
    }
  };

  const formatScheduleExpression = (expression: string) => {
    if (!expression) return '-';
    // Convert "at(2025-10-04T01:00:00)" to more readable format
    const match = expression.match(/at\((.+)\)/);
    if (match) {
      try {
        return new Date(match[1]).toLocaleString();
      } catch {
        return expression;
      }
    }
    return expression;
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case 'ENABLED': return 'bg-green-100 text-green-800';
      case 'DISABLED': return 'bg-red-100 text-red-800';
      case 'ERROR': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const columns: TableColumn<ScheduledQuery>[] = [
    {
      key: 'survey_init',
      title: 'Survey Init',
      sortable: true,
      render: (value) => formatDateTime(value as string),
    },
    {
      key: 'query_schedule',
      title: 'Query Schedule',
      sortable: true,
      render: (value) => formatScheduleExpression(value as string),
    },
    {
      key: 'schedule_name',
      title: 'Schedule Name',
      sortable: true,
    },
    {
      key: 'query_type',
      title: 'Query Type',
      sortable: true,
    },
    {
      key: 'delay_hours',
      title: 'Delay Hours',
      sortable: true,
      render: (value) => {
        const hours = value as number;
        return hours === 0 ? 'Immediate' : hours === 1 ? '1 hour' : `${hours} hours`;
      },
    },
    {
      key: 'asset',
      title: 'Asset',
      sortable: true,
    },
    {
      key: 'llm',
      title: 'LLM',
      sortable: true,
    },
    {
      key: 'target_llm',
      title: 'Target LLM',
      sortable: true,
    },
    {
      key: 'prompt_type',
      title: 'Prompt Type',
      sortable: true,
      render: (value) => {
        const type = value as string;
        return (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            type === 'live' ? 'bg-blue-100 text-blue-800' : 
            type === 'forecast' ? 'bg-purple-100 text-purple-800' : 
            'bg-gray-100 text-gray-800'
          }`}>
            {type}
          </span>
        );
      },
    },
    {
      key: 'state',
      title: 'State',
      sortable: true,
      render: (value) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStateColor(value as string)}`}>
          {value as string}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Scheduled Queries</h2>
        </div>
      </div>

      <DataTable
        title="Scheduled Queries"
        data={scheduledQueries}
        columns={columns}
        loading={isLoading}
        searchPlaceholder="Search scheduled queries..."
      />
    </div>
  );
}
