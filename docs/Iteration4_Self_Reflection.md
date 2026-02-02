# Reloconomics - Iteration 4 Self-Reflection

**Student:** Jeremiah Williams
**Course:** Project & Portfolio IV (CSBS-AI)
**Date:** January 2026

---

## 1. What do you want to continue doing that worked well?

**Modular architecture** was the biggest win. Separating concerns into dedicated modules (`tax_calculator.py`, `cost_of_living.py`, `forecaster.py`, `affordability_map.py`) made the codebase manageable and each piece testable in isolation. When I needed to add the multi-horizon forecast comparison, I only had to modify the forecaster module - nothing else broke.

**JSON configuration files** for tax brackets, state rates, and cost indices worked excellently. Updating 2024 tax brackets or adding new metros requires zero code changes. This separation of data from logic is something I'll carry forward to every project.

**Iterative feature development** kept me on track. I built the core tax calculator first, verified it worked, then layered on cost of living, then forecasting, then the map. Each layer was functional before adding the next. This prevented the "everything is broken" paralysis that happens when you build too many interdependent features simultaneously.

**Consistent color semantics** (green = good/savings, red = bad/costs, blue = current, orange = target) made the UI intuitive without needing extensive labels. Users immediately understand what the colors mean across all visualizations.

---

## 2. What do you want to stop doing that is slowing/stopping production?

**Over-polishing individual features** before the whole product works. I spent almost two full days perfecting the affordability map's curved arc and bullseye animation when a simple marker would have sufficed. That time could have gone toward adding more metro areas or improving forecast accuracy.

**Manual testing only.** Without automated tests, every change required manually clicking through the entire app to verify nothing broke. This created fear of refactoring and slowed iteration speed significantly in the final week.

**Scope creep on "quick additions."** Adding the seasonal insights section seemed like a 30-minute task but turned into 3 hours when I decided it also needed best/worst months, comparison tips, and conditional formatting. I need to timebox features more strictly.

**Late-night coding sessions.** The bugs I introduced after midnight took twice as long to fix the next day. Better to stop at a clean commit point and start fresh.

---

## 3. What do you want to start doing that you think would improve production?

**Test-Driven Development (TDD)** for calculation-heavy modules. The tax calculator and forecaster have deterministic outputs - perfect candidates for unit tests. Writing tests first would have caught edge cases (negative discretionary income, zero salary) before they appeared in the UI.

**Design system documentation upfront.** Before writing UI code, I should define: color palette, spacing scale, typography hierarchy, and component patterns. This prevents the "tweak colors for an hour" syndrome.

**CI/CD from day one.** Setting up GitHub Actions to auto-deploy to Streamlit Cloud on push would eliminate manual deployment steps and ensure the live app always matches the repo.

**User testing earlier.** I only got tester feedback in Week 3. Getting eyes on the app in Week 1 would have caught UX issues before I'd built features on top of a confusing foundation.

**Daily standup notes** even for solo projects. A 2-minute written summary of "what I did, what's blocked, what's next" would help maintain focus and provide material for milestone videos.

---

## 4. What went right, and why?

**Tech stack selection was perfect for the problem:**
- **Streamlit** eliminated frontend complexity entirely. No HTML templates, no JavaScript, no CSS frameworks to configure. Python-only development meant I could focus on logic, not boilerplate.
- **scikit-learn** provided just enough ML capability to demonstrate competence without drowning in complexity. Linear Regression is interpretable and explainable - important for a demo project.
- **Plotly** handled all visualization needs with consistent, interactive charts. The choropleth map would have been painful to build from scratch.
- **JSON data files** made the app data-driven and easily updatable.

**Scope was achievable.** The original pitch focused on tax calculation + cost comparison + forecasting. I delivered all three core features to completion rather than half-implementing ten features.

**Deployment was painless.** Streamlit Cloud's GitHub integration meant deploying was literally one click. The app has been live and accessible throughout development, making it easy to share for testing.

**Documentation as I went** (docstrings, module headers, inline comments) paid off when revisiting code after a few days away. I could understand my own code immediately.

---

## 5. What went wrong, and why?

**UI polish took 3x longer than estimated.** I thought "make it look nice" was a half-day task. In reality:
- Getting responsive layouts for side-by-side comparisons took hours of tweaking
- Color consistency across charts, tables, and metrics required multiple passes
- Edge cases (deficit budgets, same-city selection) needed special UI handling

**The root cause:** I underestimated UI work because I hadn't done much frontend development before. Now I know to multiply UI time estimates by 3x.

**Forecast accuracy is mediocre.** Linear Regression with basic features produces reasonable trends but misses nuance. The model doesn't account for:
- Economic events (inflation spikes, housing market changes)
- Regional variations in seasonal patterns
- Category interdependencies (housing costs affect other spending)

**The root cause:** I prioritized "having ML" over "having good ML." A more sophisticated approach (ARIMA, Prophet, or even ensemble methods) would produce better forecasts but require more development time.

**Limited metro coverage.** Only 15 metros have full historical data for forecasting. Major cities like Boston, Seattle, and Phoenix are missing.

**The root cause:** Data collection is time-consuming. I sourced BLS Consumer Expenditure data manually, which doesn't scale. An automated data pipeline would solve this but wasn't in scope.

---

## 6. How can you use your experience this week to make your future development smoother?

**For PP5 and beyond:**

1. **Establish testing infrastructure in Week 1.** Even basic pytest setup with a few smoke tests will pay dividends. Budget 2-3 hours upfront; it saves 10+ hours of manual testing later.

2. **Create a UI component library before building features.** Define buttons, cards, metrics, and charts with consistent styling. Streamlit's theming helps, but having documented patterns prevents ad-hoc styling decisions.

3. **Timebox aggressively.** If a feature takes longer than 2x the estimate, stop and reassess. Either the scope is wrong, the approach is wrong, or the feature isn't worth it.

4. **Get user feedback in Week 1.** Even a rough prototype with placeholder data reveals UX issues. Testers don't need polish to give valuable feedback.

5. **Document deployment steps.** Even if it's "one click," write it down. Future-you will forget which settings to use.

6. **Commit frequently with meaningful messages.** Small commits make debugging easier and provide a clear history for milestone videos.

7. **Sleep on bugs.** If something isn't working after 30 minutes of debugging, step away. Fresh eyes in the morning solve problems faster than tired eyes at midnight.

**Specific technical learnings:**
- Streamlit's `st.container(border=True)` is great for visual grouping
- Plotly's `config` parameter can disable unwanted interactions (scroll zoom on maps)
- scikit-learn models need feature scaling for some algorithms but not Linear Regression
- JSON is fine for small datasets; larger data needs SQLite or similar

**The meta-lesson:** Building software is 30% coding and 70% everything else (planning, testing, debugging, polishing, documenting). Budget accordingly.
