import { useQuery } from '@tanstack/react-query';
import DataTable from '@/components/DataTable';
import { queryTypesApi } from '@/services/api';
import type { QueryType, TableColumn } from '@/types';

export default function QueryTypesPage() {

  // Fetch query types
  const { data: queryTypes = [], isLoading } = useQuery({
    queryKey: ['queryTypes'],
    queryFn: async () => {
      const response = await queryTypesApi.getAll();
      return response.data;
    },
  });

  const columns: TableColumn<QueryType>[] = [
    {
      key: 'query_type_id',
      title: 'ID',
    },
    {
      key: 'query_type_name',
      title: 'Name',
    },
    {
      key: 'description',
      title: 'Description',
      render: (value) => value || '-',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Query Types</h2>
        </div>
      </div>

      <div className="w-[50%]">
        <DataTable
          title=""
          data={queryTypes}
          columns={columns}
          loading={isLoading}
          searchable={false}
        />
      </div>

    </div>
  );
}
