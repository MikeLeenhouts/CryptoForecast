import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import DataTable from '@/components/DataTable';
import { querySchedulesApi, schedulesApi, queryTypesApi } from '@/services/api';
import type { QuerySchedule, QueryScheduleForm, Schedule, QueryType, TableColumn } from '@/types';

export default function QuerySchedulesPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<QuerySchedule | null>(null);
  const [formData, setFormData] = useState<QueryScheduleForm>({
    schedule_id: 0,
    query_type_id: 0,
    delay_hours: 0,
    paired_followup_delay_hours: undefined,
  });

  const queryClient = useQueryClient();

  // Fetch query schedules
  const { data: querySchedules = [], isLoading } = useQuery({
    queryKey: ['querySchedules'],
    queryFn: async () => {
      const response = await querySchedulesApi.getAll();
      return response.data;
    },
  });

  // Fetch related data for dropdowns
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

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: QueryScheduleForm) => querySchedulesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['querySchedules'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: QueryScheduleForm }) =>
      querySchedulesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['querySchedules'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => querySchedulesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['querySchedules'] });
    },
  });

  const resetForm = () => {
    setFormData({
      schedule_id: 0,
      query_type_id: 0,
      delay_hours: 0,
      paired_followup_delay_hours: undefined,
    });
    setEditingItem(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.query_schedule_id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (item: QuerySchedule) => {
    setEditingItem(item);
    setFormData({
      schedule_id: item.schedule_id,
      query_type_id: item.query_type_id,
      delay_hours: item.delay_hours,
      paired_followup_delay_hours: item.paired_followup_delay_hours,
    });
    setIsDialogOpen(true);
  };

  const handleDelete = (item: QuerySchedule) => {
    if (confirm('Are you sure you want to delete this query schedule?')) {
      deleteMutation.mutate(item.query_schedule_id);
    }
  };

  const handleAdd = () => {
    resetForm();
    setIsDialogOpen(true);
  };

  const columns: TableColumn<QuerySchedule>[] = [
    {
      key: 'schedule_id_raw' as keyof QuerySchedule,
      title: 'Schedule ID',
      render: (value, record) => record.schedule_id,
    },
    {
      key: 'query_schedule_id',
      title: 'Query ID',
    },
    {
      key: 'schedule_id',
      title: 'Schedule',
      render: (value) => {
        const schedule = schedules.find((s: Schedule) => s.schedule_id === value);
        return schedule ? schedule.schedule_name : `Schedule ${value}`;
      },
    },
    {
      key: 'query_type_id',
      title: 'Query Type',
      render: (value) => {
        const queryType = queryTypes.find((qt: QueryType) => qt.query_type_id === value);
        return queryType ? queryType.query_type_name : `Type ${value}`;
      },
    },
    {
      key: 'delay_hours',
      title: 'Query Delay (Hours)',
    },
    {
      key: 'paired_followup_delay_hours',
      title: 'Forecast Delay (Hours)',
      render: (value) => value || '-',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Query Schedules</h2>
        </div>
      </div>

      <div className="w-[80%]">
        <DataTable
          title="Query Schedules"
          data={querySchedules}
          columns={columns}
          loading={isLoading}
          onAdd={handleAdd}
          onEdit={handleEdit}
          onDelete={handleDelete}
          searchPlaceholder="Search query schedules..."
        />
      </div>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="w-full max-w-[50%]">
          <DialogHeader className="pb-4">
            <DialogTitle className="text-2xl font-bold text-gray-900">
              {editingItem ? 'Edit Query Schedule' : 'Add New Query Schedule'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="schedule_id" className="text-sm font-medium text-gray-700">
                  Schedule *
                </Label>
                <Select
                  value={formData.schedule_id.toString()}
                  onValueChange={(value) =>
                    setFormData({ ...formData, schedule_id: parseInt(value) })
                  }
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select schedule" />
                  </SelectTrigger>
                  <SelectContent>
                    {schedules.map((schedule: Schedule) => (
                      <SelectItem key={schedule.schedule_id} value={schedule.schedule_id.toString()}>
                        {schedule.schedule_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="query_type_id" className="text-sm font-medium text-gray-700">
                  Query Type *
                </Label>
                <Select
                  value={formData.query_type_id.toString()}
                  onValueChange={(value) =>
                    setFormData({ ...formData, query_type_id: parseInt(value) })
                  }
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select query type" />
                  </SelectTrigger>
                  <SelectContent>
                    {queryTypes.map((queryType: QueryType) => (
                      <SelectItem key={queryType.query_type_id} value={queryType.query_type_id.toString()}>
                        {queryType.query_type_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="delay_hours" className="text-sm font-medium text-gray-700">
                  Delay Hours *
                </Label>
                <Input
                  id="delay_hours"
                  type="number"
                  value={formData.delay_hours}
                  onChange={(e) =>
                    setFormData({ ...formData, delay_hours: parseInt(e.target.value) || 0 })
                  }
                  placeholder="0"
                  min="0"
                  required
                  className="mt-1"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="paired_followup_delay_hours" className="text-sm font-medium text-gray-700">
                  Paired Followup Delay Hours
                </Label>
                <Input
                  id="paired_followup_delay_hours"
                  type="number"
                  value={formData.paired_followup_delay_hours || ''}
                  onChange={(e) =>
                    setFormData({ 
                      ...formData, 
                      paired_followup_delay_hours: e.target.value ? parseInt(e.target.value) : undefined 
                    })
                  }
                  placeholder="Optional"
                  min="0"
                  className="mt-1"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
              >
                {createMutation.isPending || updateMutation.isPending
                  ? 'Saving...'
                  : editingItem
                  ? 'Update'
                  : 'Create'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
