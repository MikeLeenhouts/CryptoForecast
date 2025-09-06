import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import DataTable from '@/components/DataTable';
import { surveysApi, assetsApi, schedulesApi, promptsApi, llmsApi } from '@/services/api';
import type { Survey, SurveyForm, Asset, Schedule, Prompt, LLM, TableColumn } from '@/types';

export default function SurveysPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Survey | null>(null);
  const [formData, setFormData] = useState<SurveyForm>({
    asset_id: 0,
    schedule_id: 0,
    prompt_id: 0,
    is_active: true,
  });

  const queryClient = useQueryClient();

  // Fetch surveys
  const { data: surveys = [], isLoading } = useQuery({
    queryKey: ['surveys'],
    queryFn: async () => {
      const response = await surveysApi.getAll();
      return response.data;
    },
  });

  // Fetch related data for dropdowns
  const { data: assets = [] } = useQuery({
    queryKey: ['assets'],
    queryFn: async () => {
      const response = await assetsApi.getAll();
      return response.data;
    },
  });

  const { data: schedules = [] } = useQuery({
    queryKey: ['schedules'],
    queryFn: async () => {
      try {
        const response = await schedulesApi.getAll();
        return response.data;
      } catch (error) {
        console.error('Failed to fetch schedules:', error);
        return [];
      }
    },
  });

  const { data: prompts = [] } = useQuery({
    queryKey: ['prompts'],
    queryFn: async () => {
      const response = await promptsApi.getAll();
      return response.data;
    },
  });

  const { data: llms = [] } = useQuery({
    queryKey: ['llms'],
    queryFn: async () => {
      const response = await llmsApi.getAll();
      return response.data;
    },
  });


  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: SurveyForm) => surveysApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['surveys'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: SurveyForm }) =>
      surveysApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['surveys'] });
      setIsDialogOpen(false);
      resetForm();
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => surveysApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['surveys'] });
    },
  });

  const resetForm = () => {
    setFormData({
      asset_id: 0,
      schedule_id: 0,
      prompt_id: 0,
      is_active: true,
    });
    setEditingItem(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.survey_id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (item: Survey) => {
    setEditingItem(item);
    setFormData({
      asset_id: item.asset_id,
      schedule_id: item.schedule_id,
      prompt_id: item.prompt_id,
      is_active: item.is_active,
    });
    setIsDialogOpen(true);
  };

  const handleDelete = (item: Survey) => {
    if (confirm('Are you sure you want to delete this survey?')) {
      deleteMutation.mutate(item.survey_id);
    }
  };

  const handleAdd = () => {
    resetForm();
    setIsDialogOpen(true);
  };

  const columns: TableColumn<Survey>[] = [
    {
      key: 'survey_id',
      title: 'ID',
    },
    {
      key: 'asset_id',
      title: 'Asset',
      render: (value) => {
        const asset = assets.find((a: Asset) => a.asset_id === value);
        return asset ? asset.asset_name : 'Unknown';
      },
    },
    {
      key: 'llm_name' as keyof Survey,
      title: 'LLM',
      render: (value, record) => {
        const prompt = prompts.find((p: Prompt) => p.prompt_id === record.prompt_id);
        if (prompt) {
          const llm = llms.find((l: LLM) => l.llm_id === prompt.llm_id);
          return llm ? llm.llm_name : 'Unknown LLM';
        }
        return 'Unknown';
      },
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
      key: 'prompt_id',
      title: 'Prompt ID',
      render: (value) => {
        return value;
      },
    },
    {
      key: 'prompt_version' as keyof Survey,
      title: 'Version',
      render: (value, record) => {
        const prompt = prompts.find((p: Prompt) => p.prompt_id === record.prompt_id);
        return prompt ? `v${prompt.prompt_version}` : 'Unknown';
      },
    },
    {
      key: 'is_active',
      title: 'Status',
      render: (value) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          value 
            ? 'bg-green-100 text-green-800' 
            : 'bg-red-100 text-red-800'
        }`}>
          {value ? 'Active' : 'Inactive'}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Surveys</h2>
        </div>
      </div>

      <div className="w-[80%]">
        <DataTable
          title="Crypto Surveys"
          data={surveys}
          columns={columns}
          loading={isLoading}
          onAdd={handleAdd}
          onEdit={handleEdit}
          onDelete={handleDelete}
          searchPlaceholder="Search surveys..."
        />
      </div>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="w-full max-w-[50%]">
          <DialogHeader className="pb-4">
            <DialogTitle className="text-2xl font-bold text-gray-900">
              {editingItem ? 'Edit Survey' : 'Add New Survey'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="asset_id" className="text-sm font-medium text-gray-700">
                  Asset *
                </Label>
                <Select
                  value={formData.asset_id.toString()}
                  onValueChange={(value) =>
                    setFormData({ ...formData, asset_id: parseInt(value) })
                  }
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select asset" />
                  </SelectTrigger>
                  <SelectContent>
                    {assets.map((asset: Asset) => (
                      <SelectItem key={asset.asset_id} value={asset.asset_id.toString()}>
                        {asset.asset_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
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
            </div>
            <div className="space-y-2">
              <Label htmlFor="prompt_id" className="text-sm font-medium text-gray-700">
                Prompt *
              </Label>
              <Select
                value={formData.prompt_id.toString()}
                onValueChange={(value) =>
                  setFormData({ ...formData, prompt_id: parseInt(value) })
                }
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select prompt" />
                </SelectTrigger>
                <SelectContent>
                  {prompts.map((prompt: Prompt) => (
                    <SelectItem key={prompt.prompt_id} value={prompt.prompt_id.toString()}>
                      Prompt {prompt.prompt_id} (v{prompt.prompt_version})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="is_active" className="text-sm font-medium text-gray-700">
                Status
              </Label>
              <Select
                value={formData.is_active?.toString() || 'true'}
                onValueChange={(value) =>
                  setFormData({ ...formData, is_active: value === 'true' })
                }
              >
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="true">Active</SelectItem>
                  <SelectItem value="false">Inactive</SelectItem>
                </SelectContent>
              </Select>
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
