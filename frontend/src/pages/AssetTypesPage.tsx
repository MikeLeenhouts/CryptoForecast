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
    asset_type_name: '',
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
    setFormData({ asset_type_name: '', description: '' });
    setEditingItem(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.asset_type_id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (item: AssetType) => {
    setEditingItem(item);
    setFormData({
      asset_type_name: item.asset_type_name,
      description: item.description || '',
    });
    setIsDialogOpen(true);
  };

  const handleDelete = (item: AssetType) => {
    if (confirm('Are you sure you want to delete this asset type?')) {
      deleteMutation.mutate(item.asset_type_id);
    }
  };

  const handleAdd = () => {
    resetForm();
    setIsDialogOpen(true);
  };

  const columns: TableColumn<AssetType>[] = [
    {
      key: 'asset_type_id',
      title: 'ID',
    },
    {
      key: 'asset_type_name',
      title: 'Name',
    },
    {
      key: 'description',
      title: 'Description',
      render: (value) => value || '-',
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Asset Types</h2>
      </div>

      <div className="w-[70%]">
        <DataTable
          title=""
          data={assetTypes}
          columns={columns}
          loading={isLoading}
          onAdd={handleAdd}
          onEdit={handleEdit}
          onDelete={handleDelete}
          searchable={false}
        />
      </div>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="w-full max-w-[50%]">
          <DialogHeader className="pb-4">
            <DialogTitle className="text-2xl font-bold text-gray-900">
              {editingItem ? 'Edit Asset Type' : 'Add New Asset Type'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="asset_type_name" className="text-sm font-medium text-gray-700">
                Name *
              </Label>
              <Input
                id="asset_type_name"
                value={formData.asset_type_name}
                onChange={(e) =>
                  setFormData({ ...formData, asset_type_name: e.target.value })
                }
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
