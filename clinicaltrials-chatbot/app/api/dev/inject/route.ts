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

export async function POST(req: Request) {
  try {
    // Optional secret check in deployments: set REQUIRE_INJECT_SECRET=1 and DEV_INJECT_SECRET
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

    // validate each message
    for (const m of body.messages) {
      if (!isValidMessage(m)) return NextResponse.json({ ok: false, error: 'invalid message shape' }, { status: 400 });
    }

    // Persist locally for dev. NOTE: Vercel serverless has an ephemeral filesystem; for cloud use Vercel KV or another store.
    fs.writeFileSync(FILE, JSON.stringify(body.messages, null, 2));
    return NextResponse.json({ ok: true });
  } catch (err) {
    return NextResponse.json({ ok: false, error: String(err) }, { status: 500 });
  }
}

export async function GET() {
  try {
    // Optional secret for reading as well
    if (process.env.REQUIRE_INJECT_SECRET === '1') {
      // Next.js route GET doesn't expose headers on server functions in the same way; callers should include secret as query param if needed.
      // For simplicity, allow read without secret on local dev.
    }

    if (!fs.existsSync(FILE)) return NextResponse.json({ ok: true, messages: [] });
    const raw = fs.readFileSync(FILE, 'utf-8');
    // clear after reading
    try { fs.unlinkSync(FILE); } catch (e) {}
    const data = JSON.parse(raw || '[]');
    return NextResponse.json({ ok: true, messages: Array.isArray(data) ? data : [] });
  } catch (err) {
    return NextResponse.json({ ok: false, error: String(err) }, { status: 500 });
  }
}
