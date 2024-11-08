import { BaseLanguageAgent, AgentExecutor, CallbackManagerForLLMRun } from 'langchain/agents';
import { PythonREPLTool } from 'langchain/tools';

/**
 * Establish component for swarm agent system.
 * Initializes a Python REPL agent with a callback manager.
 */
export class Establish {
  private agent: BaseLanguageAgent;
  private executor: AgentExecutor;
  private callbackManager: CallbackManagerForLLMRun;

  /**
   * Creates an instance of Establish.
   * @param agent The base language agent to initialize.
   * @param callbackManager The callback manager for LLM runs.
   */
  constructor(agent: BaseLanguageAgent, callbackManager: CallbackManagerForLLMRun) {
    this.agent = agent;
    this.callbackManager = callbackManager;
    this.executor = AgentExecutor.fromAgentAndTools({
      agent: this.agent,
      tools: [new PythonREPLTool()],
      callbackManager: this.callbackManager,
    });
  }

  /**
   * Initializes the agent and returns the Python REPL instance.
   * @returns The initialized Python REPL instance.
   */
  public initialize(): PythonREPLTool {
    if (!this.agent) {
      throw new Error('Agent not provided');
    }

    return this.executor.getInnerTool<PythonREPLTool>('python_repl');
  }

  /**
   * Runs a Python command on the initialized agent.
   * @param command The Python command to run.
   */
  public run(command: string): void {
    const repl = this.initialize();
    repl.run(command);
  }
}
