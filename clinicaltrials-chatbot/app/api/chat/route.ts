import { NextResponse } from 'next/server';

type CTGStudy = {
  NCTId?: string[];
  BriefTitle?: string[];
  Condition?: string[];
  Phase?: string[];
  LocationCountry?: string[];
};

function buildExpr(body: any) {
  // Build a simple expression string from message or questionnaire
  if (!body) return '';
  if (body.type === 'questionnaire' && body.data) {
    const d = body.data;
    // Prefer condition / cancerType and state
    const parts: string[] = [];
    if (d.cancerType) parts.push(d.cancerType);
    if (d.state) parts.push(d.state);
    if (d.cancerStage) parts.push(`stage ${d.cancerStage}`);
    return parts.join(' AND ');
  }
  if (body.type === 'message' && body.text) return body.text;
  return '';
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const expr = encodeURIComponent(buildExpr(body) || 'cancer');

    // Query study_fields for a lightweight JSON response
    const fields = ['NCTId', 'BriefTitle', 'Condition', 'Phase', 'LocationCountry'];
    const min_rnk = 1;
    const max_rnk = 10;
    const url = `https://clinicaltrials.gov/api/query/study_fields?expr=${expr}&fields=${fields.join(',')}&min_rnk=${min_rnk}&max_rnk=${max_rnk}&fmt=json`;

    const res = await fetch(url, { next: { revalidate: 60 } });
    const rawText = await res.text();
    if (!res.ok) {
      // Return diagnostics instead of a 502 so frontend can handle gracefully
      return NextResponse.json(
        { ok: false, upstreamStatus: res.status, upstreamBody: rawText, note: 'Upstream ClinicalTrials.gov returned error (may be blocked or endpoint changed).' },
        { status: 200 }
      );
    }
    // parse JSON from upstream
    let data: any;
    try {
      data = JSON.parse(rawText);
    } catch (e) {
      return NextResponse.json({ ok: false, error: 'Failed to parse upstream JSON', upstreamBody: rawText }, { status: 200 });
    }

    const studies: CTGStudy[] = data?.StudyFieldsResponse?.StudyFields || [];
    const results = studies.map((s: any) => ({
      nctId: s.NCTId?.[0] || '',
      title: s.BriefTitle?.[0] || '',
      condition: (s.Condition || []).join('; '),
      phase: s.Phase?.[0] || '',
      location: (s.LocationCountry || []).slice(0, 5).join(', '),
      url: s.NCTId?.[0] ? `https://clinicaltrials.gov/study/${s.NCTId[0]}` : '',
    }));

    if (!results.length) {
      return NextResponse.json({ ok: true, results: [], reply: 'No trials found for that query.' });
    }

    return NextResponse.json({ ok: true, results, count: results.length });
  } catch (err) {
    return NextResponse.json({ ok: false, error: (err as Error).message }, { status: 400 });
  }
}
