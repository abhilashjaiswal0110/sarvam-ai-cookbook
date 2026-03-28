# Regional Recipe Narrator

**APIs:** Chat + TTS

Documents indigenous Indian recipes from informal descriptions into structured, heritage-style documentation with voice narration in the regional language.

## Features

- **Structured documentation:** Name, region, ingredients (local names), step-by-step method, cultural context
- **Heritage storytelling:** Warm, narrative style preserving cultural significance
- **Voice narration:** Full recipe narrated via Sarvam TTS
- **Follow-up questions:** Ask about variations, substitutions, techniques
- **11 languages** supported

## Run

```bash
cd examples/enterprise
streamlit run usecases/regional_recipe_narrator/app.py
```

## Architecture

```
regional_recipe_narrator/
├── app.py        # Streamlit UI
├── service.py    # Recipe documentation + narration
└── README.md
```
