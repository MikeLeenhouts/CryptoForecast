import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import DataTable from '@/components/DataTable';
import { schedulesApi } from '@/services/api';
import type { Schedule, ScheduleForm, TableColumn } from '@/types';

export default function SchedulesPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Schedule | null>(null);
  const [formData, setFormData] = useState<ScheduleForm>({
    schedule_name: '',
    schedule_version: 1,
    initial_query_time: '',
    timezone: 'UTC',
    description: '',
  });

  const queryClient = useQueryClient();

  // Fetch schedules
  const { data: schedules = [], isLoading } = useQuery({
    queryKey: ['schedules'],
    queryFn: async () => {
      const response = await schedulesApi.getAll();
      return response.data;
    },
  });


  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: ScheduleForm) => schedulesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ScheduleForm }) =>
      schedulesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => schedulesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
    },
  });

  const resetForm = () => {
    setFormData({
      schedule_name: '',
      schedule_version: 1,
      initial_query_time: '',
      timezone: 'UTC',
      description: '',
    });
    setEditingItem(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.schedule_id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (item: Schedule) => {
    setEditingItem(item);
    setFormData({
      schedule_name: item.schedule_name,
      schedule_version: item.schedule_version,
      initial_query_time: item.initial_query_time,
      timezone: item.timezone,
      description: item.description || '',
    });
    setIsDialogOpen(true);
  };

  const handleDelete = (item: Schedule) => {
    if (confirm('Are you sure you want to delete this schedule?')) {
      deleteMutation.mutate(item.schedule_id);
    }
  };

  const handleAdd = () => {
    resetForm();
    setIsDialogOpen(true);
  };

  const columns: TableColumn<Schedule>[] = [
    {
      key: 'schedule_id',
      title: 'ID',
    },
    {
      key: 'schedule_name',
      title: 'Name',
    },
    {
      key: 'schedule_version',
      title: 'Version',
    },
    {
      key: 'initial_query_time',
      title: 'Query Time',
    },
    {
      key: 'timezone',
      title: 'Timezone',
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
          <h2 className="text-3xl font-bold">Schedules</h2>
          <p className="text-gray-600 mt-2">Manage automated survey execution schedules</p>
        </div>
      </div>

      <DataTable
        title="Survey Schedules"
        data={schedules}
        columns={columns}
        loading={isLoading}
        onAdd={handleAdd}
        onEdit={handleEdit}
        onDelete={handleDelete}
        searchPlaceholder="Search schedules..."
      />

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="w-full max-w-[50%]">
          <DialogHeader className="pb-4">
            <DialogTitle className="text-2xl font-bold text-gray-900">
              {editingItem ? 'Edit Schedule' : 'Add New Schedule'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="schedule_name" className="text-sm font-medium text-gray-700">
                  Schedule Name *
                </Label>
                <Input
                  id="schedule_name"
                  value={formData.schedule_name}
                  onChange={(e) =>
                    setFormData({ ...formData, schedule_name: e.target.value })
                  }
                  placeholder="e.g., Daily Bitcoin Analysis"
                  required
                  className="mt-1"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="schedule_version" className="text-sm font-medium text-gray-700">
                  Version
                </Label>
                <Input
                  id="schedule_version"
                  type="number"
                  value={formData.schedule_version}
                  onChange={(e) =>
                    setFormData({ ...formData, schedule_version: parseInt(e.target.value) || 1 })
                  }
                  placeholder="1"
                  min="1"
                  className="mt-1"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="initial_query_time" className="text-sm font-medium text-gray-700">
                  Initial Query Time *
                </Label>
                <Input
                  id="initial_query_time"
                  type="time"
                  value={formData.initial_query_time}
                  onChange={(e) =>
                    setFormData({ ...formData, initial_query_time: e.target.value })
                  }
                  required
                  className="mt-1"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="timezone" className="text-sm font-medium text-gray-700">
                  Timezone
                </Label>
                <Input
                  id="timezone"
                  value={formData.timezone}
                  onChange={(e) =>
                    setFormData({ ...formData, timezone: e.target.value })
                  }
                  placeholder="UTC"
                  className="mt-1"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="description" className="text-sm font-medium text-gray-700">
                Description
              </Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                rows={3}
                placeholder="Describe the schedule purpose and configuration..."
                className="mt-1"
              />
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
