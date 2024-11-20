import { Project } from '../models/Project.js';

export class ProjectService {
  constructor() {
    this.projects = new Map();
  }

  createProject(projectData) {
    const project = new Project(projectData);
    this.projects.set(project.id, project);
    return project;
  }

  updateProject(projectId, updates) {
    const project = this.projects.get(projectId);
    if (!project) {
      throw new Error(`Project not found with id: ${projectId}`);
    }
    project.update(updates);
    return project;
  }

  getProject(projectId) {
    const project = this.projects.get(projectId);
    if (!project) {
      throw new Error(`Project not found with id: ${projectId}`);
    }
    return project;
  }

  listProjects(filters = {}) {
    let projects = Array.from(this.projects.values());
    
    if (filters.type) {
      projects = projects.filter(p => p.type === filters.type);
    }
    if (filters.status) {
      projects = projects.filter(p => p.status === filters.status);
    }
    
    return projects;
  }
}
