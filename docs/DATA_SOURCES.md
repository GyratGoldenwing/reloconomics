# Reloconomics Data Sources

## Cost of Living Data

### 1. BEA Regional Price Parities (Primary Source)
**URL:** https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area

- **Coverage:** All 50 states + 380+ metro areas
- **Data:** Price levels as % of national average (100 = national average)
- **Categories:** All items, Goods, Services, Housing (rent)
- **Years Available:** 2008-2023
- **API:** Yes - requires free registration at http://www.bea.gov/api/signup/index.cfm
- **Format:** JSON via API, CSV download, Interactive tables

**Example:** California RPP = 112.6 (12.6% above national average)

### 2. BLS Consumer Expenditure Survey
**URL:** https://www.bls.gov/cex/

- **Coverage:** 4 regions, 9 divisions, selected metros
- **Data:** Actual dollar expenditures by category
- **Categories:** Housing, Food, Transportation, Healthcare, Utilities, etc.
- **Years Available:** 1984-2024
- **API:** Public Use Microdata (PUMD) files
- **Format:** CSV/XLSX tables, microdata files

**Note:** Metro-level data limited to ~20 major metros

### 3. HUD Fair Market Rents (Housing Only)
**URL:** https://www.huduser.gov/portal/datasets/fmr.html

- **Coverage:** Every county + ZIP code in US
- **Data:** 40th percentile rent by bedroom count
- **Years Available:** 2006-2025
- **API:** Yes - https://www.huduser.gov/portal/dataset/fmr-api.html
- **Format:** JSON via API, CSV download

**ZIP Code Data:** Small Area Fair Market Rents (SAFMRs)
- https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html


## Tax Data

### 4. Tax Foundation State Tax Rates
**URL:** https://taxfoundation.org/data/

- **Coverage:** All 50 states
- **Data:** Income tax brackets, rates, standard deductions
- **Updated:** Annually

### 5. IRS Federal Tax Brackets
**URL:** https://www.irs.gov/

- **Data:** Federal income tax brackets by filing status
- **Updated:** Annually


## Geographic Boundary Data (For Heat Maps)

### 6. Census Bureau Cartographic Boundaries (Official)
**URL:** https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html

- **Formats:** Shapefile, GeoJSON (via conversion), KML
- **Granularity:** Nation, State, County, ZIP Code Tabulation Areas
- **Resolution Options:** 500k (detailed), 5m (medium), 20m (simplified)

### 7. Pre-converted GeoJSON Files
**URL:** https://eric.clst.org/tech/usgeojson/

- **States:** gz_2010_us_040_00_500k.json (all US states)
- **Counties:** gz_2010_us_050_00_500k.json (all US counties)
- **Free to use** (US Government work - no copyright)

### 8. Plotly Built-in Datasets
**URL:** https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json

- Counties GeoJSON with FIPS codes
- Direct URL load in Python


## Implementation Priority

### MVP (Monday Deadline)
1. **BEA Regional Price Parities** - State + metro level, API available
2. **Census GeoJSON** - States only (simplified 20m)
3. **Plotly choropleth** - Built-in state support

### Phase 2 (Week 3-4)
1. **HUD Fair Market Rents** - County + ZIP granularity
2. **County GeoJSON** - Full county boundaries
3. **BLS Consumer Expenditure** - Detailed category breakdowns

### Phase 3 (Post-MVP)
1. **ZIP Code granularity** - ZCTA boundaries
2. **Historical trends** - 5-year data compilation
3. **Real-time updates** - API integration


## API Registration Required

| Source | Registration URL | Key Type |
|--------|-----------------|----------|
| BEA | http://www.bea.gov/api/signup/index.cfm | API Key |
| HUD | https://www.huduser.gov/portal/dataset/fmr-api.html | Bearer Token |
| BLS | https://www.bls.gov/developers/ | API Key (optional) |


## Data Refresh Schedule

| Source | Update Frequency | Latest Data |
|--------|-----------------|-------------|
| BEA RPP | Annual (December) | 2023 |
| HUD FMR | Annual (October) | FY2025 |
| BLS CE | Annual (September) | 2024 |
| Tax Foundation | Annual (January) | 2025 |
