# README for data used in TBD

## Overview 
Data used for manuscript: TBD

***

## Purpose of the study 
### To examine spatial and socioeconomic disparities in healthcare accessibility across U.S. census tracts using geospatial, demographic, and public health datasets. This includes quantifying healthcare facility access, evaluating community-level social determinants of health, and identifying underserved areas.

## Structure of the data
Note: Columns should have information about units, number of levels, or format where appropriate.

#### socio_economic.csv  
###### Data set #1: Socioeconomic indicators from the 2021 American Community Survey (ACS 5-Year Estimates) at the census tract level.
* GEOID: Unique 11-digit census tract identifier
* Median_Household_Income: Median income of households (USD)
* Poverty_Population: Number of individuals below poverty line
* Unemployed_Population: Number of unemployed individuals (age 16+)
* Per_Capita_Income: Average income per person (USD)
* SNAP_Recipients: Number of households receiving SNAP benefits
* Total_Pop_Health_Insurance: Total population for insurance coverage
* Uninsured_Population: Individuals without health insurance
* Medicaid_Coverage: Individuals covered by Medicaid
* Medicare_Coverage: Individuals covered by Medicare
* Private_Insurance_Coverage: Individuals with private health insurance
* High_School_Graduates: Count of adults with high school diploma
* Bachelor_Degree_Holders: Count of adults with bachelor’s degree
* Less_than_High_School: Adults without high school education
* Households_No_Vehicle: Households with no vehicle access
* Commute_Time: Average commute time (minutes)
* Public_Transit_Usage: Number of commuters using public transit
* Renter_Occupied_Housing: Number of renter-occupied housing units
* Rent_as_Income_Percentage: Median rent as % of household income
* Overcrowded_Housing: Count of overcrowded housing units
* Elderly_Population: Population aged 65 and older
* Children_Population: Population under age 18
* White_Population: Number of individuals identifying as White
* Black_Population: Number of individuals identifying as Black or African American
* Disability_Population: Number of individuals with a disability
* Limited_English_Proficiency: Population with limited English
* Households_No_Internet: Households without internet access

#### census_with_healthcare_counts.geojson  
###### Data set #2: Spatial accessibility to healthcare facilities by census tract centroid using 5 km buffers.
* geometry: Latitude/longitude point geometry (EPSG:4326)
* hospital: Count of hospitals within 5 km
* clinic: Count of clinics within 5 km
* pharmacy: Count of pharmacies within 5 km
* doctors: Count of doctor offices within 5 km
* dentist: Count of dental clinics within 5 km
* nursing_home: Count of nursing homes within 5 km
* social_facility: Count of social service facilities within 5 km

#### 500_Cities__Census_Tract-level_Data__GIS_Friendly_Format___2019_release_20250317.csv  
###### Data set #3: Public health indicators by census tract from the PLACES dataset (CDC).
* StateAbbr: State abbreviation (e.g., AZ)
* PlaceName: Name of city or place
* PlaceFIPS: FIPS code of the place
* TractFIPS: FIPS code of the census tract
* Place_TractID: Combined place and tract ID
* Population2010: Total population (2010 Census)
* ACCESS2_CrudePrev / ACCESS2_Crude95CI: % adults with no access to healthcare / Confidence Interval
* ARTHRITIS_CrudePrev / ARTHRITIS_Crude95CI: % with arthritis
* BINGE_CrudePrev / BINGE_Crude95CI: % engaging in binge drinking
* BPHIGH_CrudePrev / BPHIGH_Crude95CI: % with high blood pressure
* BPMED_CrudePrev / BPMED_Crude95CI: % taking blood pressure medication
* CANCER_CrudePrev / CANCER_Crude95CI: % ever told they had cancer
* CASTHMA_CrudePrev / CASTHMA_Crude95CI: % with current asthma
* CHD_CrudePrev / CHD_Crude95CI: % with coronary heart disease
* CHECKUP_CrudePrev / CHECKUP_Crude95CI: % with routine checkup in past year
* CHOLSCREEN_CrudePrev / CHOLSCREEN_Crude95CI: % screened for cholesterol
* COLON_SCREEN_CrudePrev / COLON_SCREEN_Crude95CI: % with colon cancer screening
* COPD_CrudePrev / COPD_Crude95CI: % with COPD
* COREM_CrudePrev / COREM_Crude95CI: % women 50–74 with mammogram
* COREW_CrudePrev / COREW_Crude95CI: % men 50–75 with colorectal screening
* CSMOKING_CrudePrev / CSMOKING_Crude95CI: % current smokers
* DENTAL_CrudePrev / DENTAL_Crude95CI: % with recent dental visit
* DIABETES_CrudePrev / DIABETES_Crude95CI: % with diabetes
* HIGHCHOL_CrudePrev / HIGHCHOL_Crude95CI: % with high cholesterol
* KIDNEY_CrudePrev / KIDNEY_Crude95CI: % with kidney disease
* LPA_CrudePrev / LPA_Crude95CI: % with no physical activity
* MAMMOUSE_CrudePrev / MAMMOUSE_Crude95CI: % of women who had mammogram
* MHLTH_CrudePrev / MHLTH_Crude95CI: % reporting poor mental health
* OBESITY_CrudePrev / OBESITY_Crude95CI: % with obesity
* PAPTEST_CrudePrev / PAPTEST_Crude95CI: % women with recent Pap test
* PHLTH_CrudePrev / PHLTH_Crude95CI: % reporting poor physical health
* SLEEP_CrudePrev / SLEEP_Crude95CI: % adults getting <7 hours of sleep
* STROKE_CrudePrev / STROKE_Crude95CI: % ever told they had a stroke
* TEETHLOST_CrudePrev / TEETHLOST_Crude95CI: % with 6+ teeth lost
* Geolocation: Latitude and longitude of tract centroid

***
