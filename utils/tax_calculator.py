"""
Tax Calculation Module for Reloconomics

Calculates federal and state income tax estimates based on filing status.
Implements progressive tax bracket calculations for federal taxes and
flat/graduated rates for state taxes.

Key Features:
- Federal tax with progressive brackets (2024 rates)
- State income tax (all 50 states)
- FICA taxes (Social Security + Medicare)
- Take-home pay estimation

Author: Jeremiah Williams
Course: Project & Portfolio IV (CSBS-AI)
"""

import json
from pathlib import Path

# =============================================================================
# DATA LOADING
# =============================================================================

# Path to JSON data files
DATA_DIR = Path(__file__).parent.parent / "data"

def load_federal_brackets():
    """Load federal tax brackets from JSON file."""
    with open(DATA_DIR / "federal_brackets_2024.json", "r") as f:
        return json.load(f)

def load_state_taxes():
    """Load state tax rates from JSON file."""
    with open(DATA_DIR / "state_taxes.json", "r") as f:
        return json.load(f)

# Load tax data at module initialization
FEDERAL_BRACKETS = load_federal_brackets()
STATE_TAXES = load_state_taxes()

# =============================================================================
# FICA TAX CONSTANTS (2024)
# =============================================================================

SOCIAL_SECURITY_RATE = 0.062           # 6.2% Social Security tax
SOCIAL_SECURITY_WAGE_BASE = 168600     # 2024 wage base limit
MEDICARE_RATE = 0.0145                 # 1.45% Medicare tax
MEDICARE_ADDITIONAL_RATE = 0.009       # Additional 0.9% Medicare tax over $200k


# =============================================================================
# FEDERAL TAX CALCULATION
# =============================================================================

def calculate_federal_tax(gross_income: float, filing_status: str) -> dict:
    """
    Calculate federal income tax based on gross income and filing status.

    Uses progressive tax brackets where each bracket is taxed at its own rate.
    Example: For $100k income, first $11k taxed at 10%, next portion at 12%, etc.

    Args:
        gross_income: Annual gross income before any deductions
        filing_status: One of 'single', 'married_filing_jointly',
                      'married_filing_separately', 'head_of_household'

    Returns:
        Dictionary with tax breakdown including effective rate
    """
    status_data = FEDERAL_BRACKETS.get(filing_status)
    if not status_data:
        raise ValueError(f"Invalid filing status: {filing_status}")

    standard_deduction = status_data["standard_deduction"]
    brackets = status_data["brackets"]

    # Calculate taxable income after standard deduction
    taxable_income = max(0, gross_income - standard_deduction)

    # Calculate tax using progressive brackets
    total_tax = 0.0
    remaining_income = taxable_income
    bracket_breakdown = []

    for bracket in brackets:
        bracket_min = bracket["min"]
        bracket_max = bracket["max"] if bracket["max"] else float("inf")
        rate = bracket["rate"]

        if remaining_income <= 0:
            break

        # Calculate income in this bracket
        bracket_income = min(remaining_income, bracket_max - bracket_min)
        bracket_tax = bracket_income * rate

        if bracket_income > 0:
            bracket_breakdown.append({
                "rate": rate,
                "income": bracket_income,
                "tax": bracket_tax
            })

        total_tax += bracket_tax
        remaining_income -= bracket_income

    effective_rate = (total_tax / gross_income * 100) if gross_income > 0 else 0

    return {
        "gross_income": gross_income,
        "standard_deduction": standard_deduction,
        "taxable_income": taxable_income,
        "federal_tax": total_tax,
        "effective_rate": effective_rate,
        "bracket_breakdown": bracket_breakdown
    }


def calculate_state_tax(gross_income: float, state_code: str) -> dict:
    """
    Calculate state income tax estimate.

    Args:
        gross_income: Annual gross income
        state_code: Two-letter state code (e.g., 'TX', 'CA')

    Returns:
        Dictionary with state tax info
    """
    state_data = STATE_TAXES.get(state_code.upper())
    if not state_data:
        raise ValueError(f"Invalid state code: {state_code}")

    rate = state_data["rate"]
    state_tax = gross_income * rate

    return {
        "state": state_data["name"],
        "state_code": state_code.upper(),
        "rate": rate,
        "rate_percent": rate * 100,
        "tax_type": state_data["type"],
        "state_tax": state_tax
    }


def calculate_fica(gross_income: float) -> dict:
    """
    Calculate FICA taxes (Social Security + Medicare).

    Args:
        gross_income: Annual gross income

    Returns:
        Dictionary with FICA breakdown
    """
    # Social Security (capped at wage base)
    ss_taxable = min(gross_income, SOCIAL_SECURITY_WAGE_BASE)
    social_security = ss_taxable * SOCIAL_SECURITY_RATE

    # Medicare (no cap, additional tax over $200k)
    medicare = gross_income * MEDICARE_RATE
    if gross_income > 200000:
        medicare += (gross_income - 200000) * MEDICARE_ADDITIONAL_RATE

    total_fica = social_security + medicare

    return {
        "social_security": social_security,
        "medicare": medicare,
        "total_fica": total_fica,
        "fica_rate": (total_fica / gross_income * 100) if gross_income > 0 else 0
    }


def calculate_take_home(gross_income: float, filing_status: str, state_code: str) -> dict:
    """
    Calculate estimated take-home pay after all taxes.

    Args:
        gross_income: Annual gross income
        filing_status: Filing status for federal taxes
        state_code: Two-letter state code

    Returns:
        Complete tax breakdown with take-home pay
    """
    federal = calculate_federal_tax(gross_income, filing_status)
    state = calculate_state_tax(gross_income, state_code)
    fica = calculate_fica(gross_income)

    total_taxes = federal["federal_tax"] + state["state_tax"] + fica["total_fica"]
    take_home = gross_income - total_taxes

    return {
        "gross_income": gross_income,
        "filing_status": filing_status,
        "state": state["state"],
        "state_code": state_code,

        # Federal breakdown
        "standard_deduction": federal["standard_deduction"],
        "taxable_income": federal["taxable_income"],
        "federal_tax": federal["federal_tax"],
        "federal_effective_rate": federal["effective_rate"],

        # State breakdown
        "state_tax": state["state_tax"],
        "state_rate": state["rate_percent"],

        # FICA breakdown
        "social_security": fica["social_security"],
        "medicare": fica["medicare"],
        "total_fica": fica["total_fica"],

        # Totals
        "total_taxes": total_taxes,
        "take_home_annual": take_home,
        "take_home_monthly": take_home / 12,
        "overall_tax_rate": (total_taxes / gross_income * 100) if gross_income > 0 else 0
    }


def get_all_states() -> list:
    """Return list of all states with their names."""
    return [(code, data["name"]) for code, data in sorted(STATE_TAXES.items(), key=lambda x: x[1]["name"])]


def get_filing_statuses() -> list:
    """Return list of available filing statuses."""
    return [
        ("single", "Single"),
        ("married_filing_jointly", "Married Filing Jointly"),
        ("married_filing_separately", "Married Filing Separately"),
        ("head_of_household", "Head of Household")
    ]
