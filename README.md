# MCH Kit Analysis Dashboard

A Streamlit dashboard for analyzing Mother and Child Health Kit distribution and related metrics.

## Features

- Key metrics overview including district, mandal, and village statistics
- Registration trends by district
- ANC visit progression analysis
- Geographical distribution of kit distribution
- Delivery statistics
- Statistical correlations
- Interactive data explorer

## Requirements

- Python 3.7+
- Required packages are listed in `requirements.txt`

## Data

The dashboard expects a file named `deepu.csv` in the root directory with the following columns:
- districtName
- mandalName
- villageName
- pwRegCnt
- anc1Cnt
- anc2Cnt
- anc3Cnt
- anc4Cnt
- delCnt
- kitsCnt

## Running Locally

```bash
streamlit run mch_dashboard_v2.py
```
