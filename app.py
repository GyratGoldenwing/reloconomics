"""
Reloconomics - Predictive Cost of Living Comparison Tool
R&D Demonstrator Application

This Streamlit app demonstrates the core functionality:
- Tax calculation (federal + state + FICA)
- Take-home pay estimation by filing status
- Cost of living comparison across metropolitan areas
- ML-powered expense forecasting with seasonal patterns
- Interactive data visualization with Plotly

Author: Jeremiah Williams
Course: Project & Portfolio IV (CSBS-AI)
Date: January 2026
"""

# =============================================================================
# IMPORTS
# =============================================================================

# Streamlit - Python web framework for data apps
import streamlit as st

# Plotly - Interactive charting library
import plotly.express as px
import plotly.graph_objects as go

# Pandas - Data manipulation
import pandas as pd

# Local utility modules
from utils.tax_calculator import (
    calculate_take_home,      # Main tax calculation function
    get_all_states,           # List of US states
    get_filing_statuses       # Tax filing status options
)
from utils.cost_of_living import (
    get_metros,               # Available metro areas
    calculate_expenses,       # Monthly expense estimates
    compare_metros,           # Side-by-side comparison
    calculate_purchasing_power  # Discretionary income calc
)
from utils.forecaster import (
    forecast_expenses,        # ML-powered predictions
    get_seasonal_insights,    # Seasonal pattern analysis
    get_available_metros as get_forecast_metros  # Metros with forecast data
)
from utils.affordability_map import (
    create_affordability_map,  # Choropleth heat map
    get_affordability_summary  # State comparison summary
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Reloconomics",
    page_icon="📊",
    layout="wide"  # Use full screen width for side-by-side comparisons
)

# =============================================================================
# HEADER SECTION
# =============================================================================

st.title("📊 Reloconomics")
st.markdown("**Predictive Cost of Living Comparison Tool**")
st.markdown("_Compare your true purchasing power across cities based on estimated take-home pay_")

st.divider()

# =============================================================================
# SIDEBAR - USER INPUTS
# =============================================================================

st.sidebar.header("Your Information")

# Salary input
salary = st.sidebar.number_input(
    "Annual Gross Salary ($)",
    min_value=0,
    max_value=1000000,
    value=95000,
    step=1000,
    help="Enter your annual salary before taxes"
)

# Filing status
filing_statuses = get_filing_statuses()
filing_status = st.sidebar.selectbox(
    "Filing Status",
    options=[fs[0] for fs in filing_statuses],
    format_func=lambda x: dict(filing_statuses)[x],
    help="Select your tax filing status"
)

st.sidebar.divider()
st.sidebar.header("Compare Locations")

# Metro selection
metros = get_metros()

current_metro = st.sidebar.selectbox(
    "Current Location",
    options=metros,
    index=metros.index("Austin, TX") if "Austin, TX" in metros else 0
)

target_metro = st.sidebar.selectbox(
    "Target Location",
    options=metros,
    index=metros.index("San Francisco, CA") if "San Francisco, CA" in metros else 1
)

# Get state codes from metro data
from utils.cost_of_living import get_metro_data
current_state = get_metro_data(current_metro)["state"]
target_state = get_metro_data(target_metro)["state"]

# =============================================================================
# INPUT VALIDATION
# =============================================================================

# Validation: ensure different cities selected
cities_valid = current_metro != target_metro
salary_valid = salary >= 10000  # Minimum salary for meaningful comparison

if not cities_valid:
    st.sidebar.warning("⚠️ Please select different cities to compare")

if not salary_valid:
    st.sidebar.warning("⚠️ Enter a salary of at least $10,000")

inputs_valid = cities_valid and salary_valid

# Calculate button (disabled if validation fails)
calculate = st.sidebar.button(
    "Calculate Comparison",
    type="primary",
    use_container_width=True,
    disabled=not inputs_valid
)

# Disclaimer
st.sidebar.divider()
st.sidebar.caption(
    "⚠️ **Disclaimer**: These are estimates only, not tax advice. "
    "Actual take-home pay varies based on deductions, credits, and individual circumstances. "
    "Consult a tax professional for accurate calculations."
)

# =============================================================================
# MAIN CONTENT - TAX & COST CALCULATIONS
# =============================================================================

if (calculate or salary > 0) and inputs_valid:
    # Calculate take-home pay for both locations using tax calculator module
    current_calc = calculate_take_home(salary, filing_status, current_state)
    target_calc = calculate_take_home(salary, filing_status, target_state)

    # Calculate purchasing power
    current_power = calculate_purchasing_power(current_calc["take_home_monthly"], current_metro)
    target_power = calculate_purchasing_power(target_calc["take_home_monthly"], target_metro)

    # Display results in columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"📍 {current_metro}")
        st.metric(
            "Estimated Take-Home Pay",
            f"${current_calc['take_home_annual']:,.0f}/yr",
            f"${current_calc['take_home_monthly']:,.0f}/mo"
        )

        # Tax breakdown
        with st.expander("Tax Breakdown"):
            st.write(f"**Gross Income:** ${salary:,.0f}")
            st.write(f"**Standard Deduction:** ${current_calc['standard_deduction']:,.0f}")
            st.write(f"**Federal Tax:** ${current_calc['federal_tax']:,.0f} ({current_calc['federal_effective_rate']:.1f}%)")
            st.write(f"**State Tax ({current_state}):** ${current_calc['state_tax']:,.0f} ({current_calc['state_rate']:.1f}%)")
            st.write(f"**FICA:** ${current_calc['total_fica']:,.0f}")
            st.divider()
            st.write(f"**Total Taxes:** ${current_calc['total_taxes']:,.0f}")
            st.write(f"**Overall Tax Rate:** {current_calc['overall_tax_rate']:.1f}%")

        # Purchasing power
        st.metric(
            "Monthly Discretionary Income",
            f"${current_power['discretionary_income']:,.0f}",
            f"{100 - current_power['expense_ratio']:.0f}% of take-home"
        )

    with col2:
        st.subheader(f"📍 {target_metro}")

        # Calculate difference - negative means LESS money (bad)
        take_home_diff = target_calc['take_home_annual'] - current_calc['take_home_annual']

        st.metric(
            "Estimated Take-Home Pay",
            f"${target_calc['take_home_annual']:,.0f}/yr",
            f"${take_home_diff:+,.0f} vs current",
            delta_color="normal"
        )
        # Explicit color indicator for clarity
        if take_home_diff < 0:
            st.caption(f"🔴 You keep **${abs(take_home_diff):,.0f} less** per year here")
        elif take_home_diff > 0:
            st.caption(f"🟢 You keep **${take_home_diff:,.0f} more** per year here")

        # Tax breakdown
        with st.expander("Tax Breakdown"):
            st.write(f"**Gross Income:** ${salary:,.0f}")
            st.write(f"**Standard Deduction:** ${target_calc['standard_deduction']:,.0f}")
            st.write(f"**Federal Tax:** ${target_calc['federal_tax']:,.0f} ({target_calc['federal_effective_rate']:.1f}%)")
            st.write(f"**State Tax ({target_state}):** ${target_calc['state_tax']:,.0f} ({target_calc['state_rate']:.1f}%)")
            st.write(f"**FICA:** ${target_calc['total_fica']:,.0f}")
            st.divider()
            st.write(f"**Total Taxes:** ${target_calc['total_taxes']:,.0f}")
            st.write(f"**Overall Tax Rate:** {target_calc['overall_tax_rate']:.1f}%")

        # Purchasing power - negative means LESS money to spend (bad)
        discretionary_diff = target_power['discretionary_income'] - current_power['discretionary_income']
        st.metric(
            "Monthly Discretionary Income",
            f"${target_power['discretionary_income']:,.0f}",
            f"${discretionary_diff:+,.0f} vs current",
            delta_color="normal"
        )
        # Explicit color indicator for clarity
        if discretionary_diff < 0:
            st.caption(f"🔴 **${abs(discretionary_diff):,.0f} less** per month to spend")
        elif discretionary_diff > 0:
            st.caption(f"🟢 **${discretionary_diff:,.0f} more** per month to spend")

    st.divider()

    # Cost comparison table
    st.subheader("📊 Monthly Expense Comparison")

    comparison = compare_metros(current_metro, target_metro)

    expense_data = {
        "Category": ["Housing", "Food", "Transportation", "Healthcare", "Utilities", "**Total**"],
        current_metro: [
            f"${comparison['metro1']['expenses']['housing']:,.0f}",
            f"${comparison['metro1']['expenses']['food']:,.0f}",
            f"${comparison['metro1']['expenses']['transportation']:,.0f}",
            f"${comparison['metro1']['expenses']['healthcare']:,.0f}",
            f"${comparison['metro1']['expenses']['utilities']:,.0f}",
            f"**${comparison['metro1']['expenses']['total']:,.0f}**"
        ],
        target_metro: [
            f"${comparison['metro2']['expenses']['housing']:,.0f}",
            f"${comparison['metro2']['expenses']['food']:,.0f}",
            f"${comparison['metro2']['expenses']['transportation']:,.0f}",
            f"${comparison['metro2']['expenses']['healthcare']:,.0f}",
            f"${comparison['metro2']['expenses']['utilities']:,.0f}",
            f"**${comparison['metro2']['expenses']['total']:,.0f}**"
        ],
        "Difference": [
            f"${comparison['differences']['housing']['amount']:+,.0f} ({comparison['differences']['housing']['percent']:+.0f}%)",
            f"${comparison['differences']['food']['amount']:+,.0f} ({comparison['differences']['food']['percent']:+.0f}%)",
            f"${comparison['differences']['transportation']['amount']:+,.0f} ({comparison['differences']['transportation']['percent']:+.0f}%)",
            f"${comparison['differences']['healthcare']['amount']:+,.0f} ({comparison['differences']['healthcare']['percent']:+.0f}%)",
            f"${comparison['differences']['utilities']['amount']:+,.0f} ({comparison['differences']['utilities']['percent']:+.0f}%)",
            f"**${comparison['differences']['total']['amount']:+,.0f} ({comparison['differences']['total']['percent']:+.0f}%)**"
        ]
    }

    df = pd.DataFrame(expense_data)
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.divider()

    # =========================================================================
    # PLOTLY VISUALIZATIONS
    # =========================================================================

    st.subheader("📈 Visual Comparison")

    viz_col1, viz_col2 = st.columns(2)

    with viz_col1:
        # Expense breakdown bar chart
        categories = ["Housing", "Food", "Transportation", "Healthcare", "Utilities"]
        current_values = [
            comparison['metro1']['expenses']['housing'],
            comparison['metro1']['expenses']['food'],
            comparison['metro1']['expenses']['transportation'],
            comparison['metro1']['expenses']['healthcare'],
            comparison['metro1']['expenses']['utilities']
        ]
        target_values = [
            comparison['metro2']['expenses']['housing'],
            comparison['metro2']['expenses']['food'],
            comparison['metro2']['expenses']['transportation'],
            comparison['metro2']['expenses']['healthcare'],
            comparison['metro2']['expenses']['utilities']
        ]

        fig = go.Figure(data=[
            go.Bar(name=current_metro, x=categories, y=current_values, marker_color='#1f77b4'),
            go.Bar(name=target_metro, x=categories, y=target_values, marker_color='#ff7f0e')
        ])
        fig.update_layout(
            title="Monthly Expenses by Category",
            barmode='group',
            yaxis_title="Monthly Cost ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

    with viz_col2:
        # Take-home vs expenses pie charts
        fig = go.Figure()

        # Current location
        fig.add_trace(go.Pie(
            labels=['Expenses', 'Discretionary'],
            values=[current_power['total_expenses'], current_power['discretionary_income']],
            name=current_metro,
            domain={'x': [0, 0.45]},
            marker_colors=['#ff7f0e', '#2ca02c']
        ))

        # Target location
        fig.add_trace(go.Pie(
            labels=['Expenses', 'Discretionary'],
            values=[target_power['total_expenses'], target_power['discretionary_income']],
            name=target_metro,
            domain={'x': [0.55, 1]},
            marker_colors=['#ff7f0e', '#2ca02c']
        ))

        fig.update_layout(
            title=f"Monthly Budget Allocation",
            annotations=[
                dict(text=current_metro.split(',')[0], x=0.18, y=0.5, font_size=12, showarrow=False),
                dict(text=target_metro.split(',')[0], x=0.82, y=0.5, font_size=12, showarrow=False)
            ]
        )
        st.plotly_chart(fig, use_container_width=True)

    # Bottom line summary
    st.divider()
    st.subheader("💡 Bottom Line")

    if discretionary_diff > 0:
        st.success(
            f"**{target_metro}** leaves you with **${discretionary_diff:,.0f} more** per month "
            f"in discretionary income, despite "
            f"{'lower' if take_home_diff < 0 else 'the same'} take-home pay due to "
            f"{'higher' if target_calc['state_tax'] > current_calc['state_tax'] else 'lower'} state taxes."
        )
    elif discretionary_diff < 0:
        st.warning(
            f"**{current_metro}** leaves you with **${abs(discretionary_diff):,.0f} more** per month "
            f"in discretionary income. The higher cost of living in {target_metro} "
            f"outweighs any tax differences."
        )
    else:
        st.info("Both locations provide similar purchasing power with your current salary.")

    # =========================================================================
    # AFFORDABILITY HEAT MAP
    # =========================================================================

    st.divider()
    st.subheader("🗺️ Affordability Map")
    st.markdown("_See how cost of living compares across all US states relative to your current location_")

    # Create the choropleth map
    affordability_fig = create_affordability_map(
        base_state=current_state,
        target_state=target_state,
        title="US Cost of Living"
    )
    st.plotly_chart(affordability_fig, use_container_width=True)

    # Legend explanation
    map_col1, map_col2, map_col3 = st.columns(3)
    with map_col1:
        st.markdown("🟢 **Green** = Cheaper than your location")
    with map_col2:
        st.markdown("⬜ **White** = Similar to your location")
    with map_col3:
        st.markdown("🔴 **Red** = More expensive than your location")

    # Show summary for target state
    summary = get_affordability_summary(current_state, target_state)
    if "error" not in summary:
        if summary["is_cheaper"]:
            st.caption(
                f"📍 **{summary['target_name']}** is **{abs(summary['overall_diff_percent']):.1f}% cheaper** "
                f"overall than {summary['base_name']} (housing: {summary['housing_diff_percent']:+.1f}%)"
            )
        else:
            st.caption(
                f"📍 **{summary['target_name']}** is **{summary['overall_diff_percent']:.1f}% more expensive** "
                f"overall than {summary['base_name']} (housing: {summary['housing_diff_percent']:+.1f}%)"
            )

# =========================================================================
    # ML FORECASTING SECTION (scikit-learn Integration)
    # =========================================================================

    st.divider()
    st.subheader("🔮 Expense Forecast (ML-Powered)")
    st.markdown("_Predicted monthly costs using scikit-learn with seasonal patterns_")

    # Check which metros have forecast data
    forecast_metros = get_forecast_metros()

    # Generate forecasts for metros that have data
    forecast_col1, forecast_col2 = st.columns(2)

    with forecast_col1:
        if current_metro in forecast_metros:
            current_forecast = forecast_expenses(current_metro, months_ahead=6)

            if "error" not in current_forecast:
                # Create forecast chart - actual dollars
                fig_forecast = go.Figure()

                # Historical total expenses
                fig_forecast.add_trace(go.Scatter(
                    x=current_forecast["historical_dates"],
                    y=current_forecast["historical_totals"],
                    mode='lines',
                    name='Historical',
                    line=dict(color='#1f77b4', width=2)
                ))

                # Forecast total expenses
                fig_forecast.add_trace(go.Scatter(
                    x=current_forecast["forecast_dates"],
                    y=current_forecast["forecast_totals"],
                    mode='lines+markers',
                    name='Forecast',
                    line=dict(color='#ff7f0e', width=2, dash='dash')
                ))

                fig_forecast.update_layout(
                    title=f"{current_metro} - Monthly Expenses",
                    xaxis_title="",
                    yaxis_title="Monthly Cost ($)",
                    yaxis_tickprefix="$",
                    hovermode='x unified'
                )
                st.plotly_chart(fig_forecast, use_container_width=True)

                # Show forecast summary
                last_actual = current_forecast["historical_totals"][-1]
                last_forecast = current_forecast["forecast_totals"][-1]
                change = last_forecast - last_actual
                st.metric(
                    f"Projected Monthly Expenses ({current_forecast['forecast_dates'][-1]})",
                    f"${last_forecast:,.0f}",
                    f"${change:+,.0f} vs today"
                )
        else:
            st.info(f"Forecast data not available for {current_metro}")

    with forecast_col2:
        if target_metro in forecast_metros:
            target_forecast = forecast_expenses(target_metro, months_ahead=6)

            if "error" not in target_forecast:
                # Create forecast chart
                fig_forecast2 = go.Figure()

                fig_forecast2.add_trace(go.Scatter(
                    x=target_forecast["historical_dates"],
                    y=target_forecast["historical_totals"],
                    mode='lines',
                    name='Historical',
                    line=dict(color='#1f77b4', width=2)
                ))

                fig_forecast2.add_trace(go.Scatter(
                    x=target_forecast["forecast_dates"],
                    y=target_forecast["forecast_totals"],
                    mode='lines+markers',
                    name='Forecast',
                    line=dict(color='#ff7f0e', width=2, dash='dash')
                ))

                fig_forecast2.update_layout(
                    title=f"{target_metro} - Monthly Expenses",
                    xaxis_title="",
                    yaxis_title="Monthly Cost ($)",
                    yaxis_tickprefix="$",
                    hovermode='x unified'
                )
                st.plotly_chart(fig_forecast2, use_container_width=True)

                # Show forecast summary
                last_actual2 = target_forecast["historical_totals"][-1]
                last_forecast2 = target_forecast["forecast_totals"][-1]
                change2 = last_forecast2 - last_actual2
                st.metric(
                    f"Projected Monthly Expenses ({target_forecast['forecast_dates'][-1]})",
                    f"${last_forecast2:,.0f}",
                    f"${change2:+,.0f} vs today"
                )
        else:
            st.info(f"Forecast data not available for {target_metro}")

    # Seasonal Insights
    st.markdown("### 📅 Seasonal Patterns")
    seasonal_col1, seasonal_col2 = st.columns(2)

    with seasonal_col1:
        if current_metro in forecast_metros:
            insights = get_seasonal_insights(current_metro)
            if "error" not in insights:
                st.markdown(f"**{current_metro}**")
                for cat, data in insights["insights"].items():
                    if data["seasonal_variance"] > 3:  # Only show meaningful variance
                        st.caption(
                            f"• **{cat.title()}**: Peaks in {data['peak_month']} "
                            f"(${data['peak_value']:,.0f}), lowest in {data['low_month']} "
                            f"(${data['low_value']:,.0f}) — {data['seasonal_variance']:.0f}% swing"
                        )

    with seasonal_col2:
        if target_metro in forecast_metros:
            insights2 = get_seasonal_insights(target_metro)
            if "error" not in insights2:
                st.markdown(f"**{target_metro}**")
                for cat, data in insights2["insights"].items():
                    if data["seasonal_variance"] > 3:
                        st.caption(
                            f"• **{cat.title()}**: Peaks in {data['peak_month']} "
                            f"(${data['peak_value']:,.0f}), lowest in {data['low_month']} "
                            f"(${data['low_value']:,.0f}) — {data['seasonal_variance']:.0f}% swing"
                        )

    # ML explanation
    with st.expander("How the ML Forecast Works"):
        st.markdown("""
        **Feature Engineering:**
        - **Lag features**: Previous 3 months of expenses (captures momentum)
        - **Seasonality**: Month of year (captures seasonal patterns like summer AC costs)
        - **Trend**: Time index (captures long-term price increases)

        **Model:** Linear Regression (scikit-learn) trained separately for each expense category

        **What This Shows:**
        - Historical monthly expenses in actual dollars
        - 6-month forecast based on seasonal patterns and trends
        - Seasonal peaks and valleys for planning your budget

        **Data Source:** BLS Consumer Expenditure Survey (sample data for R&D demonstration)
        """)

# Data sources footer
st.divider()
st.caption(
    "**Data Sources:** Federal tax brackets from IRS (2024). "
    "State tax rates from Tax Foundation. "
    "Cost of living indices based on BEA Regional Price Parities and BLS data. "
    "ML forecasts use scikit-learn on historical CPI data. "
    "All sources are free, public government data."
)
