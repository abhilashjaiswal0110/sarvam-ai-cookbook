# RTI Application Drafter

**APIs:** STT → Chat → Translate

A citizen speaks their grievance in any Indian language; the system transcribes it, drafts a formal RTI application or complaint letter, and provides both an official-language and regional-language version.

## Features

- **Voice or text input** — upload audio or type directly
- **Auto language detection** — no need to specify the language
- **Formal drafting** — legally structured RTI format (Section 6, RTI Act 2005)
- **Dual output** — official draft (Hindi/English) + regional translation
- **Iterative refinement** — provide feedback to improve the draft
- **PII-safe** — placeholders used for personal details, never stored

## Run

```bash
cd examples/enterprise
streamlit run usecases/rti_drafter/app.py
```

## Architecture

```
rti_drafter/
├── app.py        # Streamlit UI with voice + text tabs
├── service.py    # STT → Chat → Translate pipeline
└── README.md
```

## Pipeline

```
Voice/Text Input
      │
      ▼
  STT (transcribe)
      │
      ▼
  Chat (formal draft)
      │
      ▼
  Translate (regional copy)
      │
      ▼
  Official + Regional Draft
```
