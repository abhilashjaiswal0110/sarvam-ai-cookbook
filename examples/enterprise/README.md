# Sarvam AI Enterprise Use Cases

Production-grade, multilingual AI applications built on the [Sarvam AI](https://sarvam.ai/) platform — designed for India's linguistic diversity and real-world impact.

---

## Architecture Overview

```
enterprise/
├── core/                              # Shared infrastructure library
│   ├── config.py                      # Centralized configuration management
│   ├── sarvam_client.py               # Unified Sarvam API client (retry, rate limiting)
│   ├── models.py                      # Pydantic data models (request/response)
│   ├── exceptions.py                  # Custom exception hierarchy
│   ├── validators.py                  # Input validation & sanitization
│   ├── constants.py                   # Language codes, model names, limits
│   ├── middleware.py                   # Rate limiting, audit logging
│   └── logging_config.py             # Structured logging (JSON)
│
├── usecases/
│   ├── rural_bank_onboarding/         # 1. KYC onboarding in local language
│   ├── anganwadi_learning/            # 2. Early learning for children
│   ├── mother_tongue_tutor/           # 3. Language bridge tutor
│   ├── rti_drafter/                   # 4. RTI application drafter
│   ├── legal_aid_bot/                 # 5. Legal rights advisor
│   ├── regional_recipe_narrator/      # 6. Voice recipe documentation
│   ├── emergency_helpline_transcriber/# 7. Real-time distress call transcription
│   └── flood_cyclone_broadcaster/     # 8. Alert broadcasting system
│
├── tests/                             # Comprehensive test suite
├── docker/                            # Container deployment
├── .env.example                       # Environment variables template
├── pyproject.toml                     # Project metadata & tooling
└── Makefile                           # Developer commands
```

## Use Cases

| # | Use Case | APIs Used | Description |
|---|----------|-----------|-------------|
| 1 | **Rural Bank Onboarding** | Chat + TTS | Guides first-time bank account holders through KYC |
| 2 | **Anganwadi Learning** | TTS + Chat | Stories, rhymes, early learning in local dialect |
| 3 | **Mother Tongue Tutor** | Translate + Transliterate + TTS | Home language → Hindi/English bridge |
| 4 | **RTI Application Drafter** | STT → Chat → Translate | Voice-to-formal-document in regional + official language |
| 5 | **Legal Aid Bot** | Chat + Translate + TTS | FIR, land rights, consumer rights in plain language |
| 6 | **Regional Recipe Narrator** | Chat + TTS | Document indigenous recipes with voice narration |
| 7 | **Emergency Helpline Transcriber** | STT + Call Analytics | Real-time distress call transcription for dispatch |
| 8 | **Flood/Cyclone Alert Broadcaster** | Translate → TTS | Official alerts → local language voice broadcasts |

## Quick Start

### Prerequisites

- Python 3.11+
- [Sarvam AI API Key](https://dashboard.sarvam.ai/)

### Setup

```bash
cd examples/enterprise

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your SARVAM_API_KEY
```

### Run a Use Case

```bash
# Example: Rural Bank Onboarding
streamlit run usecases/rural_bank_onboarding/app.py

# Example: Emergency Helpline Transcriber
streamlit run usecases/emergency_helpline_transcriber/app.py

# Run all tests
pytest tests/ -v
```

### Docker

```bash
docker compose -f docker/docker-compose.yml up
```

## Security & Data Governance

- **API Key Management**: Environment-variable based, never logged or exposed
- **Input Sanitization**: All user input validated and sanitized before API calls
- **PII Protection**: Aadhaar, PAN, phone numbers detected and masked in logs
- **Audit Logging**: Structured JSON logs with request IDs for traceability
- **Rate Limiting**: Per-client rate limiting with configurable thresholds
- **Error Handling**: No sensitive data in error responses; structured error codes

## Supported Languages

Bengali, English, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu

## License

See repository [LICENSE](../../LICENSE).
