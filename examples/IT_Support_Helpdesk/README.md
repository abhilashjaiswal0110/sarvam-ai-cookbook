# Multilingual IT Support Helpdesk

An end-to-end IT support helpdesk application powered by **Sarvam AI**, built for enterprises that serve employees across India's diverse linguistic landscape. Employees can report IT issues in any of **11 Indian languages** — by text or voice — and receive AI-generated troubleshooting guidance, instant knowledge base answers, and automated ticket creation.

## Features

| Feature | Sarvam AI API Used |
|---|---|
| Auto-detect user's language | Language Identification (`/text-lid`) |
| Chat-based troubleshooting in any language | Chat Completion (`sarvam-m`) |
| Cross-language KB search (auto-translate to English) | Translation (`/translate`) |
| Voice-based issue reporting | Speech-to-Text (`/speech-to-text`) |
| Read-aloud AI responses | Text-to-Speech (`/text-to-speech`, Bulbul v2) |
| Auto-assign ticket priority from issue text | Keyword heuristics + Text Analytics |

### Application Tabs

- **Report Issue** — Multi-turn chat interface with audio upload, inline KB suggestions, and one-click ticket creation
- **My Tickets** — View, filter (by status / category / priority), and update all support tickets
- **Knowledge Base** — Search or browse 20+ pre-built IT issue resolutions across 5 categories
- **Dashboard** — KPI metrics and charts: total tickets, by status, category, and priority

### Supported Languages

English · Hindi · Tamil · Telugu · Bengali · Marathi · Gujarati · Kannada · Malayalam · Punjabi · Odia

## Quick Start

### 1. Get a Sarvam API key
Sign up at [app.sarvam.ai](https://app.sarvam.ai) and copy your API key.

### 2. Install dependencies
```bash
cd examples/IT_Support_Helpdesk
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env and paste your SARVAM_API_KEY
```

### 4. Run the app
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`. Enter your API key in the sidebar if not set via `.env`.

## Run Tests

All 81 tests run without a real API key (HTTP calls are mocked):

```bash
pytest tests/ -v
```

For a coverage report:
```bash
pytest tests/ --cov=. --cov-report=term-missing
```

## Architecture

```
IT_Support_Helpdesk/
├── app.py               ← Streamlit UI (4 tabs)
├── config.py            ← Constants: language map, categories, system prompt
├── sarvam_client.py     ← Thin wrapper around all Sarvam AI REST APIs
├── knowledge_base.py    ← 20+ pre-built IT resolutions, keyword search
├── ticket_manager.py    ← JSON-persisted ticket CRUD with filtering & stats
└── tests/
    ├── test_sarvam_client.py    ← Unit tests (all HTTP mocked)
    ├── test_knowledge_base.py   ← Unit tests (no I/O)
    ├── test_ticket_manager.py   ← Unit tests (tmp file fixture)
    └── test_integration.py      ← End-to-end scenario tests (HTTP mocked)
```

## Example Interaction

**User (Hindi):** मेरा VPN काम नहीं कर रहा, ऑफिस सर्वर से कनेक्ट नहीं हो पा रहा।

**HelpDesk AI:**
```
**Category:** Network & Connectivity
**Priority:** High
**Steps to resolve:**
1. जांचें कि इंटरनेट कनेक्शन काम कर रहा है।
2. VPN क्लाइंट को बंद करके दोबारा खोलें।
3. Disconnect करके 30 सेकंड बाद फिर Connect करें।
...
**Escalation needed:** No
```

The app then surfaces the matching KB article (NET-001) inline and pre-fills a ticket creation form.

## Sarvam AI APIs Reference

| API | Endpoint | Auth |
|---|---|---|
| Language Detection | `POST /text-lid` | `api-subscription-key` |
| Translation | `POST /translate` | `api-subscription-key` |
| Chat Completion | `POST /v1/chat/completions` | `Bearer` token |
| Text-to-Speech | `POST /text-to-speech` | `api-subscription-key` |
| Speech-to-Text | `POST /speech-to-text` | `api-subscription-key` |
| Text Analytics | `POST /text-analytics` | `api-subscription-key` |

All endpoints use base URL: `https://api.sarvam.ai`
