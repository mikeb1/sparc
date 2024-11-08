import { BaseAgent } from 'langchain/agents';

export class AgentManager {
  private agents: BaseAgent[];

  constructor(agents: BaseAgent[]) {
    this.agents = agents;
  }

  addAgent(agent: BaseAgent): void {
    this.agents.push(agent);
  }

  removeAgent(agent: BaseAgent): void {
    const index = this.agents.indexOf(agent);
    if (index !== -1) {
      this.agents.splice(index, 1);
    }
  }

  async run(query: string): Promise<string[]> {
    return this.delegateToAgents(query);
  }

  private async delegateToAgents(query: string): Promise<string[]> {
    const results: string[] = [];
    for (const agent of this.agents) {
      try {
        const result = await agent.run(query);
        results.push(result);
      } catch (error) {
        console.error(`Error running agent: ${error}`);
      }
    }
    return results;
  }
}
