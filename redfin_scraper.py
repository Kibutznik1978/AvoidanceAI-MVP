import re
import json
from dataclasses import dataclass, asdict
from typing import List

import requests
from bs4 import BeautifulSoup


@dataclass
class Listing:
    """Container for Redfin listing information."""

    address: str = ""
    home_type: str = ""
    square_footage: str = ""
    rooms: str = ""
    bathrooms: str = ""
    year_built: str = ""
    amenities: List[str] = None
    description: str = ""


def _extract_detail(soup: BeautifulSoup, label: str) -> str:
    """Search for a label/value pair within the property details table."""

    node = soup.find("div", string=re.compile(label, re.I))
    if not node:
        return ""
    value_node = node.find_next_sibling("div")
    return value_node.get_text(strip=True) if value_node else ""


def fetch_listing(url: str) -> Listing:
    """Fetch and parse a Redfin listing page."""

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    listing = Listing(amenities=[])

    # Address
    street = soup.find("span", {"data-rf-test-id": "street-address"})
    city = soup.find("span", {"data-rf-test-id": "cityStateZip"})
    if street and city:
        listing.address = f"{street.get_text(strip=True)}, {city.get_text(strip=True)}"

    # Property details
    listing.home_type = _extract_detail(soup, "Property Type")
    listing.square_footage = _extract_detail(soup, "Square Feet")
    listing.rooms = _extract_detail(soup, "Beds")
    listing.bathrooms = _extract_detail(soup, "Baths")
    listing.year_built = _extract_detail(soup, "Year Built")

    # Amenities
    amenities_section = soup.find("div", {"data-rf-test-id": "amenities"})
    if amenities_section:
        listing.amenities = [li.get_text(strip=True) for li in amenities_section.find_all("li")]

    # Listing description
    desc_section = soup.find("div", {"data-rf-test-id": "abp-description"})
    if desc_section:
        listing.description = desc_section.get_text(strip=True)

    return listing


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape a Redfin listing")
    parser.add_argument("url", help="URL of the Redfin property listing")
    args = parser.parse_args()

    listing = fetch_listing(args.url)
    print(json.dumps(asdict(listing), indent=2, ensure_ascii=False))
