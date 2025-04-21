#!/usr/bin/env -S uv run

# Reminder to set script as executable in the terminal: chmod u+x script.py and
# change shebang from #!/usr/bin/python -tt to #!/usr/bin/env -S uv run

# Project: uv_script
# Filename: cc3_info.py
# claudiadeluna
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "4/21/25"
__copyright__ = "Copyright (c) 2023 Claudia"
__license__ = "Python"



# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pycountry>=24.2.0",
#     "requests>=2.31.0",
#     "python-dotenv>=1.0.0",
# ]
# ///


import argparse
import json
import time
import sys
import os

from typing import List, Dict, Any, Optional

import requests
import pycountry

def get_country_codes_from_module() -> List[Dict[str, str]]:
    """
    Get all available country codes using the pycountry module.

    Returns:
        List of dictionaries containing country codes and names.
    """
    try:
        countries = []
        for country in pycountry.countries:
            countries.append({
                "code": country.alpha_3,
                "name": country.name
            })

        # Sort by country name
        countries.sort(key=lambda x: x["name"])
        return countries

    except Exception as e:
        print(f"Error fetching country codes from pycountry: {e}")
        print("Falling back to API method...")
        return []


def get_country_codes() -> List[Dict[str, str]]:
    """
    Fetch all available country codes from the REST Countries API.

    Returns:
        List of dictionaries containing country codes and names.
    """
    try:
        response = requests.get("https://restcountries.com/v3.1/all")
        response.raise_for_status()

        countries = response.json()
        country_codes = []

        for country in countries:
            if "cca3" in country and "name" in country:
                country_codes.append({
                    "code": country["cca3"],
                    "name": country["name"]["common"]
                })

        # Sort by country name
        country_codes.sort(key=lambda x: x["name"])
        return country_codes

    except requests.RequestException as e:
        print(f"Error fetching country codes: {e}")
        return []


def get_country_codes_api() -> List[Dict[str, str]]:
    """
    Fetch all available country codes from the REST Countries API.

    Returns:
        List of dictionaries containing country codes and names.
    """
    try:
        import requests
        # Updated endpoint to v3.1
        response = requests.get("https://restcountries.com/v3.1/all")
        response.raise_for_status()

        countries = response.json()
        country_codes = []

        for country in countries:
            # Updated to match v3.1 schema
            if "cca3" in country and "name" in country:
                country_codes.append({
                    "code": country["cca3"],
                    "name": country["name"]["common"]
                })

        # Sort by country name
        country_codes.sort(key=lambda x: x["name"])
        return country_codes

    except requests.RequestException as e:
        print(f"Error fetching country codes: {e}")
        return []


def display_country_list(country_codes: List[Dict[str, str]], page_size: int = 20) -> None:
    """
    Display a paginated list of countries with their codes.

    Args:
        country_codes: List of dictionaries containing country codes and names
        page_size: Number of countries to display per page
    """
    total_countries = len(country_codes)
    total_pages = (total_countries + page_size - 1) // page_size
    current_page = 1

    while True:
        # Calculate start and end indices for the current page
        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_countries)

        # Clear the screen (works on Unix/Windows)
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"\nCountry List (Page {current_page}/{total_pages}):")
        print("=" * 50)

        # Display countries for the current page
        for i in range(start_idx, end_idx):
            country = country_codes[i]
            print(f"{i + 1:3d}. {country['name']} ({country['code']})")

        print("=" * 50)
        print("Navigation: [n]ext page, [p]revious page, [q]uit navigation")
        print("Or enter the number or 3-letter code of the country to select")

        choice = input("\nYour choice: ").strip().lower()

        # Check if input is a number
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < total_countries:
                return country_codes[index]["code"]
            else:
                print(f"Please enter a number between 1 and {total_countries}")
                time.sleep(1)

        # Check if input is a country code
        elif len(choice) == 3:
            choice = choice.upper()
            for country in country_codes:
                if country["code"].upper() == choice:
                    return choice
            print(f"Country code '{choice}' not found. Please try again.")
            time.sleep(1)

        # Navigation commands
        elif choice == 'n':
            if current_page < total_pages:
                current_page += 1
        elif choice == 'p':
            if current_page > 1:
                current_page -= 1
        elif choice == 'q':
            return None
        else:
            print("Invalid input. Please try again.")
            time.sleep(1)


def select_country_code(country_codes: List[Dict[str, str]], use_cli_selector: bool = False) -> str:
    """
    Allow user to select a country code from the list.

    Args:
        country_codes: List of dictionaries containing country codes and names
        use_cli_selector: Whether to use the CLI selector interface

    Returns:
        Selected country code
    """
    if use_cli_selector:
        # Use the CLI selector interface
        selected_code = display_country_list(country_codes)
        if selected_code:
            # Find the country name for the selected code
            for country in country_codes:
                if country["code"] == selected_code:
                    print(f"Selected country: {country['name']} ({selected_code})")
                    return selected_code
            # If we get here, something went wrong
            print(f"Selected code '{selected_code}' not found in country list, using default (CZE)")
            return "CZE"
        else:
            # User quit the selector, use default
            print("No selection made, using default country (CZE)")
            return "CZE"
    else:
        # Default behavior - use Czech Republic
        print("Using default country: Czech Republic (CZE)")
        return "CZE"


def get_country_info(country_code: str) -> Dict[str, Any]:
    """
    Fetch detailed information about a country using its code.

    Args:
        country_code: 3-letter country code

    Returns:
        Dictionary containing country information
    """
    try:
        import requests
        # Updated endpoint to v3.1
        url = f"https://restcountries.com/v3.1/alpha/{country_code}"
        print(f"Requesting: {url}")
        response = requests.get(url)
        response.raise_for_status()

        return response.json()[0]

    except requests.RequestException as e:
        print(f"Error fetching country information: {e}")
        print("API endpoint might be experiencing issues. Please try again later.")
        return {}


def display_country_info(country_info: Dict[str, Any]) -> None:
    """
    Display formatted country information from v3.1 API format.

    Args:
        country_info: Dictionary containing country information
    """
    if not country_info:
        print("No country information available.")
        return

    print("\n===== COUNTRY INFORMATION =====\n")

    # Basic information (updated for v3.1 schema)
    print(f"Name: {country_info.get('name', {}).get('common', 'N/A')}")
    print(f"Official Name: {country_info.get('name', {}).get('official', 'N/A')}")

    # Capital (handling potential list)
    capitals = country_info.get('capital', ['N/A'])
    if isinstance(capitals, list):
        print(f"Capital: {', '.join(capitals)}")
    else:
        print(f"Capital: {capitals}")

    print(f"Region: {country_info.get('region', 'N/A')}")
    print(f"Subregion: {country_info.get('subregion', 'N/A')}")

    # Population
    print(f"Population: {country_info.get('population', 'N/A'):,}")

    # Area
    area = country_info.get('area', 'N/A')
    if isinstance(area, (int, float)):
        print(f"Area: {area:,} km²")
    else:
        print(f"Area: {area}")

    # Languages (updated for v3.1 schema)
    languages = country_info.get('languages', {})
    if languages:
        print("Languages:")
        for code, language in languages.items():
            print(f"  - {language} ({code})")

    # Currencies (updated for v3.1 schema)
    currencies = country_info.get('currencies', {})
    if currencies:
        print("Currencies:")
        for code, currency_info in currencies.items():
            print(f"  - {currency_info.get('name', 'N/A')} ({code})")
            print(f"    Symbol: {currency_info.get('symbol', 'N/A')}")

    # Flags (updated for v3.1 schema)
    print(f"Flag: {country_info.get('flags', {}).get('png', 'N/A')}")

    # Borders
    borders = country_info.get('borders', [])
    if borders:
        print("Borders with:")
        for border in borders:
            print(f"  - {border}")

    # Timezone
    timezones = country_info.get('timezones', [])
    if timezones:
        print("Timezones:")
        for timezone in timezones:
            print(f"  - {timezone}")


def main():
    """
    Country Information CLI Tool

    This script allows users to select a country using its 3-letter ISO code
    and retrieve information about it from a REST API.

    Usage:
      uv run script.py [-s|--select COUNTRY_CODE] [--use-api]

    Example:
        uv run script.py -s USA
        uv run script.py --select CZE

        uv run script.py (uses pycountry module with default CZE)
        uv run script.py -s USA (uses pycountry module and selects USA)
        uv run script.py --use-api (forces use of REST API with default CZE)
        uv run script.py -s GBR --use-api (forces use of REST API and selects GBR)

    """

    print("\n----- Dynamic On-demand Virtual Environment Details -----")
    print(f"\tPython version: {'.'.join(map(str, sys.version_info[:3]))}")
    print(f"\tVirtual environment path: {sys.prefix}\n")


    # Get selected code or use default (Czech Republic - CZE)
    # selected_code = arguments.select if arguments.select else "CZE"

    # Get all country codes
    print("Fetching available country codes...")

    if arguments.use_api:
        country_codes = get_country_codes_api()
    else:
        # Try using the module first, fall back to API if it fails
        country_codes = get_country_codes_from_module()
        if not country_codes:
            country_codes = get_country_codes_api()

    if not country_codes:
        print("Failed to fetch country codes. Exiting.")
        return

    # Select a country code
    # country_code = select_country_code(country_codes, selected_code)
    # Select a country code
    country_code = select_country_code(country_codes, use_cli_selector=arguments.select)

    # Get and display country information
    print(f"\nFetching information for {country_code}...")
    country_info = get_country_info(country_code)
    display_country_info(country_info)


# Standard call to the main() function.
if __name__ == '__main__':
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch information about a country using its 3-letter code",
                                     epilog="Usage: ' python cc3_info.py' ")
    parser.add_argument("-s", "--select", action="store_true", help="Show country selection interface")
    parser.add_argument("--use-api", action="store_true",
                        help="Use REST API instead of pycountry module for country codes")
    arguments = parser.parse_args()
    main()
