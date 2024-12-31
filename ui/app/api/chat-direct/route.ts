import { StreamingTextResponse, Message } from 'ai'
import { NextResponse } from 'next/server'
import { ChatAnthropic } from '@langchain/anthropic'
import { HumanMessage, SystemMessage } from '@langchain/core/messages'
import { AIMessage } from '@langchain/core/messages'
import { MessageContentText } from '@langchain/core/messages'

export async function POST(req: Request) {
  try {
    const { prompt, messages: previousMessages, modelName } = await req.json()
    
    const apiKey = process.env.ANTHROPIC_API_KEY
    if (!apiKey) {
      return NextResponse.json(
        { error: 'ANTHROPIC_API_KEY not found in environment variables. Please check Fly.io secrets are properly set.' },
        { status: 401 }
      )
    }

    if (!apiKey.startsWith('sk-ant-api')) {
      return NextResponse.json(
        { error: 'Invalid ANTHROPIC_API_KEY format - should start with sk-ant-api. Please check your API key in env.local.' },
        { status: 401 }
      )
    }

    const model = new ChatAnthropic({
      apiKey: apiKey,
      modelName: modelName || 'claude-3-sonnet-20240229',
      streaming: true
    })

    // Convert previous messages to the format expected by the model
    const messageHistory = previousMessages?.map((msg: any) => {
      // Handle nested content structure
      let messageText = ''
      if (Array.isArray(msg.content)) {
        const textContent = msg.content.find((c: any) => c.type === 'text')
        messageText = textContent?.text || ''
      } else {
        messageText = msg.content || ''
      }
      
      return msg.role === 'system'
        ? new SystemMessage(messageText)
        : new HumanMessage(messageText)
    }) || []

    // Use the full message history
    const messages = messageHistory

    let stream;
    try {
      stream = await model.stream(messages);
    } catch (error: any) {
      return NextResponse.json(
        { error: `API Error: ${error.message}. Please check your API key and try again.` },
        { status: error.status || 500 }
      )
    }
    
    // Transform the stream to emit text chunks
    const textEncoder = new TextEncoder()
    const textStream = new ReadableStream({
      async start(controller) {
        try {
          for await (const chunk of stream) {
            // Handle both string and complex message content
            let content = ''
            
            if (chunk instanceof AIMessage) {
              if (typeof chunk.content === 'string') {
                content = chunk.content
              } else if (Array.isArray(chunk.content)) {
                content = chunk.content
                  .filter((c): c is MessageContentText => c.type === 'text')
                  .map(c => c.text)
                  .join('')
              }
            } else if (typeof chunk.content === 'string') {
              content = chunk.content
            }

            if (content) {
              controller.enqueue(textEncoder.encode(content))
            }
          }
          controller.close()
        } catch (error: any) {
          controller.error(new Error(`Streaming Error: ${error.message}. Please check your connection and try again.`))
        }
      }
    })

    return new StreamingTextResponse(textStream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8'
      }
    })
    
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    )
  }
}
