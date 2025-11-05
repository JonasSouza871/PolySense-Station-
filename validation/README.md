# INMET Weather Station Data - Validation Dataset

## Overview

This directory contains official meteorological data from the **Brazilian National Institute of Meteorology (Instituto Nacional de Meteorologia - INMET)**. This dataset serves as the validation reference for the PolySense Station project, providing ground truth measurements for comparison with the project's sensor data.

## Data Source

- **Organization**: Instituto Nacional de Meteorologia (INMET)
- **Country**: Brazil
- **Official Website**: [INMET - Tempo](https://tempo.inmet.gov.br)
- **Station Data Table**: [https://tempo.inmet.gov.br/TabelaEstacoes/A001](https://tempo.inmet.gov.br/TabelaEstacoes/A001)

## Dataset Information

### File Details

- **Filename**: `inmet_weather_station_data_sep_2025_utc.csv`
- **Period**: September 2025
- **Format**: CSV (Comma-Separated Values)
- **Delimiter**: Semicolon (`;`)
- **Encoding**: UTF-8 with BOM
- **Temporal Resolution**: Hourly measurements
- **Time Zone**: UTC (Coordinated Universal Time)

### Data Organization

The data is organized in a time-series format with hourly readings. Each row represents measurements taken at a specific date and hour (in UTC). The file contains 19 columns with various meteorological parameters.

## Column Structure

| Column | Portuguese Name | English Name | Unit | Description |
|--------|-----------------|--------------|------|-------------|
| 1 | Data | Date | DD/MM/YYYY | Date of measurement |
| 2 | Hora (UTC) | Hour (UTC) | HHMM | Hour in UTC format (24-hour) |
| 3 | Temp. Ins. (C) | Instantaneous Temperature | °C | Temperature at the specific moment |
| 4 | Temp. Max. (C) | Maximum Temperature | °C | Maximum temperature in the hour |
| 5 | Temp. Min. (C) | Minimum Temperature | °C | Minimum temperature in the hour |
| 6 | Umi. Ins. (%) | Instantaneous Humidity | % | Relative humidity at the specific moment |
| 7 | Umi. Max. (%) | Maximum Humidity | % | Maximum relative humidity in the hour |
| 8 | Umi. Min. (%) | Minimum Humidity | % | Minimum relative humidity in the hour |
| 9 | Pto Orvalho Ins. (C) | Instantaneous Dew Point | °C | Dew point temperature at the specific moment |
| 10 | Pto Orvalho Max. (C) | Maximum Dew Point | °C | Maximum dew point in the hour |
| 11 | Pto Orvalho Min. (C) | Minimum Dew Point | °C | Minimum dew point in the hour |
| 12 | Pressao Ins. (hPa) | Instantaneous Pressure | hPa | Atmospheric pressure at the specific moment |
| 13 | Pressao Max. (hPa) | Maximum Pressure | hPa | Maximum atmospheric pressure in the hour |
| 14 | Pressao Min. (hPa) | Minimum Pressure | hPa | Minimum atmospheric pressure in the hour |
| 15 | Vel. Vento (m/s) | Wind Speed | m/s | Wind speed |
| 16 | Dir. Vento (m/s) | Wind Direction | degrees | Wind direction in degrees (0-360°) |
| 17 | Raj. Vento (m/s) | Wind Gust | m/s | Maximum wind gust speed |
| 18 | Radiacao (KJ/m²) | Solar Radiation | KJ/m² | Solar radiation |
| 19 | Chuva (mm) | Rainfall | mm | Accumulated rainfall in the hour |

## Data Characteristics

### Number Format
- Decimal separator: Comma (`,`)
- Example: `17,9` represents 17.9

### Missing Values
- Empty strings (`""`) indicate missing or unavailable measurements
- Common for certain parameters during specific hours (e.g., solar radiation during nighttime)

### Measurement Types
The dataset includes three types of measurements for most parameters:
1. **Instantaneous (Ins.)**: Point measurement at the specific hour
2. **Maximum (Max.)**: Highest value recorded during the hour
3. **Minimum (Min.)**: Lowest value recorded during the hour

## Purpose

This dataset serves as the **validation reference** for the PolySense Station project. By comparing the sensor measurements from the PolySense Station with this official INMET data, we can:

- Validate the accuracy of custom sensors
- Calibrate measurement instruments
- Identify systematic errors or biases
- Assess the reliability of the monitoring system
- Verify data quality and consistency

## Usage Recommendations

When using this data for validation:

1. **Time Synchronization**: Ensure PolySense Station data is converted to UTC for accurate comparison
2. **Data Cleaning**: Handle missing values appropriately in your analysis
3. **Number Format**: Convert decimal commas to dots for numerical processing in most programming languages
4. **Spatial Considerations**: Consider the geographical distance between INMET station and PolySense Station location
5. **Temporal Resolution**: Align the temporal resolution of both datasets (hourly in this case)

## License and Citation

This data is provided by INMET, the official meteorological service of Brazil. When using this data, please cite:

```
Instituto Nacional de Meteorologia (INMET)
Source: https://tempo.inmet.gov.br/TabelaEstacoes/A001
```

## Contact

For more information about INMET data and services, visit:
- Website: [https://portal.inmet.gov.br](https://portal.inmet.gov.br)
- Data Portal: [https://tempo.inmet.gov.br](https://tempo.inmet.gov.br)
