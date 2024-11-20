import { describe, it, expect } from 'vitest';
import { Project } from '../../src/models/Project.js';

describe('Project', () => {
  it('should create a new project with required fields', () => {
    const projectData = {
      name: 'Test Solar Plant',
      type: 'IMPLEMENTATION',
      location: 'Test Location',
      startDate: new Date('2024-01-01')
    };

    const project = new Project(projectData);

    expect(project.id).toBeDefined();
    expect(project.name).toBe(projectData.name);
    expect(project.type).toBe(projectData.type);
    expect(project.location).toBe(projectData.location);
    expect(project.startDate).toBe(projectData.startDate);
    expect(project.status).toBe('PLANNING');
    expect(project.createdAt).toBeInstanceOf(Date);
    expect(project.updatedAt).toBeInstanceOf(Date);
  });

  it('should update project fields', () => {
    const project = new Project({
      name: 'Test Solar Plant',
      type: 'IMPLEMENTATION',
      location: 'Test Location',
      startDate: new Date('2024-01-01')
    });

    const originalUpdatedAt = project.updatedAt;
    
    // Wait a small amount to ensure updatedAt will be different
    setTimeout(() => {
      project.update({
        name: 'Updated Solar Plant',
        status: 'IN_PROGRESS'
      });

      expect(project.name).toBe('Updated Solar Plant');
      expect(project.status).toBe('IN_PROGRESS');
      expect(project.updatedAt).not.toBe(originalUpdatedAt);
    }, 1);
  });
});
