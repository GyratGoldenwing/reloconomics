"""
Machine Learning Forecaster Module for Reloconomics

Uses scikit-learn to predict future monthly expenses based on historical data.
Demonstrates core ML concepts: feature engineering, model training, and inference.

Key ML Concepts Demonstrated:
- Feature Engineering: Creating predictive features from raw data
  - Lag features (t-1, t-2, t-3): Capture recent trends
  - Seasonality (month): Capture annual patterns
  - Trend (time index): Capture long-term price increases

- Model Training: Linear Regression with train/test split
- Evaluation Metrics: MAE (Mean Absolute Error), R² (coefficient of determination)
- Prediction: Generate actual dollar forecasts for future months

Author: Jeremiah Williams
Course: Project & Portfolio IV (CSBS-AI)
"""

import json
from pathlib import Path
import numpy as np

# =============================================================================
# SCIKIT-LEARN IMPORTS
# =============================================================================

# LinearRegression: Simple, interpretable model for time series
from sklearn.linear_model import LinearRegression

# Evaluation metrics to measure prediction accuracy
from sklearn.metrics import mean_absolute_error, r2_score


# =============================================================================
# DATA LOADING
# =============================================================================

def load_historical_expenses() -> dict:
    """
    Load historical expense data from JSON file (60 months of data).

    Returns:
        Dictionary with historical expense data, or empty dict on error
    """
    try:
        data_path = Path(__file__).parent.parent / "data" / "historical_expenses.json"
        with open(data_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"data": {}, "error": "Historical data file not found"}
    except json.JSONDecodeError:
        return {"data": {}, "error": "Invalid JSON in data file"}


def get_available_metros() -> list:
    """Get list of metros with historical expense data available for forecasting."""
    data = load_historical_expenses()
    return list(data["data"].keys())


# =============================================================================
# FEATURE ENGINEERING
# =============================================================================

def prepare_features(values: list, dates: list) -> tuple:
    """
    Create features for expense forecasting.

    Feature Engineering:
    - Lag features: expense at t-1, t-2, t-3
    - Seasonality: month of year (captures seasonal patterns)
    - Trend: linear time index

    Returns:
        X: Feature matrix
        y: Target values (actual dollar amounts)
    """
    n = len(values)

    if n < 4:
        return None, None

    X = []
    y = []

    for i in range(3, n):
        # Extract month from date for seasonality
        month = int(dates[i].split("-")[1])

        features = [
            values[i-1],      # lag_1: last month
            values[i-2],      # lag_2: 2 months ago
            values[i-3],      # lag_3: 3 months ago
            month,            # seasonality: month of year (1-12)
            i                 # trend: time index
        ]
        X.append(features)
        y.append(values[i])

    return np.array(X), np.array(y)


# =============================================================================
# MODEL TRAINING
# =============================================================================

def train_expense_model(metro: str, category: str) -> dict:
    """
    Train a model to predict a specific expense category.

    Args:
        metro: Metropolitan area name
        category: Expense category (housing, food, etc.)

    Returns:
        Trained model with metrics, or error dict on failure
    """
    try:
        data = load_historical_expenses()

        if "error" in data:
            return {"error": data["error"]}

        if metro not in data["data"]:
            return {"error": f"No data for {metro}"}

        metro_data = data["data"][metro]
        dates = [d["date"] for d in metro_data]
        values = [d[category] for d in metro_data]

        X, y = prepare_features(values, dates)

        if X is None:
            return {"error": "Insufficient data"}

        # Train/test split - last 6 months for validation
        split_idx = len(X) - 6
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        return {
            "model": model,
            "mae": round(mae, 2),
            "r2": round(r2, 4),
            "last_values": values[-3:],
            "last_date": dates[-1]
        }

    except Exception as e:
        return {"error": f"Model training failed: {str(e)}"}


# =============================================================================
# EXPENSE FORECASTING
# =============================================================================

def forecast_expenses(metro: str, months_ahead: int = 6) -> dict:
    """
    Forecast all expense categories for a metro area.

    Args:
        metro: Metropolitan area name
        months_ahead: Number of months to forecast

    Returns:
        Forecasted expenses in actual dollars
    """
    data = load_historical_expenses()

    if metro not in data["data"]:
        return {"error": f"No data for {metro}"}

    categories = ["housing", "food", "transportation", "utilities", "healthcare"]
    metro_data = data["data"][metro]
    dates = [d["date"] for d in metro_data]

    # Generate forecast dates
    last_date = dates[-1]
    year, month = map(int, last_date.split("-"))
    forecast_dates = []
    for i in range(1, months_ahead + 1):
        new_month = month + i
        new_year = year
        while new_month > 12:
            new_month -= 12
            new_year += 1
        forecast_dates.append(f"{new_year}-{new_month:02d}")

    # Forecast each category
    forecasts = {}
    metrics = {}

    for category in categories:
        result = train_expense_model(metro, category)

        if "error" in result:
            continue

        model = result["model"]
        current_values = result["last_values"]
        trend_idx = len(metro_data)

        category_forecast = []
        for i, date in enumerate(forecast_dates):
            forecast_month = int(date.split("-")[1])

            features = [
                current_values[-1],
                current_values[-2],
                current_values[-3],
                forecast_month,  # Seasonality
                trend_idx + i    # Trend
            ]

            pred = max(0, model.predict([features])[0])  # No negative expenses
            category_forecast.append(round(pred, 0))

            # Update rolling window
            current_values = current_values[1:] + [pred]

        forecasts[category] = category_forecast
        metrics[category] = {"mae": result["mae"], "r2": result["r2"]}

    # Calculate totals
    forecasts["total"] = [
        sum(forecasts[cat][i] for cat in categories)
        for i in range(months_ahead)
    ]

    # Get historical totals for chart
    historical_totals = [
        sum(d[cat] for cat in categories)
        for d in metro_data
    ]

    return {
        "metro": metro,
        "historical_dates": dates,
        "historical_totals": historical_totals,
        "historical_by_category": {
            cat: [d[cat] for d in metro_data]
            for cat in categories
        },
        "forecast_dates": forecast_dates,
        "forecast_by_category": forecasts,
        "forecast_totals": forecasts["total"],
        "metrics": metrics,
        "model_type": "Linear Regression",
        "features": ["lag_1", "lag_2", "lag_3", "month (seasonality)", "trend"]
    }


def get_seasonal_insights(metro: str) -> dict:
    """
    Analyze seasonal patterns in expense data.

    Returns insights like "Housing peaks in July" or "Utilities highest in August"
    """
    data = load_historical_expenses()

    if metro not in data["data"]:
        return {"error": f"No data for {metro}"}

    metro_data = data["data"][metro]
    categories = ["housing", "food", "transportation", "utilities", "healthcare"]

    insights = {}

    for category in categories:
        # Group by month and find averages
        monthly_avgs = {}
        for record in metro_data:
            month = int(record["date"].split("-")[1])
            if month not in monthly_avgs:
                monthly_avgs[month] = []
            monthly_avgs[month].append(record[category])

        # Calculate averages
        for month in monthly_avgs:
            monthly_avgs[month] = np.mean(monthly_avgs[month])

        # Find peak and low months
        peak_month = max(monthly_avgs, key=monthly_avgs.get)
        low_month = min(monthly_avgs, key=monthly_avgs.get)

        month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        peak_val = monthly_avgs[peak_month]
        low_val = monthly_avgs[low_month]
        variance = ((peak_val - low_val) / low_val) * 100

        insights[category] = {
            "peak_month": month_names[peak_month],
            "peak_value": round(peak_val, 0),
            "low_month": month_names[low_month],
            "low_value": round(low_val, 0),
            "seasonal_variance": round(variance, 1)
        }

    return {
        "metro": metro,
        "insights": insights,
        "seasonal_notes": data.get("seasonal_notes", {})
    }


# =============================================================================
# MULTI-HORIZON FORECAST COMPARISON
# =============================================================================

def compare_forecasts(metro1: str, metro2: str, horizons: list = [3, 6, 9, 12]) -> dict:
    """
    Compare forecasted expenses between two metros at multiple time horizons.

    Args:
        metro1: First metro (current location)
        metro2: Second metro (target location)
        horizons: List of months ahead to forecast (default: 3, 6, 9, 12)

    Returns:
        Comparison data with forecasts at each horizon by category
    """
    categories = ["housing", "food", "transportation", "utilities", "healthcare"]
    max_horizon = max(horizons)

    # Get forecasts for both metros
    forecast1 = forecast_expenses(metro1, months_ahead=max_horizon)
    forecast2 = forecast_expenses(metro2, months_ahead=max_horizon)

    if "error" in forecast1:
        return {"error": f"Could not forecast {metro1}: {forecast1['error']}"}
    if "error" in forecast2:
        return {"error": f"Could not forecast {metro2}: {forecast2['error']}"}

    # Build comparison structure
    comparison = {
        "metro1": metro1,
        "metro2": metro2,
        "horizons": horizons,
        "categories": {},
        "totals": {}
    }

    # Current values (latest historical)
    current1 = {cat: forecast1["historical_by_category"][cat][-1] for cat in categories}
    current2 = {cat: forecast2["historical_by_category"][cat][-1] for cat in categories}

    for category in categories:
        comparison["categories"][category] = {
            "current": {
                "metro1": round(current1[category], 0),
                "metro2": round(current2[category], 0),
                "diff": round(current2[category] - current1[category], 0)
            },
            "forecasts": {}
        }

        for h in horizons:
            # Get forecast value at horizon h (index h-1 since 0-indexed)
            val1 = forecast1["forecast_by_category"][category][h - 1]
            val2 = forecast2["forecast_by_category"][category][h - 1]

            comparison["categories"][category]["forecasts"][h] = {
                "metro1": round(val1, 0),
                "metro2": round(val2, 0),
                "diff": round(val2 - val1, 0),
                "diff_pct": round(((val2 - val1) / val1) * 100, 1) if val1 > 0 else 0
            }

    # Calculate totals at each horizon
    comparison["totals"]["current"] = {
        "metro1": round(sum(current1.values()), 0),
        "metro2": round(sum(current2.values()), 0),
        "diff": round(sum(current2.values()) - sum(current1.values()), 0)
    }

    for h in horizons:
        total1 = sum(forecast1["forecast_by_category"][cat][h - 1] for cat in categories)
        total2 = sum(forecast2["forecast_by_category"][cat][h - 1] for cat in categories)

        comparison["totals"][h] = {
            "metro1": round(total1, 0),
            "metro2": round(total2, 0),
            "diff": round(total2 - total1, 0),
            "diff_pct": round(((total2 - total1) / total1) * 100, 1) if total1 > 0 else 0
        }

    # Add forecast dates for reference
    comparison["forecast_dates"] = {
        h: forecast1["forecast_dates"][h - 1] for h in horizons
    }

    return comparison
