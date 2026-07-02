# 🛒 Product Review AI

AI-powered customer review intelligence platform for e-commerce.
Built to demonstrate end-to-end ML + LLM system design.

## What it does
- Sentiment analysis on customer reviews (86% accuracy)
- Fake review detection using weak supervision
- Aspect-based sentiment extraction (battery, camera, price...)
- LLM-powered product summaries, comparisons, recommendations
- Executive report generation with PDF export
- 6-page interactive dashboard

## Tech Stack
| Layer | Technology |
|-------|-----------|
| ML Models | Logistic Regression, Random Forest, XGBoost |
| LLM | Google Gemini 2.5 Flash (REST API) |
| Prompt Engineering | Zero-shot, Few-shot, Chain-of-Thought |
| NLP | spaCy, TF-IDF |
| Explainability | SHAP |
| Experiment Tracking | MLflow |
| Backend API | FastAPI + Uvicorn |
| Dashboard | Streamlit |
| Database | SQLite |
| Containerization | Docker |

## ML vs LLM Design Decisions
| Task | Approach | Why |
|------|----------|-----|
| Sentiment classification | ML (Logistic Regression) | Fast, cheap, interpretable with SHAP |
| Fake review detection | ML (XGBoost) | Tabular features, no text generation needed |
| Product summary | LLM (few-shot) | Requires language understanding and synthesis |
| Product comparison | LLM (few-shot) | Requires reasoning across two inputs |
| Improvement recommendations | LLM (CoT) | Requires prioritization and business reasoning |
| Executive report | LLM (instruction) | Requires structured long-form generation |

## Dataset
Amazon Electronics Reviews — 100,000 reviews loaded, 86,738 after cleaning.

## Setup
```bash
conda create -n product_review_ai python=3.10
conda activate product_review_ai
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env  # add your GEMINI_API_KEY
```

## Run
```bash
# terminal 1 — API
uvicorn src.api.main:app --port 8000

# terminal 2 — dashboard  
streamlit run src/dashboard/app.py
```

## API docs
Visit http://localhost:8000/docs for interactive API documentation.

## Key findings from EDA
- Dataset 86:14 positive:negative (handled with class_weight='balanced')
- review_length ↔ verified_purchase = -0.33 (fake review signal)
- HTML artifacts (<br>) found and cleaned from review text
- December 2022 review spike (holiday season)

## Model selection reasoning
Logistic Regression chosen over Random Forest (higher F1) because
it has 3x fewer False Positives (324 vs 1,191). In retail, missing
real negative reviews is more costly than false alarms.

## Experiment tracking
MLflow tracks all training runs. View with:
```bash
mlflow ui
```
Visit http://localhost:5000