# Author: Codex | Created: 2026-11-24 21:27:52 +08:00 | Build the Linux workbench without local project data.
FROM node:24-bookworm-slim AS web
WORKDIR /app/frontend
RUN npm install --global pnpm@10.32.1
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
COPY remotion/src/ /app/remotion/src/
RUN ln -s /app/frontend/node_modules /app/remotion/node_modules && pnpm run build

FROM python:3.14-slim-bookworm
WORKDIR /app
RUN pip install --no-cache-dir 'fastapi>=0.115,<1' 'uvicorn>=0.34,<1' 'pydantic>=2,<3' 'aiofiles>=24,<26' 'python-multipart>=0.0.20,<1'
COPY backend/ backend/
COPY library/motions/ library/motions/
COPY library/styles/ library/styles/
COPY library/catalog.json* library/
COPY remotion/public/ remotion/public/
COPY --from=web /app/frontend/dist/ frontend/dist/
RUN mkdir -p projects library/assets
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
