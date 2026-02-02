# Reloconomics - Iteration 4 Video Script

**Target Length:** 8-10 minutes
**Due:** Sunday, February 1st, 2026

---

## INTRO (30 seconds)

"Hi, I'm Jeremiah Williams, and this is my Iteration 4 final presentation for Reloconomics - a predictive cost of living comparison tool I built for Project & Portfolio IV.

Reloconomics helps job seekers compare salaries across US cities by showing true take-home pay after taxes, expense breakdowns, and ML-powered cost forecasts. Let me walk you through the finished product."

---

## SECTION 1: APP DEMONSTRATION (3-4 minutes)

### 1.1 Overview & User Flow

"The app runs on Streamlit and is deployed live at [show URL]. Here's how a typical user would interact with it.

First, you enter your annual salary in the sidebar - let's use $95,000. Then select your tax filing status. The app supports all four IRS filing statuses: single, married filing jointly, married filing separately, and head of household.

Next, pick your current city and a target city you're considering. Let's compare Austin, Texas to San Francisco, California."

### 1.2 Take-Home Pay Comparison

"The first thing users see is the take-home pay comparison. This shows estimated annual and monthly take-home after federal tax, state tax, and FICA.

You can expand the tax breakdown to see exactly how taxes are calculated - the standard deduction, federal tax by bracket, state tax rate, and Social Security plus Medicare.

Notice the color coding: green indicates you keep more money, red means you keep less. San Francisco has higher state taxes, so take-home is lower."

### 1.3 Monthly Expense Comparison

"Below that is the monthly expense comparison table. This breaks down costs by category: housing, food, transportation, healthcare, and utilities.

The difference column shows both dollar amounts and percentages, with color indicators. San Francisco housing is significantly more expensive.

I also added percentage breakdown bars showing how your budget is allocated in each city."

### 1.4 Visual Charts

"The visual comparison section has two charts:
- A grouped bar chart comparing expenses by category
- Dual pie charts showing budget allocation - expenses vs discretionary income

If expenses exceed take-home pay at a given salary, the app shows a budget alert warning."

### 1.5 Affordability Heat Map

"The affordability map is a US choropleth showing cost of living relative to your current location. Green states are cheaper, red states are more expensive.

There's a curved arc connecting your current state to your target, with a bullseye marker. The legend explains the color scale."

### 1.6 ML Forecasting

"This is the ML-powered section. The app uses scikit-learn Linear Regression to forecast expenses 12 months out.

Features used: three months of lag data, seasonality by month, and a trend index. You can see historical data as a solid line and forecasted data as a dashed line.

The multi-horizon comparison table shows forecasts at 3, 6, 9, and 12 months with tabs. Below that are seasonal insights showing which months are cheapest and most expensive for each city."

### 1.7 Bottom Line

"Finally, there's a bottom-line summary that tells you which city gives you more discretionary income - the money left over after all expenses."

---

## SECTION 2: CODE REVIEW (2-3 minutes)

### 2.1 Project Structure

"Let me show you the codebase. The project has a clean modular structure:
- `app.py` - main Streamlit application (860 lines)
- `utils/` folder with four modules:
  - `tax_calculator.py` - federal and state tax calculations
  - `cost_of_living.py` - expense calculations using BEA price indices
  - `forecaster.py` - scikit-learn ML module
  - `affordability_map.py` - Plotly choropleth generation
- `data/` folder with JSON files for tax brackets, state taxes, cost indices, and historical expenses"

### 2.2 Tax Calculator Module

"The tax calculator implements progressive federal tax brackets. The `calculate_federal_tax` function takes gross income and filing status, applies the standard deduction, then loops through each bracket calculating tax at that rate. This is how real tax calculations work - each bracket only applies to income within that range.

State taxes are simpler - most are flat rates loaded from JSON. FICA calculates Social Security (capped at the wage base) plus Medicare with the additional 0.9% over $200k."

### 2.3 ML Forecaster Module

"The forecaster module demonstrates key ML concepts. The `prepare_features` function creates the feature matrix:
- Lag features: expenses from t-1, t-2, t-3
- Seasonality: month of year (1-12)
- Trend: linear time index

Training uses an 80/20 split with scikit-learn's LinearRegression. The model predicts actual dollar amounts, not percentages. I evaluate with MAE and R-squared.

The `forecast_expenses` function chains predictions forward - each forecast becomes input for the next month's lag features."

### 2.4 Design Decisions

"Some key design decisions:
- JSON data files for easy updates without code changes
- Consistent color palette defined once and reused everywhere
- Edge case handling - negative discretionary income shows a deficit warning
- All calculations happen server-side, no client-side JavaScript needed"

---

## SECTION 3: TRELLO REVIEW (1 minute)

"Here's my Trello board. [Show board]

The columns are: Backlog, In Progress, Testing, and Done.

For Iteration 4, I focused on:
- [Card 1] Visual polish - containers, typography, theme consistency
- [Card 2] UX improvements - section headers, percentage bars
- [Card 3] Color semantics - consistent green/red meaning across all visualizations

All cards have descriptions, acceptance criteria, and are marked complete. I also have a backlog of stretch goals I didn't get to, like additional metro areas and a savings calculator."

---

## SECTION 4: GITHUB REVIEW (1 minute)

"Let me show the GitHub repository. [Show repo]

You can see commits across multiple days this week:
- [Date 1]: Visual polish commit
- [Date 2]: UX improvements
- [Date 3]: Final cleanup

Commit messages are descriptive - they explain what changed, not just 'fixed stuff.'

The repo includes a README, requirements.txt, and .gitignore. The app is deployed via Streamlit Cloud connected to this repo."

---

## SECTION 5: SELF-REFLECTION (2 minutes)

### What do you want to continue doing that worked well?

"Modular code organization worked really well. Having separate modules for tax calculation, cost of living, and forecasting made the code maintainable and testable. I also want to continue using JSON for configuration data - it's easy to update without touching code."

### What do you want to stop doing that is slowing/stopping production?

"I need to stop perfecting features before moving on. I spent too much time tweaking the affordability map's visual details when I could have been adding more metros or improving the forecasting accuracy."

### What do you want to start doing that you think would improve production?

"I want to start writing tests earlier. I didn't have automated tests for this project, which made me nervous about refactoring. Unit tests for the tax calculator would have saved time debugging edge cases."

### What went right, and why?

"The tech stack choice was spot-on. Streamlit let me build a polished UI quickly without frontend complexity. scikit-learn was the right level of ML complexity for a demonstration - powerful enough to be meaningful, simple enough to explain."

### What went wrong, and why?

"I underestimated how much time UI polish would take. Getting colors, spacing, and responsive layouts right took almost as long as the core functionality. Next time I'll budget more time for polish or use a pre-built component library."

### How can you use your experience this week to make your future development smoother?

"For PP5, I'll set up CI/CD from day one. Having automatic deploys on push would have saved the manual deploy steps I did this week. I'll also create a design system document upfront defining colors, spacing, and typography before writing any UI code."

---

## OUTRO (30 seconds)

"That's Reloconomics - a predictive cost of living comparison tool with real tax calculations, expense breakdowns, and ML-powered forecasting.

The app is live at [URL] if you want to try it. Thanks for watching, and I'm happy to answer any questions."

---

## VIDEO CHECKLIST

- [ ] App demonstration shows all features
- [ ] Code review explains logic, not just reads code
- [ ] Trello board shown with updated cards
- [ ] GitHub repo shown with 3+ days of commits
- [ ] All 6 self-reflection questions answered
- [ ] Video is 8-10 minutes
- [ ] Audio is clear
- [ ] Screen is visible and readable
