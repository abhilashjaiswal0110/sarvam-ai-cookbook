# Mother Tongue Tutor

**APIs:** Translate + Transliterate + TTS

Helps children learn in their home language before transitioning to Hindi or English — using a three-step pipeline of translation, transliteration, and voice narration.

## Features

- **Word-by-word teaching:** Translate → Transliterate → Speak in both languages
- **Home-language-first:** Explanations always start in the child's mother tongue
- **Script bridging:** Shows new words in the child's home script via transliteration
- **Dual audio:** Hear the word in both home and target language
- **Interactive chat:** Follow-up questions with the tutor
- **11 language pairs** supported

## Run

```bash
cd examples/enterprise
streamlit run usecases/mother_tongue_tutor/app.py
```

## Architecture

```
mother_tongue_tutor/
├── app.py        # Streamlit UI
├── service.py    # Translate + Transliterate + TTS pipeline
└── README.md
```
