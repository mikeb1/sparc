import { describe, it, expect, beforeEach } from 'vitest';
import { ProjectService } from '../../src/services/ProjectService.js';

describe('ProjectService', () => {
  let projectService;
  
  beforeEach(() => {
    projectService = new ProjectService();
  });

  it('should create a new project', () => {
    const projectData = {
      name: 'Test Solar Plant',
      type: 'IMPLEMENTATION',
      location: 'Test Location',
      startDate: new Date('2024-01-01')
    };

    const project = projectService.createProject(projectData);

    expect(project.name).toBe(projectData.name);
    expect(projectService.getProject(project.id)).toBe(project);
  });

  it('should update an existing project', () => {
    const project = projectService.createProject({
      name: 'Test Solar Plant',
      type: 'IMPLEMENTATION',
      location: 'Test Location',
      startDate: new Date('2024-01-01')
    });

    const updates = {
      name: 'Updated Solar Plant',
      status: 'IN_PROGRESS'
    };

    const updatedProject = projectService.updateProject(project.id, updates);

    expect(updatedProject.name).toBe(updates.name);
    expect(updatedProject.status).toBe(updates.status);
  });

  it('should list projects with filters', () => {
    projectService.createProject({
      name: 'Project 1',
      type: 'IMPLEMENTATION',
      status: 'PLANNING',
      location: 'Location 1',
      startDate: new Date()
    });

    projectService.createProject({
      name: 'Project 2',
      type: 'TRANSMISSION_LINE',
      status: 'IN_PROGRESS',
      location: 'Location 2',
      startDate: new Date()
    });

    const implementationProjects = projectService.listProjects({ type: 'IMPLEMENTATION' });
    expect(implementationProjects.length).toBe(1);
    expect(implementationProjects[0].name).toBe('Project 1');

    const inProgressProjects = projectService.listProjects({ status: 'IN_PROGRESS' });
    expect(inProgressProjects.length).toBe(1);
    expect(inProgressProjects[0].name).toBe('Project 2');
  });
});
