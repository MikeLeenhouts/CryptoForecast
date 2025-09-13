import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import DataTable from '@/components/DataTable';
import { assetsApi, assetTypesApi } from '@/services/api';
import type { Asset, AssetForm, AssetType, TableColumn } from '@/types';

export default function AssetsPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Asset | null>(null);
  const [formData, setFormData] = useState<AssetForm>({
    asset_name: '',
    asset_symbol: '',
    description: '',
    asset_type_id: 0,
  });

  const queryClient = useQueryClient();

  // Fetch assets
  const { data: assets = [], isLoading } = useQuery({
    queryKey: ['assets'],
    queryFn: async () => {
      const response = await assetsApi.getAll();
      return response.data;
    },
  });

  // Fetch asset types for dropdown
  const { data: assetTypes = [] } = useQuery({
    queryKey: ['assetTypes'],
    queryFn: async () => {
      const response = await assetTypesApi.getAll();
      return response.data;
    },
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: AssetForm) => assetsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: AssetForm }) =>
      assetsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => assetsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] });
    },
  });

  const resetForm = () => {
    setFormData({ asset_name: '', asset_symbol: '', description: '', asset_type_id: 0 });
    setEditingItem(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.asset_id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (item: Asset) => {
    setEditingItem(item);
    setFormData({
      asset_name: item.asset_name,
      asset_symbol: item.asset_symbol,
      description: item.description || '',
      asset_type_id: item.asset_type_id,
    });
    setIsDialogOpen(true);
  };

  const handleDelete = (item: Asset) => {
    if (confirm('Are you sure you want to delete this asset?')) {
      deleteMutation.mutate(item.asset_id);
    }
  };

  const handleAdd = () => {
    resetForm();
    setIsDialogOpen(true);
  };

  const columns: TableColumn<Asset>[] = [
    {
      key: 'asset_id',
      title: 'ID',
    },
    {
      key: 'asset_name',
      title: 'Name',
    },
    {
      key: 'asset_symbol',
      title: 'Symbol',
    },
    {
      key: 'asset_type_id',
      title: 'Asset Type',
      render: (value) => {
        const assetType = assetTypes.find((type: AssetType) => type.asset_type_id === value);
        return assetType ? assetType.asset_type_name : 'Unknown';
      },
    },
    {
      key: 'description',
      title: 'Description',
      render: (value) => value || '-',
    },
  ];

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Assets</h2>
      </div>

      <div className="w-[80%]">
        <DataTable
          title=""
          data={assets}
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
              {editingItem ? 'Edit Asset' : 'Add New Asset'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="asset_name" className="text-sm font-medium text-gray-700">
                Name *
              </Label>
              <Input
                id="asset_name"
                value={formData.asset_name}
                onChange={(e) =>
                  setFormData({ ...formData, asset_name: e.target.value })
                }
                required
                className="mt-1"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="asset_symbol" className="text-sm font-medium text-gray-700">
                Symbol *
              </Label>
              <Input
                id="asset_symbol"
                value={formData.asset_symbol}
                onChange={(e) =>
                  setFormData({ ...formData, asset_symbol: e.target.value })
                }
                required
                className="mt-1"
                placeholder="e.g., BTC-USD, ETH-USD, GC=F"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="asset_type_id" className="text-sm font-medium text-gray-700">
                Asset Type *
              </Label>
              <Select
                value={formData.asset_type_id.toString()}
                onValueChange={(value) =>
                  setFormData({ ...formData, asset_type_id: parseInt(value) })
                }
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select asset type" />
                </SelectTrigger>
                <SelectContent>
                  {assetTypes.map((type: AssetType) => (
                    <SelectItem key={type.asset_type_id} value={type.asset_type_id.toString()}>
                      {type.asset_type_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
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
