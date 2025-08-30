import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import DataTable from '@/components/DataTable';
import { llmsApi } from '@/services/api';
import type { LLM, LLMForm, TableColumn } from '@/types';

export default function LLMsPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<LLM | null>(null);
  const [formData, setFormData] = useState<LLMForm>({
    llm_name: '',
    api_url: '',
    api_key_secret: '',
  });

  const queryClient = useQueryClient();

  // Fetch LLMs
  const { data: llms = [], isLoading } = useQuery({
    queryKey: ['llms'],
    queryFn: async () => {
      const response = await llmsApi.getAll();
      return response.data;
    },
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: LLMForm) => llmsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['llms'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: LLMForm }) =>
      llmsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['llms'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => llmsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['llms'] });
    },
  });

  const resetForm = () => {
    setFormData({
      llm_name: '',
      api_url: '',
      api_key_secret: '',
    });
    setEditingItem(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.llm_id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (item: LLM) => {
    setEditingItem(item);
    setFormData({
      llm_name: item.llm_name,
      api_url: item.api_url,
      api_key_secret: item.api_key_secret || '',
    });
    setIsDialogOpen(true);
  };

  const handleDelete = (item: LLM) => {
    if (confirm('Are you sure you want to delete this LLM configuration?')) {
      deleteMutation.mutate(item.llm_id);
    }
  };

  const handleAdd = () => {
    resetForm();
    setIsDialogOpen(true);
  };

  const columns: TableColumn<LLM>[] = [
    {
      key: 'llm_id',
      title: 'ID',
    },
    {
      key: 'llm_name',
      title: 'Name',
    },
    {
      key: 'api_url',
      title: 'API URL',
      render: (value) => value || '-',
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">LLMs</h2>
          <p className="text-gray-600 mt-2">Manage Large Language Model configurations for crypto forecasting</p>
        </div>
      </div>

      <DataTable
        title="LLM Configurations"
        data={llms}
        columns={columns}
        loading={isLoading}
        onAdd={handleAdd}
        onEdit={handleEdit}
        onDelete={handleDelete}
        searchPlaceholder="Search LLM configurations..."
      />

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingItem ? 'Edit LLM Configuration' : 'Add New LLM Configuration'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="llm_name">LLM Name *</Label>
              <Input
                id="llm_name"
                value={formData.llm_name}
                onChange={(e) =>
                  setFormData({ ...formData, llm_name: e.target.value })
                }
                placeholder="e.g., gpt-4o"
                required
              />
            </div>
            <div>
              <Label htmlFor="api_url">API URL *</Label>
              <Input
                id="api_url"
                value={formData.api_url}
                onChange={(e) =>
                  setFormData({ ...formData, api_url: e.target.value })
                }
                placeholder="https://api.openai.com/v1/completions"
                required
              />
            </div>
            <div>
              <Label htmlFor="api_key_secret">API Key Secret *</Label>
              <Input
                id="api_key_secret"
                type="password"
                value={formData.api_key_secret}
                onChange={(e) =>
                  setFormData({ ...formData, api_key_secret: e.target.value })
                }
                placeholder="API key or secret reference"
                required
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
