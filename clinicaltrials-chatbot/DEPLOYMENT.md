# Deployment Guide — Backend (Render) and Frontend (Vercel)

This guide shows how to deploy the FastAPI backend to Render and the Next.js frontend to Vercel, and how to wire `NEXT_PUBLIC_API_URL` so the frontend talks to the backend.

## Overview
- Backend: Deploy to Render (recommended for small teams). The GitHub Actions workflow `/.github/workflows/deploy-backend-render.yml` will trigger a Render deploy on push to `main`.
- Frontend: Deploy to Vercel. Configure `NEXT_PUBLIC_API_URL` to point to the backend URL (Render service domain).

## Prerequisites
- GitHub repository connected to this project
- Render account and a Service created for the backend (Web Service)
- Vercel account and project for the frontend
- Add these secrets to your GitHub repository (Settings → Secrets):
  - `RENDER_SERVICE_ID` — the Render service ID for your backend (found in Render service dashboard URL)
  - `RENDER_API_KEY` — a Render API key with deploy access
  - `VERCEL_TOKEN` — Vercel personal token (if you want the workflow to set env vars automatically)
  - `VERCEL_PROJECT_ID` — the Vercel project ID (from Vercel dashboard)

## Using the included GitHub Actions workflow
1. Push your branch to `main`.
2. The workflow `deploy-backend-render.yml` will run and:
   - POST to Render to create a new deploy for `RENDER_SERVICE_ID`.
   - Poll Render for the service domain.
   - If `VERCEL_TOKEN` and `VERCEL_PROJECT_ID` are set, the workflow will call the Vercel API to set `NEXT_PUBLIC_API_URL` to the Render domain.

Notes:
- The workflow requires `jq` to parse JSON; `ubuntu-latest` includes it by default. If anything fails, check the Actions run logs.
- For production, you may want to set the Vercel env var manually in the Vercel dashboard instead of using the workflow.

## Vercel KV (recommended for injection in production)
- The dev injection route in `app/api/dev/inject/route.ts` supports Vercel KV when `VERCEL_KV_ENABLED=1`.
- To enable on Vercel, provision a Vercel KV instance, add its connection variables to your Vercel project, and set `VERCEL_KV_ENABLED=1` in Vercel Environment Variables.

## Manual steps to connect backend and frontend
1. Deploy backend to Render:
   - Create a new Web Service on Render, connect your backend repo (or the same monorepo backend folder), and set build/start commands as described in the backend README.
   - After creation, copy the service ID and set `RENDER_SERVICE_ID` in GitHub secrets.
   - Create an API key in Render and set `RENDER_API_KEY` in GitHub secrets.
2. Deploy frontend to Vercel:
   - Import the repo into Vercel.
   - Set env var `NEXT_PUBLIC_API_URL` to the Render service domain (e.g., `https://your-service.onrender.com`).

## Security
- `app/api/dev/inject/route.ts` supports `REQUIRE_INJECT_SECRET=1` and `DEV_INJECT_SECRET` for protection. When deploying to Vercel, enable `REQUIRE_INJECT_SECRET` and set `DEV_INJECT_SECRET` in Vercel env variables.

## Troubleshooting
- If the frontend cannot contact the backend, check `NEXT_PUBLIC_API_URL` and CORS settings on the backend.
- Check GitHub Actions logs for deploy errors and Render dashboard for build failures.
