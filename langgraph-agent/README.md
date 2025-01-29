# LangGraph Agent with DeepSeek and GPT-3.5

This project implements a LangGraph-based agent that uses DeepSeek-R1 for detailed reasoning and GPT-3.5 for generating concise responses.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
Create a `.env` file with your API keys:
```
OPENROUTER_API_KEY=your_openrouter_api_key
OPENAI_API_KEY=your_openai_api_key
```

- Get your OpenRouter API key from: https://openrouter.ai/
- Get your OpenAI API key from: https://platform.openai.com/

## Usage

Run the agent:
```bash
npm start
# or
npm run dev
```

The agent will:
1. Use DeepSeek-R1 to perform detailed reasoning about the input
2. Pass the reasoning to GPT-3.5 to generate a clear, concise response

## How it Works

1. The input is first processed by DeepSeek-R1, which provides detailed reasoning and analysis
2. This reasoning is then passed to GPT-3.5, which generates a clear and concise final response
3. The workflow is managed by LangGraph, ensuring proper flow of information between models

## Example

The default example asks about the principles of functional programming. You can modify the input in `index.js` to ask different questions or handle different tasks.
