import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import DataTable from '@/components/DataTable';
import { promptsApi, llmsApi } from '@/services/api';
import type { Prompt, PromptForm, LLM, TableColumn } from '@/types';

export default function PromptsPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Prompt | null>(null);
  const [formData, setFormData] = useState<PromptForm>({
    llm_id: 0,
    prompt_text: '',
    prompt_version: 1,
  });

  const queryClient = useQueryClient();

  // Fetch prompts
  const { data: prompts = [], isLoading } = useQuery({
    queryKey: ['prompts'],
    queryFn: async () => {
      const response = await promptsApi.getAll();
      return response.data;
    },
  });

  // Fetch LLMs for dropdown
  const { data: llms = [] } = useQuery({
    queryKey: ['llms'],
    queryFn: async () => {
      const response = await llmsApi.getAll();
      return response.data;
    },
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: PromptForm) => promptsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: PromptForm }) =>
      promptsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => promptsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts'] });
    },
  });

  const resetForm = () => {
    setFormData({ llm_id: 0, prompt_text: '', prompt_version: 1 });
    setEditingItem(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.prompt_id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (item: Prompt) => {
    setEditingItem(item);
    setFormData({
      llm_id: item.llm_id,
      prompt_text: item.prompt_text,
      prompt_version: item.prompt_version,
    });
    setIsDialogOpen(true);
  };

  const handleDelete = (item: Prompt) => {
    if (confirm('Are you sure you want to delete this prompt?')) {
      deleteMutation.mutate(item.prompt_id);
    }
  };

  const handleAdd = () => {
    resetForm();
    setIsDialogOpen(true);
  };

  const columns: TableColumn<Prompt>[] = [
    {
      key: 'prompt_id',
      title: 'ID',
    },
    {
      key: 'llm_id',
      title: 'LLM',
      render: (value) => {
        const llm = llms.find((l: LLM) => l.llm_id === value);
        return llm ? llm.llm_name : 'Unknown';
      },
    },
    {
      key: 'prompt_text',
      title: 'Content Preview',
      render: (value) => {
        const text = String(value);
        const preview = text.length > 100 ? text.substring(0, 100) + '...' : text;
        return <span className="text-sm text-gray-600">{preview}</span>;
      },
    },
    {
      key: 'prompt_version',
      title: 'Version',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Prompts</h2>
        </div>
      </div>

      <DataTable
        title="AI Prompts"
        data={prompts}
        columns={columns}
        loading={isLoading}
        onAdd={handleAdd}
        onEdit={handleEdit}
        onDelete={handleDelete}
        searchPlaceholder="Search prompts..."
      />

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="w-full max-w-[50%]">
          <DialogHeader className="pb-4">
            <DialogTitle className="text-2xl font-bold text-gray-900">
              {editingItem ? 'Edit Prompt' : 'Add New Prompt'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="llm_id" className="text-sm font-medium text-gray-700">
                  LLM *
                </Label>
                <Select
                  value={formData.llm_id.toString()}
                  onValueChange={(value) =>
                    setFormData({ ...formData, llm_id: parseInt(value) })
                  }
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select LLM" />
                  </SelectTrigger>
                  <SelectContent>
                    {llms.map((llm: LLM) => (
                      <SelectItem key={llm.llm_id} value={llm.llm_id.toString()}>
                        {llm.llm_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="prompt_version" className="text-sm font-medium text-gray-700">
                  Version
                </Label>
                <Input
                  id="prompt_version"
                  type="number"
                  value={formData.prompt_version}
                  onChange={(e) =>
                    setFormData({ ...formData, prompt_version: parseInt(e.target.value) || 1 })
                  }
                  placeholder="1"
                  min="1"
                  className="mt-1"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="prompt_text" className="text-sm font-medium text-gray-700">
                Prompt Text *
              </Label>
              <Textarea
                id="prompt_text"
                value={formData.prompt_text}
                onChange={(e) =>
                  setFormData({ ...formData, prompt_text: e.target.value })
                }
                rows={8}
                placeholder="Enter the AI prompt content here..."
                required
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
