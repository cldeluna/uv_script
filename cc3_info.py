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
import dotenv


def load_env_variables():
    """
    Load environment variables from .env file if it exists
    """
    try:

        # Load environment variables from .env file
        dotenv.load_dotenv()
        print("Environment variables loaded from .env file")
    except ImportError:
        print("Warning: python-dotenv not installed, skipping .env file loading")
    except Exception as e:
        print(f"Warning: Failed to load .env file: {e}")


def get_api_token(api_key: Optional[str] = None) -> str:
    """
    Get API token from command line argument or environment variable.

    Args:
        api_key: API key provided via command line argument

    Returns:
        API token to use for requests
    """
    # First try command line argument
    if api_key:
        return api_key

    # Then try environment variable
    evar_name = "CC3_API_TOKEN"
    env_token = os.environ.get(evar_name)
    if env_token:
        print(f"Found environment variable: {evar_name}")
        return env_token

    # No token found
    sys.exit(
        "Error: API token required. Please provide it via --api-key argument or set CC3_API_TOKEN environment variable.")


def get_country_codes_from_module() -> List[Dict[str, str]]:
    """
    Get all available country codes using the pycountry module.

    Returns:
        List of dictionaries containing country codes and names.
    """
    try:
        import pycountry
        countries = []
        for country in pycountry.countries:
            countries.append({
                "code": country.alpha_3,
                "name": country.name
            })

        # Sort by country name
        countries.sort(key=lambda x: x["name"])
        return countries

    except ImportError:
        print("Error: pycountry module not found. Make sure to run with 'uv run script.py'")
        print("Falling back to API method...")
        return []
    except Exception as e:
        print(f"Error fetching country codes from pycountry: {e}")
        print("Falling back to API method...")
        return []


def get_country_codes(api_token: str) -> List[Dict[str, str]]:
    """
    Fetch all available country codes from the Restful Countries API.

    Args:
        api_token: API token for authentication

    Returns:
        List of dictionaries containing country codes and names.
    """
    try:
        import requests
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_token}"
        }

        url = "https://restfulcountries.com/api/v1/countries"
        print(f"Requesting: {url}")

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the response
        data = response.json()

        if "data" not in data:
            print(f"Unexpected API response format: {data}")
            return []

        countries = []
        for country in data["data"]:
            if "iso3" in country and "name" in country:
                countries.append({
                    "code": country["iso3"],
                    "name": country["name"]
                })

        # Sort by country name
        countries.sort(key=lambda x: x["name"])
        return countries

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


def get_country_info(country_code: str, api_token: str) -> Dict[str, Any]:
    """
    Fetch detailed information about a country using its code from Restful Countries API.

    Args:
        country_code: 3-letter country code
        api_token: API token for authentication

    Returns:
        Dictionary containing country information
    """
    try:
        import requests
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_token}"
        }

        # Using the Restful Countries API for a specific country
        url = f"https://restfulcountries.com/api/v1/countries?iso3={country_code}"
        print(f"Requesting: {url}")

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()

        # Check if the response has the expected structure
        if "data" not in data or not data["data"]:
            print(f"No data found for country code: {country_code}")
            return {}

        # Return the first country that matches (should be only one)
        # return data["data"][0]
        return data["data"]

    except requests.RequestException as e:
        print(f"Error fetching country information: {e}")
        print("API endpoint might be experiencing issues. Please try again later.")
        return {}


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


    # Load environment variables
    load_env_variables()

    # Get API token
    api_token = get_api_token(arguments.api_key)

    # Get all country codes
    print("Fetching available country codes...")

    # Try using the module first, fall back to API if it fails
    country_codes = get_country_codes_from_module()
    if not country_codes:
        country_codes = get_country_codes(api_token)

    if not country_codes:
        print("Failed to fetch country codes. Exiting.")
        return

    # Select a country code
    country_code = select_country_code(country_codes, use_cli_selector=arguments.select)

    # Get and display country information
    print(f"\nFetching information for {country_code}...")
    country_info = get_country_info(country_code, api_token)
    for k, v in country_info.items():
        print(f"{k.upper()}: {v}")


# Standard call to the main() function.
if __name__ == '__main__':
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch information about a country using its 3-letter code",
                                     epilog="Usage: ' python cc3_info.py' ")
    parser.add_argument("-s", "--select", action="store_true", help="Show country selection interface")
    parser.add_argument("-a", "--use-api", action="store_true",
                        help="Use REST API instead of pycountry module for country codes")
    parser.add_argument("-k", "--api-key", type=str, help="API key for Restful Countries API")

    arguments = parser.parse_args()
    main()
