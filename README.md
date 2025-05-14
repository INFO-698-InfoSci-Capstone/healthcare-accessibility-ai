# AI Healthcare Accessibility

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**Authors:** Ansh Dev, Akash Satpathy, Himanshu Nimbarte, and Jay Patil  
**Affiliation:** VIP Capstone Project (INFO 698) - College of Information Science

Dashboard Link: https://healthcare-application-fdkwtldzaq5mtthgvldkl7.streamlit.app

## Overview

This project leverages AI to improve healthcare accessibility insights across U.S. census tracts. It replaces traditional siloed spreadsheets and manual GIS workflows with a unified, AI-powered platform for instant, tract-level insights.

- Harmonize multi-source data into a single feature store.
- Visualize healthcare access metrics using interactive heatmaps and dashboards.
- Generate policy briefs and plain-language answers via a Gen-AI Q&A assistant.

## Data Sources

- Socio-Economic: American Community Survey (ACS) - 2023
- Disease Prevalence: CDC PLACES (Behavioral Risk & Chronic Disease) - 2024
- Healthcare Sites: OpenStreetMap “amenity” layer - 2024-04
- Hospital Beds: HHS Geospatial Management Office - 2023
- Shortage Areas: HRSA Health Professional Shortage Areas (HPSA) - Q1 2025

## File Organization

```
Healthcare-Accessibility-AI/
├── analysis/
│   ├── data/
│   │   ├── rawData/         # data obtained from elsewhere
│   │   └── derivedData/     # data generated from rawData/ and scripts.*
│   ├── logs/
│   │   └── log.md           # log of any progress or relevant information
│   └── scripts/             # scripts used for data processing/analysis
├── healthcare_application/
│   ├── data/                # data used by the Streamlit app
│   ├── pages/               # multi-page Streamlit layout files
│   ├── utils/               # functions and backend logic
│   ├── Home.py              # python script for the dashboard
│   └── requirements.txt     # dependencies to run the dashboard
├── src/
│   └── README.md
├── CONDUCT.md
├── DESCRIPTION
├── LICENSE                
└── README.md              
```
## Try It Out

Scan the QR code below to launch the live demo, or click the link if you’re on desktop:

[![Scan to Open Demo](https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://qr.link/rchkuO)](https://qr.link/rchkuO)

**Live Demo:** [https://qr.link/rchkuO](https://qr.link/rchkuO)
