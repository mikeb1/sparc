import { AgentExecutor } from 'langchain/agents';

export class CommunicationService {
  private agent: AgentExecutor;

  constructor(agent: AgentExecutor) {
    this.agent = agent;
  }

  sendMessage(message: string): string {
    if (!message.trim()) {
      throw new Error('Message cannot be empty');
    }
    return this.agent.run(message);
  }

  printResponse(response: string | null): void {
    if (response === null) {
      console.log('Response was None');
    } else {
      console.log(response);
    }
  }

  runAgent(message: string): string {
    if (!message.trim()) {
      throw new Error('Message cannot be empty');
    }
    const response = this.sendMessage(message);
    this.printResponse(response);
    return response;
  }
}
