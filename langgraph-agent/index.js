import { ChatOpenAI } from "@langchain/openai";
import { StateGraph, END } from "@langchain/langgraph";
import { RunnableSequence } from "@langchain/core/runnables";
import { StringOutputParser } from "@langchain/core/output_parsers";
import axios from "axios";

// Initialize models
const deepseekModel = {
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: process.env.OPENROUTER_API_KEY,
  async invoke(input) {
    try {
      const response = await axios.post(
        `${this.baseURL}/chat/completions`,
        {
          model: "deepseek-ai/deepseek-coder-33b-instruct",
          messages: [{ role: "user", content: input }]
        },
        {
          headers: {
            "Authorization": `Bearer ${this.apiKey}`,
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "LangGraph Agent"
          }
        }
      );
      return response.data.choices[0].message.content;
    } catch (error) {
      console.error("DeepSeek API Error:", error);
      throw error;
    }
  }
};

const gpt35 = new ChatOpenAI({
  modelName: "gpt-3.5-turbo",
  temperature: 0.7,
  openAIApiKey: process.env.OPENAI_API_KEY,
});

// Define the reasoning chain using DeepSeek
const reasoningChain = RunnableSequence.from([
  {
    reasoning: async (input) => {
      const prompt = `Given this input: "${input}", provide detailed reasoning about how to handle it. Break down the problem and analyze different aspects.`;
      return await deepseekModel.invoke(prompt);
    }
  }
]);

// Define the response chain using GPT-3.5
const responseChain = RunnableSequence.from([
  {
    finalResponse: async (input) => {
      const prompt = `Based on this reasoning: "${input.reasoning}", generate a clear and concise response.`;
      return await gpt35.invoke(prompt);
    }
  },
  new StringOutputParser()
]);

// Create the graph
const workflow = new StateGraph({
  channels: ["reasoning", "response"]
});

// Add nodes
workflow.addNode("reasoning", reasoningChain);
workflow.addNode("response", responseChain);

// Add edges
workflow.addEdge("reasoning", "response");
workflow.addEdge("response", END);

// Create the runnable
const chain = workflow.compile();

// Example usage
async function main() {
  const input = "What are the key principles of functional programming?";
  try {
    const result = await chain.invoke(input);
    console.log("Final Response:", result);
  } catch (error) {
    console.error("Error:", error);
  }
}

main();
