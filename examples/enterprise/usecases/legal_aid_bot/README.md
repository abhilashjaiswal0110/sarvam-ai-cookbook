# Legal Aid Bot

**APIs:** Chat + Translate + TTS

Explains FIR filing, land rights, consumer rights, domestic violence protections, and labour rights in plain regional language with voice narration.

## Features

- **5 legal topics:** FIR Filing, Land Rights, Consumer Rights, Domestic Violence, Labour Rights
- **Knowledge-grounded:** Structured legal information fed as context to the LLM
- **Plain language:** Explains complex law in words anyone can understand
- **Dual language:** Answer in regional language + English translation
- **Voice output:** Listen to the explanation
- **Disclaimer built-in:** Always reminds user to consult a lawyer

## Run

```bash
cd examples/enterprise
streamlit run usecases/legal_aid_bot/app.py
```

## Architecture

```
legal_aid_bot/
├── app.py             # Streamlit UI
├── service.py         # Chat + Translate + TTS pipeline
├── knowledge_base.py  # Structured legal information
└── README.md
```
