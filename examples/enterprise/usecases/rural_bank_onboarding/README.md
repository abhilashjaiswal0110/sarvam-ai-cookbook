# Rural Bank Onboarding Assistant

**APIs:** Chat Completions + Text-to-Speech

Guides first-time bank account holders in rural India through the KYC (Know Your Customer) process entirely in their chosen regional language, with voice narration for accessibility.

## Features

- **Step-by-step KYC flow:** Welcome → Language → Personal Info → Documents → Account Type → Summary
- **Voice output:** Every response is narrated aloud via Sarvam TTS
- **11 Indian languages** supported
- **Culturally sensitive:** Simple, respectful language; no jargon
- **PII-safe:** Never collects actual document numbers — only explains requirements

## Run

```bash
cd examples/enterprise
streamlit run usecases/rural_bank_onboarding/app.py
```

## Architecture

```
rural_bank_onboarding/
├── app.py        # Streamlit UI
├── service.py    # KYC flow logic, onboarding state machine
└── README.md
```
