import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import DataTable from '@/components/DataTable';
import { assetTypesApi } from '@/services/api';
import type { AssetType, AssetTypeForm, TableColumn } from '@/types';

export default function AssetTypesPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<AssetType | null>(null);
  const [formData, setFormData] = useState<AssetTypeForm>({
    name: '',
    description: '',
  });

  const queryClient = useQueryClient();

  // Fetch asset types
  const { data: assetTypes = [], isLoading } = useQuery({
    queryKey: ['assetTypes'],
    queryFn: async () => {
      const response = await assetTypesApi.getAll();
      return response.data;
    },
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: AssetTypeForm) => assetTypesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assetTypes'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: AssetTypeForm }) =>
      assetTypesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assetTypes'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => assetTypesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assetTypes'] });
    },
  });

  const resetForm = () => {
    setFormData({ name: '', description: '' });
    setEditingItem(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (item: AssetType) => {
    setEditingItem(item);
    setFormData({
      name: item.name,
      description: item.description || '',
    });
    setIsDialogOpen(true);
  };

  const handleDelete = (item: AssetType) => {
    if (confirm('Are you sure you want to delete this asset type?')) {
      deleteMutation.mutate(item.id);
    }
  };

  const handleAdd = () => {
    resetForm();
    setIsDialogOpen(true);
  };

  const columns: TableColumn<AssetType>[] = [
    {
      key: 'id',
      title: 'ID',
    },
    {
      key: 'name',
      title: 'Name',
    },
    {
      key: 'description',
      title: 'Description',
      render: (value) => value || '-',
    },
    {
      key: 'created_at',
      title: 'Created At',
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Asset Types</h2>
      </div>

      <DataTable
        title="Asset Types"
        data={assetTypes}
        columns={columns}
        loading={isLoading}
        onAdd={handleAdd}
        onEdit={handleEdit}
        onDelete={handleDelete}
        searchPlaceholder="Search asset types..."
      />

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingItem ? 'Edit Asset Type' : 'Add New Asset Type'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                rows={3}
              />
            </div>
            <div className="flex justify-end space-x-2">
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
