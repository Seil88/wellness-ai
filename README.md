# Wellness.AI

A mobile-first wellness coaching app for **Mind, Body, and Soul**. Features an AI-powered chat with streaming responses, voice input, and a curated onboarding flow.

![Stack](https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-green)
![Stack](https://img.shields.io/badge/Backend-FastAPI-009688)
![Stack](https://img.shields.io/badge/Mobile-Expo%20%2B%20WebView-blue)
![Stack](https://img.shields.io/badge/AI-Ollama%20%2F%20qwen3-orange)

## Screens

1. **Welcome** — Email signup, Google login
2. **Interests** — Pick up to 5 wellness topics
3. **Home** — Voice prompt with animated AI orb
4. **Listening** — Live transcript with waveform visualizer
5. **Chat** — Text-based conversation with suggestion cards
6. **AI Response** — Structured wellness guidance with markdown rendering

## Architecture

```
index.html + design-system.css    Web app (vanilla HTML/CSS/JS)
backend/server.py                 FastAPI streaming proxy → Ollama
mobile/App.js                     Expo WebView wrapper for iOS
```

- **Frontend**: Single-file web app with a full design system, frosted glass UI, screen transitions, and streaming markdown rendering
- **Backend**: FastAPI server that proxies chat requests to an Ollama-compatible endpoint with SSE streaming
- **Mobile**: Expo app wrapping the web app in `react-native-webview` for native iOS deployment

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) with a model pulled (e.g. `ollama pull qwen3:8b`)
- Xcode + iOS Simulator (for mobile)

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # edit MODEL_ENDPOINT and MODEL_NAME
uvicorn server:app --host 0.0.0.0 --port 8000
```

### 2. Web App

```bash
# From project root
python3 -m http.server 8080
```

Open http://localhost:8080 in a browser.

### 3. iOS App

```bash
cd mobile
npm install
npx expo run:ios
```

### All-in-One

```bash
./start-dev.sh
```

Starts the web server (`:8080`), API server (`:8000`), and Expo iOS build in one command.

## Configuration

Edit `backend/.env`:

| Variable | Default | Description |
|---|---|---|
| `MODEL_ENDPOINT` | `http://localhost:8080/v1/chat/completions` | Ollama-compatible chat completions URL |
| `MODEL_NAME` | `default` | Model to use for responses |
| `PORT` | `8000` | Backend server port |

In-app settings (hamburger menu in chat) let you change the backend URL at runtime.

## License

MIT
