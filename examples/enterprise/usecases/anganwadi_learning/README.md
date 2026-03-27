# Anganwadi Learning Assistant

**APIs:** TTS + Chat Completions

Early-learning content engine for India's Anganwadi centres — generates and narrates stories, nursery rhymes, alphabet lessons, and more in the child's mother tongue.

## Features

- **7 content types:** Stories, Rhymes, Alphabet, Numbers, Colours, Animals, Good Habits
- **Voice narration:** Every piece of content is read aloud via Sarvam TTS
- **Age-appropriate:** Vocabulary tuned for ages 3-6, culturally familiar examples
- **Interactive follow-ups:** Children (or caregivers) can ask for more
- **Content safety:** No scary/violent content; positive morals built in

## Run

```bash
cd examples/enterprise
streamlit run usecases/anganwadi_learning/app.py
```

## Architecture

```
anganwadi_learning/
├── app.py        # Streamlit UI
├── service.py    # Content generation + narration logic
└── README.md
```
