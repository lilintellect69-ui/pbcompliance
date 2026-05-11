// Compliance assistant — Vercel Node.js serverless function with streaming SSE.
//
// Per the design brief §5 Architecture Phase 1:
//   - Anthropic SDK (Sonnet 4.6 default, Opus 4.7 via env-var override)
//   - Streaming SSE response
//   - Prompt caching enabled on the route-tier system prompt
//   - Env vars: ANTHROPIC_API_KEY, ASSISTANT_MODEL
//
// Request shape (POST):
//   {
//     messages: [{ role: 'user'|'assistant', content: string }, ...],
//     route:    { type: 'home' | 'framework' | 'requirement' | 'scenario' | 'oq' | 'graph' | 'oq-index',
//                 frameworkId?, reqId?, scenarioId?, oqId? },
//     lens:     'on-prem' | 'ai-factory' | 'both'
//   }
//
// Response: SSE stream of `data: {...}` events. Event shapes:
//   { delta: string }       — text chunk
//   { mode: string }        — detected output mode (emitted once at start)
//   { citations: string[] } — YAML ids the model has been given (emitted once at start)
//   { done: true }          — stream finished
//   { error: string }       — server-side error

import Anthropic from '@anthropic-ai/sdk';
import data from '../os/src/data.json' with { type: 'json' };
import { buildSystemPrompt } from './lib/context-builder.js';
import { detectMode, detectFrameworkMentions } from './lib/intent-detector.js';

const MODEL = process.env.ASSISTANT_MODEL || 'claude-sonnet-4-6';

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

export default async function handler(req, res) {
  // CORS — same-origin in production but useful for local dev / future use
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Vercel Node functions auto-parse JSON bodies when Content-Type is set.
  // Fall back to manual parse for robustness.
  let body = req.body;
  if (!body || typeof body !== 'object') {
    try {
      const chunks = [];
      for await (const chunk of req) chunks.push(chunk);
      body = JSON.parse(Buffer.concat(chunks).toString('utf-8'));
    } catch (e) {
      return res.status(400).json({ error: 'Invalid JSON body' });
    }
  }

  const { messages, route, lens } = body || {};
  if (!Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: 'messages array required' });
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    return res.status(500).json({
      error: 'ANTHROPIC_API_KEY not set. Configure in Vercel project settings → Environment Variables.',
    });
  }

  const lastUser = [...messages].reverse().find((m) => m.role === 'user');
  const userText = lastUser?.content || '';
  const mode = detectMode(userText);
  const frameworkMentions = detectFrameworkMentions(userText);

  const systemPrompt = buildSystemPrompt({
    route,
    lens,
    data,
    mode,
    frameworkMentions,
  });

  // SSE headers
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache, no-transform');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('X-Accel-Buffering', 'no'); // disable nginx/Vercel response buffering

  const send = (obj) => {
    res.write(`data: ${JSON.stringify(obj)}\n\n`);
  };

  send({ mode });

  try {
    const stream = await client.messages.create({
      model: MODEL,
      max_tokens: 1024,
      system: [
        {
          type: 'text',
          text: systemPrompt,
          cache_control: { type: 'ephemeral' },
        },
      ],
      messages: messages.map((m) => ({ role: m.role, content: m.content })),
      stream: true,
    });

    for await (const event of stream) {
      if (event.type === 'content_block_delta' && event.delta?.type === 'text_delta') {
        send({ delta: event.delta.text });
      } else if (event.type === 'message_delta' && event.delta?.stop_reason) {
        // intermediate
      } else if (event.type === 'message_stop') {
        send({ done: true });
      }
    }
  } catch (e) {
    console.error('Anthropic stream error:', e);
    send({ error: e?.message || String(e) });
  }

  res.end();
}

// Vercel function config — give it room for slower-network streams.
export const config = {
  maxDuration: 60,
};
