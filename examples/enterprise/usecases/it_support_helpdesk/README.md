# IT Support Helpdesk

**APIs:** Chat + Translate + TTS + STT + Language Detection

Multilingual IT support helpdesk with AI-powered diagnostics, knowledge base search, ticket management, and voice input/output — built on the Sarvam Enterprise framework.

## Features

- **AI Diagnostics:** Describe your issue in any supported language — the AI diagnoses, categorizes, and suggests solutions
- **20+ KB Articles:** Pre-built knowledge base covering Network, Hardware, Software, Security, and Email/Collaboration issues
- **Ticket Management:** Auto-creates tickets with category/priority detection, full CRUD with JSON persistence
- **Voice I/O:** Upload audio to describe issues (STT) and listen to responses (TTS)
- **Multilingual:** Supports 11 Indian languages with automatic language detection
- **Enterprise Features:** Rate limiting, audit logging, PII masking, retry with backoff (via core framework)

## Run

```bash
cd examples/enterprise
streamlit run usecases/it_support_helpdesk/app.py
```

## Architecture

```
it_support_helpdesk/
├── app.py             # Streamlit UI with 4 tabs (Report, Tickets, KB, Dashboard)
├── service.py         # Diagnose pipeline: detect lang → translate → KB search → chat → TTS
├── knowledge_base.py  # 20+ IT articles + category/priority constants
├── ticket_manager.py  # JSON-file backed ticket CRUD
└── README.md
```

## Tabs

| Tab | Description |
|-----|-------------|
| 🆘 Report Issue | Chat with AI to diagnose IT issues, with voice input support |
| 🎫 My Tickets | View, filter, and update support tickets |
| 📚 Knowledge Base | Browse or search 20+ common IT issue resolutions |
| 📊 Dashboard | KPI metrics and charts for ticket statistics |
