# Changelog

All notable changes to Reloconomics are documented here.

## [1.0.0] - 2026-01-31

### Features
- Federal + state + FICA tax calculations for all 50 US states
- Take-home pay comparison by filing status (single, married, head of household)
- Monthly expense breakdown: housing, food, transportation, healthcare, utilities
- ML-powered expense forecasting (3, 6, 9, 12 month horizons)
- US affordability heat map with curved arc visualization
- Seasonal insights: best/worst months for budgeting
- Budget allocation charts (pie and bar)

### Technical
- Streamlit framework with wide layout
- scikit-learn Linear Regression for forecasting
- Plotly interactive visualizations
- JSON-based configuration for easy data updates
- Deployed on Streamlit Community Cloud

## [0.9.0] - 2026-01-28

### Added
- Visual polish: containers, borders, typography
- UX improvements: section headers, percentage bars
- Consistent color semantics (green=savings, red=costs)

## [0.8.0] - 2026-01-18

### Added
- Historical expense data for 7 additional metros
- Multi-horizon forecast comparison table with tabs

## [0.7.0] - 2026-01-15

### Added
- Best/worst 3 months comparison for budgeting
- State-level affordability heat map
- Curved arc and bullseye marker on map
- Input validation for salary and city selection
- Error handling in ML forecaster

## [0.1.0] - 2026-01-13

### Added
- Initial release: R&D demonstrator
- Basic tax calculator
- Cost of living comparison
- Simple forecasting
