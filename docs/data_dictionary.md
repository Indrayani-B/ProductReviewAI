# Data Dictionary

## Table: reviews (raw)
| Column           | Type    | Description                        |
|------------------|---------|------------------------------------|
| rating           | float   | 1.0 to 5.0 star rating             |
| title            | string  | review title                       |
| text             | string  | review body                        |
| asin             | string  | product ID                         |
| parent_asin      | string  | parent product ID (groups variants)|
| user_id          | string  | reviewer ID                        |
| timestamp        | int     | epoch milliseconds                 |
| helpful_vote     | int     | number of helpful votes            |
| verified_purchase| bool    | whether purchase was verified      |

## Table: reviews_clean (processed)
Same columns plus:
| Column           | Type    | Description                        |
|------------------|---------|------------------------------------|
| sentiment        | int     | 1=positive (4-5★), 0=negative(1-2★)|
| review_length    | int     | word count of review text          |
| title_length     | int     | word count of title                |
| month            | string  | review month (2021-03 format)      |
| year             | int     | review year                        |

## Cleaning decisions
- Removed exact duplicates: 12 rows
- Removed same user + same text: 2,178 rows (bot behavior)
- Removed rating 3.0: 7,064 rows (neutral, ambiguous for binary classification)
- Removed reviews under 3 words: 4,020 rows (no sentiment signal)
- Removed HTML tags (<br>) from text: regex clean
- Kept all reviews 3+ words including long ones (max 2665 words)

## Key findings from EDA
- Dataset heavily skewed: 86% positive, 14% negative
- Fix: use class_weight='balanced' in all sklearn models
- review_length ↔ verified_purchase = -0.33 (fake review signal)
- December 2022 peak (holiday season)
- March 2023 incomplete (dataset collection cutoff)
- Bigrams needed: "doesn't work" ≠ "work"