import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { Project } from '@/lib/types';

interface ProjectFormProps {
  onSubmit: (data: Partial<Project>) => void;
  initialData?: Partial<Project>;
}

export function ProjectForm({ onSubmit, initialData }: ProjectFormProps) {
  const formatDateForInput = (date: Date | undefined) => {
    if (!date) return '';
    const d = new Date(date);
    return d.toISOString().split('T')[0];
  };

  const [formData, setFormData] = useState({
    name: initialData?.name || '',
    type: initialData?.type || 'IMPLEMENTATION',
    location: initialData?.location || '',
    startDate: formatDateForInput(initialData?.startDate),
    status: initialData?.status || 'PLANNING'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const [year, month, day] = formData.startDate.split('-').map(Number);
    onSubmit({
      ...formData,
      startDate: new Date(year, month - 1, day) // month is 0-based in JS Date
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <label htmlFor="name" className="text-sm font-medium">Project Name</label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="type" className="text-sm font-medium">Project Type</label>
        <Select
          value={formData.type}
          onValueChange={(value) => setFormData({ ...formData, type: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="IMPLEMENTATION">Implementation</SelectItem>
            <SelectItem value="TRANSMISSION">Transmission</SelectItem>
            <SelectItem value="SUBSTATION">Substation</SelectItem>
            <SelectItem value="TEDAS">TEDAS Approval</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <label htmlFor="location" className="text-sm font-medium">Location</label>
        <Input
          id="location"
          value={formData.location}
          onChange={(e) => setFormData({ ...formData, location: e.target.value })}
          required
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="startDate" className="text-sm font-medium">Start Date</label>
        <Input
          id="startDate"
          type="date"
          value={formData.startDate}
          onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
          required
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="status" className="text-sm font-medium">Status</label>
        <Select
          value={formData.status}
          onValueChange={(value) => setFormData({ ...formData, status: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="PLANNING">Planning</SelectItem>
            <SelectItem value="IN_PROGRESS">In Progress</SelectItem>
            <SelectItem value="COMPLETED">Completed</SelectItem>
            <SelectItem value="ON_HOLD">On Hold</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Button type="submit" className="w-full">
        {initialData ? 'Update Project' : 'Create Project'}
      </Button>
    </form>
  );
}
