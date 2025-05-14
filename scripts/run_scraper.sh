#!/bin/bash

# Define a list of years you want to scrape the data for
years=(2010 2005 2000 1995 1990 1985)

# Loop through each year and execute the Python script
for year in "${years[@]}"; do
    echo "Running script for year: $year"
    python3 fetch_data.py "$year"
done

echo "All data scraping completed."