import { VectorStore } from 'langchain/vectorstores/base';

interface ConversationState {
  history: string[];
}

export class StateManager {
  private vectorStore: VectorStore;

  constructor(vectorStore: VectorStore) {
    this.vectorStore = vectorStore;
  }

  async getState(conversationId: string): Promise<ConversationState> {
    const state = await this.vectorStore.get(conversationId);
    return state ?? { history: [] };
  }

  async setState(conversationId: string, state: ConversationState): Promise<void> {
    await this.vectorStore.add(conversationId, state);
  }

  async updateState(conversationId: string, message: string): Promise<ConversationState> {
    const currentState = await this.getState(conversationId);
    const updatedState = {
      history: [...currentState.history, message],
    };
    await this.setState(conversationId, updatedState);
    return updatedState;
  }

  async getConversationHistory(conversationId: string): Promise<string[]> {
    const state = await this.getState(conversationId);
    return state.history;
  }
}
