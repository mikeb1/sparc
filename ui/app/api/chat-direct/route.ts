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
    console.log('API Key present:', !!apiKey)
    console.log('API Key format:', apiKey?.startsWith('sk-ant-api'))
    console.log('API Key length:', apiKey?.length)
    console.log('Environment variables:', Object.keys(process.env).filter(key => key.includes('ANTHROPIC')))
    
    if (!apiKey) {
      console.error('ANTHROPIC_API_KEY missing from environment')
      return NextResponse.json(
        { 
          error: 'ANTHROPIC_API_KEY not found in environment variables.',
          details: 'Check Fly.io secrets with: flyctl secrets list',
          env: Object.keys(process.env).filter(key => key.includes('ANTHROPIC'))
        },
        { status: 401 }
      )
    }

    if (!apiKey.startsWith('sk-ant-api')) {
      console.error('Invalid API key format')
      return NextResponse.json(
        { 
          error: 'Invalid ANTHROPIC_API_KEY format - should start with sk-ant-api',
          details: 'Verify key format in Anthropic console and update Fly.io secrets',
          keyPrefix: apiKey.substring(0, 10) + '...'
        },
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
      console.error('Streaming error:', error)
      console.error('Error details:', {
        message: error.message,
        status: error.status,
        response: error.response?.data
      })
      return NextResponse.json(
        { 
          error: `API Error: ${error.message}. Please check your API key and try again.`,
          details: error.response?.data || 'No additional details available'
        },
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
