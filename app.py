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
    get_available_metros as get_forecast_metros,  # Metros with forecast data
    compare_forecasts,        # Multi-horizon forecast comparison
    get_best_worst_months     # Cheapest/most expensive months
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
    width="stretch",
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
        st.caption("📍 Your current location")

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
        st.caption("💰 Baseline for comparison")

    with col2:
        st.subheader(f"📍 {target_metro}")

        # Calculate difference - negative means LESS money (bad)
        take_home_diff = target_calc['take_home_annual'] - current_calc['take_home_annual']

        st.metric(
            "Estimated Take-Home Pay",
            f"${target_calc['take_home_annual']:,.0f}/yr",
            f"{'+$' if take_home_diff >= 0 else '-$'}{abs(take_home_diff):,.0f} vs current",
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
        # Format main value to handle negative discretionary income
        disc_value = target_power['discretionary_income']
        disc_display = f"${disc_value:,.0f}" if disc_value >= 0 else f"-${abs(disc_value):,.0f}"
        st.metric(
            "Monthly Discretionary Income",
            disc_display,
            f"{'+$' if discretionary_diff >= 0 else '-$'}{abs(discretionary_diff):,.0f} vs current",
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
        "Category": ["Housing", "Food", "Transportation", "Healthcare", "Utilities", "TOTAL"],
        current_metro: [
            f"${comparison['metro1']['expenses']['housing']:,.0f}",
            f"${comparison['metro1']['expenses']['food']:,.0f}",
            f"${comparison['metro1']['expenses']['transportation']:,.0f}",
            f"${comparison['metro1']['expenses']['healthcare']:,.0f}",
            f"${comparison['metro1']['expenses']['utilities']:,.0f}",
            f"${comparison['metro1']['expenses']['total']:,.0f}"
        ],
        target_metro: [
            f"${comparison['metro2']['expenses']['housing']:,.0f}",
            f"${comparison['metro2']['expenses']['food']:,.0f}",
            f"${comparison['metro2']['expenses']['transportation']:,.0f}",
            f"${comparison['metro2']['expenses']['healthcare']:,.0f}",
            f"${comparison['metro2']['expenses']['utilities']:,.0f}",
            f"${comparison['metro2']['expenses']['total']:,.0f}"
        ],
        "Difference": [
            ("🔴 " if comparison['differences']['housing']['amount'] > 0 else "🟢 " if comparison['differences']['housing']['amount'] < 0 else "") + f"${comparison['differences']['housing']['amount']:+,.0f} ({comparison['differences']['housing']['percent']:+.0f}%)",
            ("🔴 " if comparison['differences']['food']['amount'] > 0 else "🟢 " if comparison['differences']['food']['amount'] < 0 else "") + f"${comparison['differences']['food']['amount']:+,.0f} ({comparison['differences']['food']['percent']:+.0f}%)",
            ("🔴 " if comparison['differences']['transportation']['amount'] > 0 else "🟢 " if comparison['differences']['transportation']['amount'] < 0 else "") + f"${comparison['differences']['transportation']['amount']:+,.0f} ({comparison['differences']['transportation']['percent']:+.0f}%)",
            ("🔴 " if comparison['differences']['healthcare']['amount'] > 0 else "🟢 " if comparison['differences']['healthcare']['amount'] < 0 else "") + f"${comparison['differences']['healthcare']['amount']:+,.0f} ({comparison['differences']['healthcare']['percent']:+.0f}%)",
            ("🔴 " if comparison['differences']['utilities']['amount'] > 0 else "🟢 " if comparison['differences']['utilities']['amount'] < 0 else "") + f"${comparison['differences']['utilities']['amount']:+,.0f} ({comparison['differences']['utilities']['percent']:+.0f}%)",
            ("🔴 " if comparison['differences']['total']['amount'] > 0 else "🟢 " if comparison['differences']['total']['amount'] < 0 else "") + f"${comparison['differences']['total']['amount']:+,.0f} ({comparison['differences']['total']['percent']:+.0f}%)"
        ]
    }

    df = pd.DataFrame(expense_data)
    st.dataframe(df, hide_index=True, width="stretch")

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
        st.plotly_chart(fig, width="stretch")

    with viz_col2:
        # Take-home vs expenses pie charts
        # Handle edge case: zero or negative discretionary income
        current_disc = max(0, current_power['discretionary_income'])
        target_disc = max(0, target_power['discretionary_income'])

        # Check if either location has no discretionary income
        current_warning = current_power['discretionary_income'] <= 0
        target_warning = target_power['discretionary_income'] <= 0

        fig = go.Figure()

        # Current location
        if current_warning:
            # Show expenses only with deficit indicator
            fig.add_trace(go.Pie(
                labels=['Expenses', 'Deficit'],
                values=[current_power['total_expenses'], abs(current_power['discretionary_income']) if current_power['discretionary_income'] < 0 else 1],
                name=current_metro,
                domain={'x': [0, 0.45]},
                marker_colors=['#d73027', '#7f0000'],  # Red shades for warning
                textinfo='label+percent'
            ))
        else:
            fig.add_trace(go.Pie(
                labels=['Expenses', 'Discretionary'],
                values=[current_power['total_expenses'], current_disc],
                name=current_metro,
                domain={'x': [0, 0.45]},
                marker_colors=['#ff7f0e', '#2ca02c'],
                textinfo='label+percent'
            ))

        # Target location
        if target_warning:
            # Show expenses only with deficit indicator
            fig.add_trace(go.Pie(
                labels=['Expenses', 'Deficit'],
                values=[target_power['total_expenses'], abs(target_power['discretionary_income']) if target_power['discretionary_income'] < 0 else 1],
                name=target_metro,
                domain={'x': [0.55, 1]},
                marker_colors=['#d73027', '#7f0000'],  # Red shades for warning
                textinfo='label+percent'
            ))
        else:
            fig.add_trace(go.Pie(
                labels=['Expenses', 'Discretionary'],
                values=[target_power['total_expenses'], target_disc],
                name=target_metro,
                domain={'x': [0.55, 1]},
                marker_colors=['#ff7f0e', '#2ca02c'],
                textinfo='label+percent'
            ))

        fig.update_layout(
            title=f"Monthly Budget Allocation",
            annotations=[
                dict(text=current_metro.split(',')[0], x=0.18, y=0.5, font_size=12, showarrow=False),
                dict(text=target_metro.split(',')[0], x=0.82, y=0.5, font_size=12, showarrow=False)
            ]
        )
        st.plotly_chart(fig, width="stretch")

        # Show warning if either location has no discretionary income
        if current_warning or target_warning:
            warning_cities = []
            if current_warning:
                warning_cities.append(current_metro.split(',')[0])
            if target_warning:
                warning_cities.append(target_metro.split(',')[0])
            st.warning(f"⚠️ **Budget Alert:** {', '.join(warning_cities)} expenses exceed take-home pay at this salary level.")

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
    # Disable scroll zoom to prevent accidental map movement
    st.plotly_chart(
        affordability_fig,
        width="stretch",
        config={'scrollZoom': False, 'displayModeBar': True, 'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d']}
    )

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
            current_forecast = forecast_expenses(current_metro, months_ahead=12)

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
                st.plotly_chart(fig_forecast, width="stretch")

                # Show forecast summary
                last_actual = current_forecast["historical_totals"][-1]
                last_forecast = current_forecast["forecast_totals"][-1]
                change = last_forecast - last_actual
                st.metric(
                    f"Projected Monthly Expenses ({current_forecast['forecast_dates'][-1]})",
                    f"${last_forecast:,.0f}",
                    f"{'+$' if change >= 0 else '-$'}{abs(change):,.0f} vs today",
                    delta_color="inverse"  # Higher expenses = bad (red)
                )
        else:
            st.info(f"Forecast data not available for {current_metro}")

    with forecast_col2:
        if target_metro in forecast_metros:
            target_forecast = forecast_expenses(target_metro, months_ahead=12)

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
                st.plotly_chart(fig_forecast2, width="stretch")

                # Show forecast summary
                last_actual2 = target_forecast["historical_totals"][-1]
                last_forecast2 = target_forecast["forecast_totals"][-1]
                change2 = last_forecast2 - last_actual2
                st.metric(
                    f"Projected Monthly Expenses ({target_forecast['forecast_dates'][-1]})",
                    f"${last_forecast2:,.0f}",
                    f"{'+$' if change2 >= 0 else '-$'}{abs(change2):,.0f} vs today",
                    delta_color="inverse"  # Higher expenses = bad (red)
                )
        else:
            st.info(f"Forecast data not available for {target_metro}")

    # =========================================================================
    # MULTI-HORIZON FORECAST COMPARISON TABLE
    # =========================================================================

    if current_metro in forecast_metros and target_metro in forecast_metros:
        st.markdown("### 📊 Forecast Comparison: 3, 6, 9, 12 Months")
        st.markdown("_Predicted monthly expenses by category at each time horizon_")

        forecast_comparison = compare_forecasts(current_metro, target_metro, horizons=[3, 6, 9, 12])

        if "error" not in forecast_comparison:
            # Build comparison table data
            categories = ["housing", "food", "transportation", "utilities", "healthcare"]
            horizons = [3, 6, 9, 12]

            # Create tabs for each time horizon
            tab_now, tab_3m, tab_6m, tab_9m, tab_12m = st.tabs(["Now", "3 Months", "6 Months", "9 Months", "12 Months"])

            def build_comparison_table(data_key, date_label=""):
                """Helper to build a comparison table for a given horizon."""
                table_data = {
                    "Category": [],
                    f"{current_metro.split(',')[0]}": [],
                    f"{target_metro.split(',')[0]}": [],
                    "Difference": []
                }

                for cat in categories:
                    cat_data = forecast_comparison["categories"][cat]
                    if data_key == "current":
                        vals = cat_data["current"]
                    else:
                        vals = cat_data["forecasts"][data_key]

                    diff_display = f"${vals['diff']:+,.0f}"
                    if data_key != "current" and vals.get('diff_pct'):
                        diff_display += f" ({vals['diff_pct']:+.1f}%)"

                    # Color indicator
                    if vals['diff'] > 0:
                        diff_display = f"🔴 {diff_display}"
                    elif vals['diff'] < 0:
                        diff_display = f"🟢 {diff_display}"

                    table_data["Category"].append(cat.title())
                    table_data[f"{current_metro.split(',')[0]}"].append(f"${vals['metro1']:,.0f}")
                    table_data[f"{target_metro.split(',')[0]}"].append(f"${vals['metro2']:,.0f}")
                    table_data["Difference"].append(diff_display)

                # Add totals row
                if data_key == "current":
                    totals = forecast_comparison["totals"]["current"]
                else:
                    totals = forecast_comparison["totals"][data_key]

                total_diff = f"${totals['diff']:+,.0f}"
                if data_key != "current" and totals.get('diff_pct'):
                    total_diff += f" ({totals['diff_pct']:+.1f}%)"
                if totals['diff'] > 0:
                    total_diff = f"🔴 {total_diff}"
                elif totals['diff'] < 0:
                    total_diff = f"🟢 {total_diff}"

                table_data["Category"].append("TOTAL")
                table_data[f"{current_metro.split(',')[0]}"].append(f"${totals['metro1']:,.0f}")
                table_data[f"{target_metro.split(',')[0]}"].append(f"${totals['metro2']:,.0f}")
                table_data["Difference"].append(total_diff)

                return pd.DataFrame(table_data)

            with tab_now:
                st.dataframe(build_comparison_table("current"), hide_index=True, width="stretch")

            with tab_3m:
                st.caption(f"Forecast for {forecast_comparison['forecast_dates'][3]}")
                st.dataframe(build_comparison_table(3), hide_index=True, width="stretch")

            with tab_6m:
                st.caption(f"Forecast for {forecast_comparison['forecast_dates'][6]}")
                st.dataframe(build_comparison_table(6), hide_index=True, width="stretch")

            with tab_9m:
                st.caption(f"Forecast for {forecast_comparison['forecast_dates'][9]}")
                st.dataframe(build_comparison_table(9), hide_index=True, width="stretch")

            with tab_12m:
                st.caption(f"Forecast for {forecast_comparison['forecast_dates'][12]}")
                st.dataframe(build_comparison_table(12), hide_index=True, width="stretch")

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

    # Best & Worst Months Comparison
    st.markdown("### 💰 Best & Worst Months to Budget")
    st.markdown("_Cheapest and most expensive months based on historical data_")

    bw_col1, bw_col2 = st.columns(2)

    with bw_col1:
        if current_metro in forecast_metros:
            bw_current = get_best_worst_months(current_metro)
            if "error" not in bw_current:
                st.markdown(f"**{current_metro}**")

                # Cheapest months
                st.markdown("🟢 **Cheapest 3 Months:**")
                for month, cost in bw_current["cheapest_months"]:
                    st.caption(f"  • {month}: ${cost:,.0f}/mo")

                # Most expensive months
                st.markdown("🔴 **Most Expensive 3 Months:**")
                for month, cost in bw_current["most_expensive_months"]:
                    st.caption(f"  • {month}: ${cost:,.0f}/mo")

    with bw_col2:
        if target_metro in forecast_metros:
            bw_target = get_best_worst_months(target_metro)
            if "error" not in bw_target:
                st.markdown(f"**{target_metro}**")

                # Cheapest months
                st.markdown("🟢 **Cheapest 3 Months:**")
                for month, cost in bw_target["cheapest_months"]:
                    st.caption(f"  • {month}: ${cost:,.0f}/mo")

                # Most expensive months
                st.markdown("🔴 **Most Expensive 3 Months:**")
                for month, cost in bw_target["most_expensive_months"]:
                    st.caption(f"  • {month}: ${cost:,.0f}/mo")

    # Show comparison insight
    if current_metro in forecast_metros and target_metro in forecast_metros:
        if "error" not in bw_current and "error" not in bw_target:
            best_current = bw_current["annual_low"]
            best_target = bw_target["annual_low"]
            worst_current = bw_current["annual_high"]
            worst_target = bw_target["annual_high"]

            # Compare the best months
            if best_target[1] < best_current[1]:
                savings = best_current[1] - best_target[1]
                st.success(
                    f"💡 Tip: {target_metro.split(',')[0]}'s cheapest month "
                    f"({best_target[0]}: ${best_target[1]:,.0f}) is ${savings:,.0f} less than "
                    f"{current_metro.split(',')[0]}'s cheapest ({best_current[0]}: ${best_current[1]:,.0f})"
                )
            else:
                extra = best_target[1] - best_current[1]
                st.warning(
                    f"💡 Note: Even {target_metro.split(',')[0]}'s cheapest month "
                    f"({best_target[0]}: ${best_target[1]:,.0f}) costs ${extra:,.0f} more than "
                    f"{current_metro.split(',')[0]}'s cheapest ({best_current[0]}: ${best_current[1]:,.0f})"
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
        - 12-month forecast based on seasonal patterns and trends
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
