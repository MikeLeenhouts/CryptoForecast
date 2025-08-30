import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import DataTable from '@/components/DataTable';
import { queryTypesApi } from '@/services/api';
import type { QueryType, QueryTypeForm, TableColumn } from '@/types';

export default function QueryTypesPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<QueryType | null>(null);
  const [formData, setFormData] = useState<QueryTypeForm>({
    query_type_name: '',
    description: '',
  });

  const queryClient = useQueryClient();

  // Fetch query types
  const { data: queryTypes = [], isLoading } = useQuery({
    queryKey: ['queryTypes'],
    queryFn: async () => {
      const response = await queryTypesApi.getAll();
      return response.data;
    },
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: QueryTypeForm) => queryTypesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['queryTypes'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: QueryTypeForm }) =>
      queryTypesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['queryTypes'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => queryTypesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['queryTypes'] });
    },
  });

  const resetForm = () => {
    setFormData({
      query_type_name: '',
      description: '',
    });
    setEditingItem(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.query_type_id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (item: QueryType) => {
    setEditingItem(item);
    setFormData({
      query_type_name: item.query_type_name,
      description: item.description || '',
    });
    setIsDialogOpen(true);
  };

  const handleDelete = (item: QueryType) => {
    if (confirm('Are you sure you want to delete this query type?')) {
      deleteMutation.mutate(item.query_type_id);
    }
  };

  const handleAdd = () => {
    resetForm();
    setIsDialogOpen(true);
  };

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
          <p className="text-gray-600 mt-2">Manage different types of queries for crypto forecasting</p>
        </div>
      </div>

      <DataTable
        title="Query Types"
        data={queryTypes}
        columns={columns}
        loading={isLoading}
        onAdd={handleAdd}
        onEdit={handleEdit}
        onDelete={handleDelete}
        searchPlaceholder="Search query types..."
      />

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="w-full max-w-[50%]">
          <DialogHeader className="pb-4">
            <DialogTitle className="text-2xl font-bold text-gray-900">
              {editingItem ? 'Edit Query Type' : 'Add New Query Type'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="query_type_name" className="text-sm font-medium text-gray-700">
                Query Type Name *
              </Label>
              <Input
                id="query_type_name"
                value={formData.query_type_name}
                onChange={(e) =>
                  setFormData({ ...formData, query_type_name: e.target.value })
                }
                placeholder="e.g., Initial, OneHour, FourHour"
                required
                className="mt-1"
              />
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
                placeholder="Describe the purpose and timing of this query type..."
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
