# Iteration 2 Video Checklist

## App Demonstration
| Requirement | Status | Notes |
|-------------|--------|-------|
| Show progress made during the week | ⬜ | Demo: heat map, forecasting, best/worst months |
| Explain how it works from user's perspective | ⬜ | Walk through input → tax calc → comparison → forecast |

## Code Review
| Requirement | Status | Notes |
|-------------|--------|-------|
| Show code written during the week | ⬜ | Show `forecaster.py`, `affordability_map.py` |
| Explain how it works (developer perspective) | ⬜ | Explain feature engineering, model training |
| DO NOT JUST READ THE CODE | ⬜ | Explain the "why" - lag features, seasonality, etc. |

## Trello
| Requirement | Status | Notes |
|-------------|--------|-------|
| Entire board confirmed updated | ⬜ | Move completed cards to Done |
| Any new cards are noted | ⬜ | Mention cards added this week |
| Any changes to existing cards are noted | ⬜ | Mention scope changes if any |

## GitHub
| Requirement | Status | Notes |
|-------------|--------|-------|
| At least 3 days of pushes confirmed | ✅ | Jan 13, Jan 15, Jan 18 |

## Self-Reflection (6 Questions)

### 1. What do you want to continue doing that worked well?
"Iterating based on visual feedback - the color fixes came from actually using the app. Also, using official government data sources gave the project credibility."

### 2. What do you want to stop doing that is slowing/stopping production?
"Over-planning ML experiments before validating the simple approach works. I pitched comparing 5 model types but Linear Regression was sufficient."

### 3. What do you want to start doing that you think would improve production?
"Testing on mobile viewport earlier - Streamlit responsive layout needs attention. Also, creating sample data earlier to unblock feature development."

### 4. What went right, and why?
"Core features work as pitched - tax calculation, expense comparison, ML forecasting all function correctly. Scoping to 15 metros kept data manageable while still demonstrating the concept."

### 5. What went wrong, and why?
"Underestimated data prep time. Generating 60 months × 15 cities × 5 categories = 4,500 data points took significant effort. The heat map color logic also required several iterations to get the UX right."

### 6. How can you use your experience this week to make your future development smoother?
"Start with data availability, then design features around it - not the reverse. Also, get visual feedback early and often rather than building features in isolation."

---

## Features Completed This Week
- State-level affordability heat map with relative coloring
- Curved arc and bullseye markers showing relocation path
- Multi-horizon forecast comparison (3, 6, 9, 12 months)
- Best/worst 3 months budgeting indicator
- Historical data for all 15 metros (was 8, now complete)
- Color indicator UX fixes (green=good, red=bad consistently)

## Features Cut (With Justification)
- Additional expense categories (entertainment, childcare) - Core 5 demonstrate concept
- Dependent/children tax credits - Adds complexity without changing comparison
- PDF export - Nice-to-have, doesn't demonstrate ML
- Multiple ML models comparison - Linear Regression performed well enough
- Confidence intervals - Adds visual complexity without improving decisions
