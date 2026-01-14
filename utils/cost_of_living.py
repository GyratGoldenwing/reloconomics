"""
Cost of Living Module for Reloconomics

Provides cost estimates based on Bureau of Economic Analysis (BEA)
Regional Price Parities. Uses index values where 100 = national average.

Key Features:
- Regional expense calculations (housing, food, transport, healthcare, utilities)
- Metro-to-metro cost comparisons
- Purchasing power analysis (discretionary income after expenses)

Data Source: BEA Regional Price Parities (public government data)

Author: Jeremiah Williams
Course: Project & Portfolio IV (CSBS-AI)
"""

import json
from pathlib import Path

# =============================================================================
# DATA LOADING
# =============================================================================

DATA_DIR = Path(__file__).parent.parent / "data"


def load_cost_data():
    """Load cost of living indices and national averages from JSON."""
    with open(DATA_DIR / "cost_of_living.json", "r") as f:
        return json.load(f)


# Load data at module initialization for performance
COST_DATA = load_cost_data()


def get_metros() -> list:
    """Return list of available metro areas."""
    return sorted(COST_DATA["metros"].keys())


def get_metro_data(metro: str) -> dict:
    """Get cost of living data for a specific metro."""
    return COST_DATA["metros"].get(metro)


def calculate_expenses(metro: str, monthly_budget: float = None) -> dict:
    """
    Calculate estimated monthly expenses for a metro area.

    Args:
        metro: Metro area name
        monthly_budget: Optional monthly budget to allocate

    Returns:
        Dictionary with expense breakdown
    """
    metro_data = get_metro_data(metro)
    if not metro_data:
        raise ValueError(f"Metro not found: {metro}")

    national_avg = COST_DATA["national_average_expenses"]

    # Calculate expenses based on index values
    expenses = {}
    total = 0

    for category in ["housing", "food", "transportation", "healthcare", "utilities"]:
        index = metro_data.get(category, 100) / 100
        base = national_avg[category]
        amount = base * index
        expenses[category] = round(amount, 2)
        total += amount

    expenses["total"] = round(total, 2)
    expenses["overall_index"] = metro_data["overall_index"]

    return expenses


def compare_metros(metro1: str, metro2: str) -> dict:
    """
    Compare cost of living between two metros.

    Args:
        metro1: First metro area
        metro2: Second metro area

    Returns:
        Comparison data
    """
    expenses1 = calculate_expenses(metro1)
    expenses2 = calculate_expenses(metro2)

    comparison = {
        "metro1": {
            "name": metro1,
            "expenses": expenses1
        },
        "metro2": {
            "name": metro2,
            "expenses": expenses2
        },
        "differences": {}
    }

    for category in ["housing", "food", "transportation", "healthcare", "utilities", "total"]:
        diff = expenses2[category] - expenses1[category]
        pct = (diff / expenses1[category] * 100) if expenses1[category] > 0 else 0
        comparison["differences"][category] = {
            "amount": round(diff, 2),
            "percent": round(pct, 1)
        }

    return comparison


def calculate_purchasing_power(take_home_monthly: float, metro: str) -> dict:
    """
    Calculate purchasing power after expenses.

    Args:
        take_home_monthly: Monthly take-home pay
        metro: Metro area

    Returns:
        Purchasing power analysis
    """
    expenses = calculate_expenses(metro)
    total_expenses = expenses["total"]
    discretionary = take_home_monthly - total_expenses

    return {
        "take_home_monthly": take_home_monthly,
        "total_expenses": total_expenses,
        "discretionary_income": round(discretionary, 2),
        "expense_ratio": round((total_expenses / take_home_monthly * 100), 1) if take_home_monthly > 0 else 0,
        "expenses_breakdown": expenses
    }
