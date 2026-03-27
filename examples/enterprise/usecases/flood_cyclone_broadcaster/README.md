# Flood/Cyclone Alert Broadcaster

**APIs:** Translate → TTS

Converts official disaster alerts (cyclone, flood, earthquake) into multi-language voice broadcasts for rapid dissemination to affected populations.

## Features

- **One alert → 11 languages** in a single click
- **Voice broadcasts:** Audio output for each language, ready for PA systems or calls
- **Sample alerts:** Pre-loaded cyclone, flood, and earthquake templates
- **Selective or full broadcast:** Choose specific languages or broadcast to all
- **Formal translation mode:** Maintains the official, urgent tone
- **Fault tolerant:** Continues broadcasting even if one language fails

## Run

```bash
cd examples/enterprise
streamlit run usecases/flood_cyclone_broadcaster/app.py
```

## Architecture

```
flood_cyclone_broadcaster/
├── app.py        # Streamlit broadcast dashboard
├── service.py    # Translate → TTS multi-language pipeline
└── README.md
```

## Pipeline

```
Official Alert (English/Hindi)
      │
      ├─→ Translate to Tamil    → TTS → 🔊 Tamil Audio
      ├─→ Translate to Bengali  → TTS → 🔊 Bengali Audio
      ├─→ Translate to Telugu   → TTS → 🔊 Telugu Audio
      ├─→ Translate to Odia     → TTS → 🔊 Odia Audio
      └─→ ... (all 11 languages)
```
