# ML vs LLM Trade-off Analysis

## Decision framework used

For each task, we asked 3 questions:
1. Does this need language generation or just classification?
2. How fast does it need to be? (ML = ms, LLM = seconds)
3. How important is explainability? (ML = SHAP, LLM = black box)

## Task-by-task decisions

### Sentiment Analysis → ML
- Binary classification (positive/negative) — no generation needed
- Needs to run on 86,738 reviews — LLM would cost hundreds of dollars
- SHAP explainability shows which words drove the prediction
- Logistic Regression inference: <1ms per review

### Fake Review Detection → ML  
- Tabular features (length, rating deviation, user frequency)
- No natural language generation required
- SHAP shows feature importance clearly
- XGBoost handles class imbalance well with scale_pos_weight

### Product Summary → LLM (few-shot)
- Requires synthesizing 15-20 reviews into coherent prose
- ML cannot generate natural language summaries
- Few-shot chosen: examples ensure consistent business-appropriate format

### Product Comparison → LLM (few-shot)
- Requires reasoning across two separate review sets
- Needs to identify relative strengths/weaknesses
- No ML approach handles multi-document reasoning

### Improvement Recommendations → LLM (CoT)
- Requires grouping complaints, ranking by frequency, suggesting fixes
- Multi-step reasoning benefits from chain-of-thought
- Business impact estimation requires language understanding

### Executive Report → LLM (instruction-based)
- Structured long-form document generation
- Requires integrating structured data (stats) with unstructured (reviews)
- Instruction-based prompting with explicit section headers works best

## Cost analysis
- ML inference: essentially free (local model)
- LLM inference: ~$0.001 per call (Gemini free tier for this project)
- At Amazon scale: ML for high-volume tasks, LLM for high-value tasks