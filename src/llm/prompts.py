"""
All prompts for the project live here, organized by task and strategy.
This is the file you show in interviews when asked "how did you do prompt engineering?"
"""

# ─────────────────────────────────────────────────────────────────
# TASK 1: Product Summary
# ─────────────────────────────────────────────────────────────────

SUMMARY_ZERO_SHOT = """Summarize the following customer reviews for a product 
in 3-4 sentences. Focus on overall sentiment and key themes.

Reviews:
{reviews}

Summary:"""

SUMMARY_FEW_SHOT = """Summarize customer reviews into a short, complete business summary of 3-4 full sentences.

Example 1:
Reviews: "Great battery life, lasts all day." "Camera is blurry in low light." 
"Love the design, very sleek."
Summary: Customers praise the long battery life and sleek design, but report 
issues with low-light camera performance. Overall sentiment leans positive, 
with camera quality as the main area for improvement.

Example 2:
Reviews: "Stopped working after 2 weeks." "Cheaply made, broke easily." 
"Customer service was unhelpful."
Summary: Customers report significant reliability issues, with the product 
breaking quickly and poor customer service experiences. This suggests urgent 
attention is needed on build quality and support responsiveness.

Now summarize these reviews in 3-4 complete sentences:
{reviews}

Summary:"""

SUMMARY_COT = """Analyze the following customer reviews step by step.

Reviews:
{reviews}

Step 1: List the main topics customers mention (e.g., battery, camera, price).
Step 2: For each topic, determine if feedback is mostly positive or negative.
Step 3: Identify the single most important theme overall.
Step 4: Write a 3-4 sentence summary based on your analysis.

Provide only the final summary as your answer."""


# ─────────────────────────────────────────────────────────────────
# TASK 2: Product Comparison
# ─────────────────────────────────────────────────────────────────

COMPARE_ZERO_SHOT = """Compare these two products based on customer reviews. 
Provide pros, cons, and a recommendation.

Product A reviews:
{reviews_a}

Product B reviews:
{reviews_b}

Comparison:"""

COMPARE_FEW_SHOT = """Compare two products based on customer reviews using this format:
Pros of A / Cons of A / Pros of B / Cons of B / Recommendation

Example:
Product A reviews: "Fast charging." "Bit expensive."
Product B reviews: "Affordable." "Charges slowly."

Pros of A: Fast charging speed
Cons of A: Higher price point
Pros of B: Budget-friendly
Cons of B: Slower charging
Recommendation: Choose A for speed, B for budget-conscious buyers.

Now compare:
Product A reviews: {reviews_a}
Product B reviews: {reviews_b}"""

COMPARE_COT = """Compare two products step by step using their customer reviews.

Product A reviews:
{reviews_a}

Product B reviews:
{reviews_b}

Step 1: Identify the main strengths of Product A.
Step 2: Identify the main weaknesses of Product A.
Step 3: Identify the main strengths of Product B.
Step 4: Identify the main weaknesses of Product B.
Step 5: Based on steps 1-4, give a clear recommendation on which 
product suits which type of buyer.

Provide your final comparison in this format:
Pros of A: ...
Cons of A: ...
Pros of B: ...
Cons of B: ...
Recommendation: ..."""


# ─────────────────────────────────────────────────────────────────
# TASK 3: Improvement Recommendations
# ─────────────────────────────────────────────────────────────────

RECOMMEND_ZERO_SHOT = """Based on these customer reviews, suggest the top 5 
improvements the company should make to this product. List them in order 
of priority.

Reviews:
{reviews}

Top 5 improvements:"""

RECOMMEND_FEW_SHOT = """Suggest product improvements based on customer reviews.

Example:
Reviews: "Battery drains fast." "Battery drains fast." "Screen cracks easily." 
"Love the design."
Improvements:
1. Improve battery life (High priority — most frequent complaint)
2. Strengthen screen durability (Medium priority)
3. Keep current design (customers love it, no change needed)

Now suggest improvements for these reviews:
{reviews}

Improvements:"""

RECOMMEND_COT = """Analyze these customer reviews to recommend product improvements.

Reviews:
{reviews}

Step 1: Group complaints by theme (e.g., battery, build quality, price).
Step 2: Count roughly how often each theme appears.
Step 3: Rank themes by frequency and severity of complaint.
Step 4: For each of the top 5 themes, write a specific, actionable 
improvement recommendation with a priority level (High/Medium/Low) 
and estimated customer satisfaction impact.

Provide your final answer as a numbered list of 5 improvements."""


# ─────────────────────────────────────────────────────────────────
# TASK 4: Executive Report
# ─────────────────────────────────────────────────────────────────

REPORT_INSTRUCTION = """You are a business analyst preparing an executive 
report for a product management team at an e-commerce company.

Based on the following data, write a structured executive report with 
these sections: Executive Summary, Overall Customer Satisfaction, 
Major Complaints, Strengths, Weaknesses, Risk Analysis, and Recommendations.

Product: {product_name}
Total reviews analyzed: {review_count}
Average rating: {avg_rating}
Positive sentiment: {positive_pct}%
Negative sentiment: {negative_pct}%

Top customer aspects mentioned:
{aspects_summary}

Sample reviews:
{sample_reviews}

Write the executive report now, using clear business language 
appropriate for a product management audience."""