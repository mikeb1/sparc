import { AgentExecutor, AgentExecutorInput } from 'langchain/agents';

interface TaskSchedulerOptions {
  agent: AgentExecutor;
}

class TaskScheduler {
  private agent: AgentExecutor;

  constructor(options: TaskSchedulerOptions) {
    this.agent = options.agent;
  }

  scheduleTask(task: AgentExecutorInput, callback?: (result: string) => void): void {
    try {
      const result = this.agent.run(task);
      if (callback) {
        result.addCallback((output: string) => callback(output));
      }
    } catch (error) {
      console.error('Error scheduling task:', error);
      throw error;
    }
  }
}

export default TaskScheduler;
