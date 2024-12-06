'use client';

import { useState, useEffect } from 'react';
import { ProjectService } from '@/lib/services/ProjectService';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { ProjectForm } from "@/components/ProjectForm";
import { PlusCircle, Pencil, Trash2 } from "lucide-react";
import type { Project } from '@/lib/types';

export default function Home() {
  const [projectService] = useState(() => new ProjectService());
  const [projects, setProjects] = useState<Project[]>([]);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  useEffect(() => {
    // Initialize with sample projects
    projectService.createProject({
      name: "Solar Farm Alpha",
      type: "IMPLEMENTATION",
      location: "Desert Valley",
      startDate: new Date("2024-01-01"),
      status: "PLANNING"
    });

    projectService.createProject({
      name: "Wind Farm Beta",
      type: "TRANSMISSION",
      location: "Mountain Ridge",
      startDate: new Date("2024-02-01"),
      status: "PLANNING"
    });

    setProjects(projectService.listProjects());
  }, [projectService]);

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleCreateProject = (data: Partial<Project>) => {
    const newProject = projectService.createProject(data);
    setProjects(projectService.listProjects());
    setIsDialogOpen(false);
  };

  const handleUpdateProject = (data: Partial<Project>) => {
    if (editingProject) {
      projectService.updateProject(editingProject.id, data);
      setProjects(projectService.listProjects());
      setEditingProject(null);
      setIsDialogOpen(false);
    }
  };

  const handleDeleteProject = (id: string) => {
    if (confirm('Are you sure you want to delete this project?')) {
      const updatedProjects = projects.filter(p => p.id !== id);
      setProjects(updatedProjects);
    }
  };

  const openEditDialog = (project: Project) => {
    setEditingProject(project);
    setIsDialogOpen(true);
  };

  return (
    <main className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">Solar Power Plant Management</h1>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => setEditingProject(null)}>
              <PlusCircle className="mr-2 h-4 w-4" />
              New Project
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>
                {editingProject ? 'Edit Project' : 'Create New Project'}
              </DialogTitle>
            </DialogHeader>
            <ProjectForm
              onSubmit={editingProject ? handleUpdateProject : handleCreateProject}
              initialData={editingProject || undefined}
            />
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.map((project) => (
          <Card key={project.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>{project.name}</CardTitle>
                  <CardDescription>Type: {project.type}</CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => openEditDialog(project)}
                  >
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDeleteProject(project.id)}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="flex justify-between">
                  <span className="text-muted-foreground">Location:</span>
                  <span className="font-medium">{project.location}</span>
                </p>
                <p className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <span className="font-medium">{project.status}</span>
                </p>
                <p className="flex justify-between">
                  <span className="text-muted-foreground">Start Date:</span>
                  <span className="font-medium">
                    {formatDate(project.startDate)}
                  </span>
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </main>
  );
}
