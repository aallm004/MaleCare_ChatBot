const DEFAULT_BACKEND = 'http://localhost:8000';

const getBaseUrl = () => {
  // Use NEXT_PUBLIC_API_URL if provided (Vercel env var), otherwise default to local backend
  if (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;
  return DEFAULT_BACKEND;
};

async function fetchJSON(fullUrl: string, opts: RequestInit = {}) {
  const res = await fetch(fullUrl, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  // return raw response for callers to inspect status/body
  const text = await res.text();
  let json: any = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch (e) {
    // not JSON
  }
  return { ok: res.ok, status: res.status, json, text };
}

export async function healthCheck() {
  try {
    const base = getBaseUrl();
    const res = await fetch(`${base}/health`);
    if (res.ok) return { ok: true, path: '/health', status: res.status };
    return { ok: false, status: res.status };
  } catch (err) {
    return { ok: false, error: (err as Error).message };
  }
}

// Post chat or questionnaire payload to backend service (FastAPI)
export async function postChat(payload: any) {
  const base = getBaseUrl();
  try {
    if (payload?.type === 'message') {
      // Backend expects { user_id, message }
      const body = { user_id: payload.user_id || 'local-user', message: payload.text };
      const r = await fetchJSON(`${base}/message`, { method: 'POST', body: JSON.stringify(body) });
      return r.json ?? { ok: r.ok, status: r.status, text: r.text };
    }

    if (payload?.type === 'questionnaire') {
      const d = payload.data || {};
      // Map frontend fields to backend intake fields
      const intake = {
        user_id: payload.user_id || 'local-user',
        cancer_type: d.cancerType || d.cancer_type || '',
        stage: d.cancerStage || d.stage || '',
        age: Number(d.age) || 0,
        sex: (d.gender || '').toLowerCase(),
        // backend expects location as 'City, State' ideally; frontend may provide 'state' only
        location: d.location || d.state || '',
        comorbidities: d.comorbidities ? (Array.isArray(d.comorbidities) ? d.comorbidities : [d.comorbidities]) : [],
        prior_treatments: d.priorTreatments ? (Array.isArray(d.priorTreatments) ? d.priorTreatments : [d.priorTreatments]) : [],
      };
      const r = await fetchJSON(`${base}/intake`, { method: 'POST', body: JSON.stringify(intake) });
      return r.json ?? { ok: r.ok, status: r.status, text: r.text };
    }

    // default: forward to /message with text
    const body = { user_id: payload?.user_id || 'local-user', message: payload?.text || '' };
    const r = await fetchJSON(`${base}/message`, { method: 'POST', body: JSON.stringify(body) });
    return r.json ?? { ok: r.ok, status: r.status, text: r.text };
  } catch (err) {
    return { ok: false, error: (err as Error).message };
  }
}
