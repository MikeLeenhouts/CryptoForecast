import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { reportsApi } from '@/services/api';
import DataTable from '@/components/DataTable';
import type { Report, TableColumn } from '@/types';

export default function ReportsPage() {
  // Fetch reports
  const { data: reports = [], isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: async () => {
      const response = await reportsApi.getAll();
      return response.data;
    },
  });

  const columns: TableColumn<Report>[] = [
    {
      key: 'id',
      title: 'ID',
    },
    {
      key: 'name',
      title: 'Name',
    },
    {
      key: 'query_id',
      title: 'Query ID',
    },
    {
      key: 'created_at',
      title: 'Created At',
    },
  ];

  const handleView = (report: Report) => {
    // Open report data in a modal or new page
    console.log('Viewing report:', report);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">Reports</h2>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{reports.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Recent Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {reports.filter(r => {
                const createdAt = new Date(r.created_at);
                const dayAgo = new Date();
                dayAgo.setDate(dayAgo.getDate() - 1);
                return createdAt > dayAgo;
              }).length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">This Week</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {reports.filter(r => {
                const createdAt = new Date(r.created_at);
                const weekAgo = new Date();
                weekAgo.setDate(weekAgo.getDate() - 7);
                return createdAt > weekAgo;
              }).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Reports Table */}
      <DataTable
        title="Generated Reports"
        data={reports}
        columns={columns}
        loading={isLoading}
        onView={handleView}
        searchPlaceholder="Search reports..."
      />
    </div>
  );
}
