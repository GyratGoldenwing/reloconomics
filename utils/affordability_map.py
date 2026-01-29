"""
Affordability Map Module for Reloconomics

Creates a choropleth heat map showing relative cost of living
across US states, colored relative to user's current location.

Red = More expensive than current location
Green = Less expensive than current location

Data Source: BEA Regional Price Parities

Author: Jeremiah Williams
Course: Project & Portfolio IV (CSBS-AI)
"""

import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# =============================================================================
# DATA LOADING
# =============================================================================

DATA_DIR = Path(__file__).parent.parent / "data"


def load_state_rpp() -> dict:
    """Load state-level Regional Price Parity data."""
    try:
        with open(DATA_DIR / "state_rpp.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"states": {}, "error": "State RPP data not found"}


def get_all_states() -> list:
    """Get list of all state codes."""
    data = load_state_rpp()
    return sorted(data.get("states", {}).keys())


def get_state_name(state_code: str) -> str:
    """Get full state name from code."""
    data = load_state_rpp()
    state = data.get("states", {}).get(state_code, {})
    return state.get("name", state_code)


# =============================================================================
# AFFORDABILITY CALCULATIONS
# =============================================================================

def calculate_relative_affordability(base_state: str) -> pd.DataFrame:
    """
    Calculate affordability of all states relative to a base state.

    Args:
        base_state: Two-letter state code for current location

    Returns:
        DataFrame with state codes, names, and relative affordability
    """
    data = load_state_rpp()
    states = data.get("states", {})

    if base_state not in states:
        return pd.DataFrame()

    base_rpp = states[base_state]["rpp"]

    rows = []
    for code, info in states.items():
        # Calculate relative difference (negative = cheaper, positive = more expensive)
        relative_diff = ((info["rpp"] - base_rpp) / base_rpp) * 100

        rows.append({
            "state_code": code,
            "state_name": info["name"],
            "rpp": info["rpp"],
            "housing_rpp": info.get("housing", info["rpp"]),
            "relative_diff": round(relative_diff, 1),
            "is_base": code == base_state
        })

    return pd.DataFrame(rows)


# =============================================================================
# HEAT MAP GENERATION
# =============================================================================

def create_affordability_map(
    base_state: str,
    target_state: str = None,
    title: str = "Cost of Living Relative to Your Location"
) -> go.Figure:
    """
    Create a choropleth map showing relative affordability.

    Colors:
    - Green shades: Less expensive than current location (good)
    - Red shades: More expensive than current location (bad)
    - White/neutral: Similar to current location

    Args:
        base_state: Current location state code
        target_state: Optional target state to highlight with marker
        title: Map title

    Returns:
        Plotly figure object
    """
    df = calculate_relative_affordability(base_state)

    if df.empty:
        # Return empty figure with error message
        fig = go.Figure()
        fig.add_annotation(
            text="Could not load state data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

    base_name = get_state_name(base_state)

    # Create choropleth map
    fig = px.choropleth(
        df,
        locations="state_code",
        locationmode="USA-states",
        color="relative_diff",
        color_continuous_scale=[
            [0.0, "#1a9850"],    # Dark green (most affordable)
            [0.3, "#91cf60"],    # Light green
            [0.45, "#d9ef8b"],   # Yellow-green
            [0.5, "#ffffbf"],    # White/neutral (same as base)
            [0.55, "#fee08b"],   # Yellow-orange
            [0.7, "#fc8d59"],    # Orange
            [1.0, "#d73027"]     # Dark red (most expensive)
        ],
        range_color=[-25, 25],  # Center scale at 0
        scope="usa",
        labels={"relative_diff": "% vs Your Location"},
        hover_name="state_name",
        hover_data={
            "state_code": False,
            "state_name": False,
            "rpp": ":.1f",
            "relative_diff": ":.1f%"
        }
    )

    # Update layout
    fig.update_layout(
        title={
            "text": f"{title}<br><sup>Relative to {base_name}</sup>",
            "x": 0.5,
            "xanchor": "center"
        },
        geo=dict(
            showlakes=True,
            lakecolor="rgb(255, 255, 255)",
            bgcolor="rgba(0,0,0,0)"
        ),
        coloraxis_colorbar=dict(
            title=dict(
                text="Cost Difference",
                side="right"
            ),
            ticksuffix="%",
            tickvals=[-20, -10, 0, 10, 20],
            ticktext=["20% Less", "10% Less", "Same", "10% More", "20% More"],
            len=0.6,
            thickness=15,
            x=1.02,
            y=0.5,
            yanchor="middle"
        ),
        margin={"r": 80, "t": 60, "l": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    # Disable scroll zoom on the map
    fig.update_geos(
        fitbounds="locations",
        visible=True
    )

    # State centroids (approximate) - used for markers and arc
    state_coords = {
        "AL": (32.7, -86.8), "AK": (64.0, -153.0), "AZ": (34.3, -111.7),
        "AR": (34.9, -92.4), "CA": (37.2, -119.4), "CO": (39.0, -105.5),
        "CT": (41.6, -72.7), "DE": (39.0, -75.5), "FL": (28.6, -82.4),
        "GA": (32.6, -83.4), "HI": (20.8, -156.3), "ID": (44.4, -114.6),
        "IL": (40.0, -89.2), "IN": (39.9, -86.3), "IA": (42.0, -93.5),
        "KS": (38.5, -98.4), "KY": (37.8, -85.7), "LA": (31.0, -92.0),
        "ME": (45.3, -69.0), "MD": (39.0, -76.7), "MA": (42.2, -71.5),
        "MI": (44.3, -85.4), "MN": (46.3, -94.3), "MS": (32.7, -89.7),
        "MO": (38.4, -92.5), "MT": (47.0, -109.6), "NE": (41.5, -99.8),
        "NV": (39.5, -116.9), "NH": (43.7, -71.6), "NJ": (40.2, -74.7),
        "NM": (34.5, -106.0), "NY": (42.9, -75.5), "NC": (35.5, -79.8),
        "ND": (47.4, -100.5), "OH": (40.4, -82.8), "OK": (35.6, -97.5),
        "OR": (43.9, -120.6), "PA": (40.9, -77.8), "RI": (41.7, -71.5),
        "SC": (33.9, -80.9), "SD": (44.4, -100.2), "TN": (35.9, -86.4),
        "TX": (31.5, -99.4), "UT": (39.3, -111.7), "VT": (44.0, -72.7),
        "VA": (37.5, -78.8), "WA": (47.4, -120.5), "WV": (38.9, -80.5),
        "WI": (44.6, -89.7), "WY": (43.0, -107.5), "DC": (38.9, -77.0)
    }

    # Add current location marker
    if base_state in state_coords:
        base_lat, base_lon = state_coords[base_state]

        # Current location - home marker
        fig.add_trace(go.Scattergeo(
            lon=[base_lon],
            lat=[base_lat],
            mode="markers",
            marker=dict(
                size=16,
                color="#2196F3",  # Blue for current
                symbol="circle",
                line=dict(width=3, color="white")
            ),
            name="Your Location",
            hoverinfo="text",
            hovertext=f"📍 {base_name} (You are here)"
        ))

    # Add target state marker and arc if provided
    if target_state and target_state in df["state_code"].values and target_state != base_state:
        target_row = df[df["state_code"] == target_state].iloc[0]
        target_name = target_row["state_name"]
        target_diff = target_row["relative_diff"]

        if target_state in state_coords and base_state in state_coords:
            target_lat, target_lon = state_coords[target_state]
            base_lat, base_lon = state_coords[base_state]

            # Marker color based on affordability
            marker_color = "#d73027" if target_diff > 0 else "#1a9850"

            # Create curved arc from base to target
            # Generate points along a great circle with an upward arc
            import numpy as np
            num_points = 50
            t = np.linspace(0, 1, num_points)

            # Interpolate lat/lon
            arc_lons = base_lon + t * (target_lon - base_lon)
            arc_lats = base_lat + t * (target_lat - base_lat)

            # Add upward curve (parabolic arc)
            # Peak at midpoint, scaled by distance
            distance = np.sqrt((target_lat - base_lat)**2 + (target_lon - base_lon)**2)
            arc_height = min(distance * 0.3, 8)  # Cap the arc height
            arc_lats = arc_lats + arc_height * 4 * t * (1 - t)  # Parabolic curve

            # Draw the arc line
            fig.add_trace(go.Scattergeo(
                lon=arc_lons.tolist(),
                lat=arc_lats.tolist(),
                mode="lines",
                line=dict(
                    width=3,
                    color=marker_color,
                    dash="dot"
                ),
                name="Route",
                hoverinfo="skip",
                showlegend=False
            ))

            # Add arrowhead at the end of arc (pointing to target)
            arrow_lat = arc_lats[-3]
            arrow_lon = arc_lons[-3]
            fig.add_trace(go.Scattergeo(
                lon=[arc_lons[-1]],
                lat=[arc_lats[-1]],
                mode="markers",
                marker=dict(
                    size=12,
                    color=marker_color,
                    symbol="triangle-down",
                    angle=0
                ),
                hoverinfo="skip",
                showlegend=False
            ))

            # Bullseye/target marker - outer ring
            fig.add_trace(go.Scattergeo(
                lon=[target_lon],
                lat=[target_lat],
                mode="markers",
                marker=dict(
                    size=35,
                    color="rgba(255,255,255,0.3)",
                    symbol="circle",
                    line=dict(width=3, color=marker_color)
                ),
                hoverinfo="skip",
                showlegend=False
            ))

            # Bullseye - middle ring
            fig.add_trace(go.Scattergeo(
                lon=[target_lon],
                lat=[target_lat],
                mode="markers",
                marker=dict(
                    size=24,
                    color="rgba(255,255,255,0.5)",
                    symbol="circle",
                    line=dict(width=2, color=marker_color)
                ),
                hoverinfo="skip",
                showlegend=False
            ))

            # Bullseye - center dot
            fig.add_trace(go.Scattergeo(
                lon=[target_lon],
                lat=[target_lat],
                mode="markers+text",
                marker=dict(
                    size=14,
                    color=marker_color,
                    symbol="circle",
                    line=dict(width=2, color="white")
                ),
                text=[target_name],
                textposition="top center",
                textfont=dict(size=11, color="white", family="Arial Black"),
                name="Target",
                hoverinfo="text",
                hovertext=f"🎯 {target_name}: {target_diff:+.1f}% vs your location"
            ))

    return fig


def get_affordability_summary(base_state: str, target_state: str) -> dict:
    """
    Get a summary of affordability between two states.

    Returns:
        Dictionary with comparison details
    """
    data = load_state_rpp()
    states = data.get("states", {})

    if base_state not in states or target_state not in states:
        return {"error": "Invalid state code"}

    base_info = states[base_state]
    target_info = states[target_state]

    overall_diff = ((target_info["rpp"] - base_info["rpp"]) / base_info["rpp"]) * 100
    housing_diff = ((target_info["housing"] - base_info["housing"]) / base_info["housing"]) * 100

    return {
        "base_state": base_state,
        "base_name": base_info["name"],
        "base_rpp": base_info["rpp"],
        "target_state": target_state,
        "target_name": target_info["name"],
        "target_rpp": target_info["rpp"],
        "overall_diff_percent": round(overall_diff, 1),
        "housing_diff_percent": round(housing_diff, 1),
        "is_cheaper": overall_diff < 0
    }
