# Emergency Helpline Transcriber

**APIs:** STT + Chat (Call Analytics)

Transcribes distress calls in any Indian language and provides structured analysis for the dispatch team — emergency type, urgency level, location, and recommended action.

## Features

- **Multilingual transcription:** Understands calls in 11 Indian languages
- **Structured analysis:** Emergency type, urgency (critical/high/medium/low), location, key details
- **Dispatch dashboard:** Visual urgency indicators for quick triage
- **English translation:** Standardized transcript for dispatch teams
- **Audio or text input:** Upload a recording or paste a transcript
- **Caller assessment:** Evaluates emotional state for dispatcher preparedness

## Run

```bash
cd examples/enterprise
streamlit run usecases/emergency_helpline_transcriber/app.py
```

## Architecture

```
emergency_helpline_transcriber/
├── app.py        # Streamlit dispatch dashboard
├── service.py    # STT + analysis pipeline
└── README.md
```

## Pipeline

```
Distress Call Audio
      │
      ▼
  STT (transcribe, detect language)
      │
      ▼
  Translate to English
      │
      ▼
  Chat LLM (structured analysis)
      │
      ▼
  Dispatch Dashboard
  (type, urgency, location, action)
```
