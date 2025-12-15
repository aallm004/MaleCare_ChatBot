import fs from 'fs';
import path from 'path';
import { NextResponse } from 'next/server';

const FILE = path.resolve(process.cwd(), '.dev_inject.json');

function isValidMessage(m: any) {
  if (!m || typeof m !== 'object') return false;
  if (!('from' in m) || !('text' in m)) return false;
  if (typeof m.from !== 'string' || typeof m.text !== 'string') return false;
  if ('results' in m && !Array.isArray(m.results)) return false;
  return true;
}

async function writeMessages(messages: any[]) {
  // If Vercel KV enabled, use it; otherwise fallback to filesystem for local dev.
  if (process.env.VERCEL_KV_ENABLED === '1') {
    try {
      const { kv } = await import('@vercel/kv');
      await kv.set('dev_inject_messages', JSON.stringify(messages));
      return;
    } catch (e) {
      // fallback
    }
  }

  fs.writeFileSync(FILE, JSON.stringify(messages, null, 2));
}

async function readAndClearMessages() {
  if (process.env.VERCEL_KV_ENABLED === '1') {
    try {
      const { kv } = await import('@vercel/kv');
      const val = await kv.get('dev_inject_messages');
      if (!val) return [];
      await kv.del('dev_inject_messages');
      try {
        return JSON.parse(val as string);
      } catch (e) {
        return [];
      }
    } catch (e) {
      // fallback
    }
  }

  if (!fs.existsSync(FILE)) return [];
  const raw = fs.readFileSync(FILE, 'utf-8');
  try { fs.unlinkSync(FILE); } catch (e) {}
  try { return JSON.parse(raw || '[]'); } catch (e) { return []; }
}

export async function POST(req: Request) {
  try {
    if (process.env.REQUIRE_INJECT_SECRET === '1') {
      const secret = req.headers.get('x-dev-inject-secret') || '';
      if (!process.env.DEV_INJECT_SECRET || secret !== process.env.DEV_INJECT_SECRET) {
        return NextResponse.json({ ok: false, error: 'missing or invalid secret' }, { status: 401 });
      }
    }

    const body = await req.json();
    if (!body || !Array.isArray(body.messages)) {
      return NextResponse.json({ ok: false, error: 'invalid shape: expected { messages: [...] }' }, { status: 400 });
    }

    for (const m of body.messages) {
      if (!isValidMessage(m)) return NextResponse.json({ ok: false, error: 'invalid message shape' }, { status: 400 });
    }

    await writeMessages(body.messages);
    return NextResponse.json({ ok: true });
  } catch (err) {
    return NextResponse.json({ ok: false, error: String(err) }, { status: 500 });
  }
}

export async function GET() {
  try {
    const messages = await readAndClearMessages();
    return NextResponse.json({ ok: true, messages: Array.isArray(messages) ? messages : [] });
  } catch (err) {
    return NextResponse.json({ ok: false, error: String(err) }, { status: 500 });
  }
}
