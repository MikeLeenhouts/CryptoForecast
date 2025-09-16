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
import type { Prompt, PromptForm, LLM, TableColumn, PromptType } from '@/types';

export default function PromptsPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Prompt | null>(null);
  const [formData, setFormData] = useState<PromptForm>({
    llm_id: 0,
    prompt_name: '',
    prompt_text: '',
    followup_llm: 0,
    prompt_type: 'live',
    attribute_1: '',
    attribute_2: '',
    attribute_3: '',
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
    setFormData({ 
      llm_id: 0, 
      prompt_name: '', 
      prompt_text: '', 
      followup_llm: 0, 
      prompt_type: 'live',
      attribute_1: '', 
      attribute_2: '', 
      attribute_3: '', 
      prompt_version: 1 
    });
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
      prompt_name: item.prompt_name || '',
      prompt_text: item.prompt_text,
      followup_llm: item.followup_llm,
      prompt_type: item.prompt_type,
      attribute_1: item.attribute_1 || '',
      attribute_2: item.attribute_2 || '',
      attribute_3: item.attribute_3 || '',
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
      key: 'prompt_name',
      title: 'Prompt Name',
      render: (value) => {
        return value ? <span className="font-medium">{String(value)}</span> : <span className="text-gray-400 italic">No name</span>;
      },
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
      key: 'followup_llm',
      title: 'Followup LLM',
      render: (value) => {
        if (!value) return <span className="text-gray-400 italic">None</span>;
        const llm = llms.find((l: LLM) => l.llm_id === value);
        return llm ? llm.llm_name : 'Unknown';
      },
    },
    {
      key: 'prompt_type',
      title: 'Type',
      render: (value) => {
        const type = String(value);
        return (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            type === 'live' 
              ? 'bg-green-100 text-green-800' 
              : 'bg-blue-100 text-blue-800'
          }`}>
            {type === 'live' ? 'Live' : 'Forecast'}
          </span>
        );
      },
    },
    {
      key: 'attribute_1',
      title: 'Attribute 1',
      render: (value) => {
        if (!value) return <span className="text-gray-400 italic">None</span>;
        const text = String(value);
        const preview = text.length > 20 ? text.substring(0, 20) + '...' : text;
        return <span className="text-sm text-gray-600">{preview}</span>;
      },
    },
    {
      key: 'attribute_2',
      title: 'Attribute 2',
      render: (value) => {
        if (!value) return <span className="text-gray-400 italic">None</span>;
        const text = String(value);
        const preview = text.length > 20 ? text.substring(0, 20) + '...' : text;
        return <span className="text-sm text-gray-600">{preview}</span>;
      },
    },
    {
      key: 'attribute_3',
      title: 'Attribute 3',
      render: (value) => {
        if (!value) return <span className="text-gray-400 italic">None</span>;
        const text = String(value);
        const preview = text.length > 20 ? text.substring(0, 20) + '...' : text;
        return <span className="text-sm text-gray-600">{preview}</span>;
      },
    },
    {
      key: 'prompt_text',
      title: 'Content Preview',
      render: (value) => {
        const text = String(value);
        const preview = text.length > 50 ? text.substring(0, 50) + '...' : text;
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

      <div className="w-[90%]">
        <DataTable
          title=""
          data={prompts}
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
              <Label htmlFor="prompt_name" className="text-sm font-medium text-gray-700">
                Prompt Name
              </Label>
              <Input
                id="prompt_name"
                value={formData.prompt_name || ''}
                onChange={(e) =>
                  setFormData({ ...formData, prompt_name: e.target.value })
                }
                placeholder="Enter a descriptive name for this prompt..."
                className="mt-1"
              />
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
                rows={6}
                placeholder="Enter the AI prompt content here..."
                required
                className="mt-1"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="followup_llm" className="text-sm font-medium text-gray-700">
                Follow-up LLM *
              </Label>
              <Select
                value={formData.followup_llm.toString()}
                onValueChange={(value) =>
                  setFormData({ ...formData, followup_llm: parseInt(value) })
                }
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select Follow-up LLM" />
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
              <Label htmlFor="prompt_type" className="text-sm font-medium text-gray-700">
                Prompt Type *
              </Label>
              <Select
                value={formData.prompt_type}
                onValueChange={(value: PromptType) =>
                  setFormData({ ...formData, prompt_type: value })
                }
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select Prompt Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="live">Live - Real-time Analysis</SelectItem>
                  <SelectItem value="forecast">Forecast - Predictive Analysis</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="attribute_1" className="text-sm font-medium text-gray-700">
                  Attribute 1
                </Label>
                <Textarea
                  id="attribute_1"
                  value={formData.attribute_1 || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, attribute_1: e.target.value })
                  }
                  rows={3}
                  placeholder="Custom attribute 1..."
                  className="mt-1"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="attribute_2" className="text-sm font-medium text-gray-700">
                  Attribute 2
                </Label>
                <Textarea
                  id="attribute_2"
                  value={formData.attribute_2 || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, attribute_2: e.target.value })
                  }
                  rows={3}
                  placeholder="Custom attribute 2..."
                  className="mt-1"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="attribute_3" className="text-sm font-medium text-gray-700">
                  Attribute 3
                </Label>
                <Textarea
                  id="attribute_3"
                  value={formData.attribute_3 || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, attribute_3: e.target.value })
                  }
                  rows={3}
                  placeholder="Custom attribute 3..."
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
