import { ProjectService } from './services/ProjectService.js';

// Create a new instance of ProjectService
const projectService = new ProjectService();

// Create some sample projects
const project1 = projectService.createProject({
  name: 'Solar Farm Alpha',
  type: 'IMPLEMENTATION',
  location: 'Desert Valley',
  startDate: new Date('2024-01-01'),
  status: 'PLANNING'
});

const project2 = projectService.createProject({
  name: 'Wind Farm Beta',
  type: 'TRANSMISSION',
  location: 'Mountain Ridge',
  startDate: new Date('2024-02-01'),
  status: 'PLANNING'
});

// List all projects
console.log('All Projects:');
console.log(JSON.stringify(projectService.listProjects(), null, 2));

// List projects filtered by type
console.log('\nImplementation Projects:');
console.log(JSON.stringify(projectService.listProjects({ type: 'IMPLEMENTATION' }), null, 2));

// Get a specific project
console.log('\nProject Details:');
const firstProject = projectService.listProjects()[0];
console.log(JSON.stringify(projectService.getProject(firstProject.id), null, 2));
