from flask import Blueprint, request, jsonify
import requests
import os
import re
import logging
import boto3
from decimal import Decimal

routes = Blueprint("routes", __name__)
logger = logging.getLogger(__name__)

# ✅ AWS DynamoDB Table
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
usage_table = dynamodb.Table("RealtyEnrichUsage")

# ✅ Load API Keys from Environment
SCRAPEAK_API_KEY = os.getenv("SCRAPEAK_API_KEY")
GOOGLE_CX_ID = os.getenv("GOOGLE_CX_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ✅ Function to Search Zillow Link
def search_zillow_link(address):
    """Searches Zillow link using Google API."""
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {"q": f"{address} site:zillow.com", "cx": GOOGLE_CX_ID, "key": GOOGLE_API_KEY}

    response = requests.get(search_url, params=params)
    data = response.json()

    if "items" in data:
        for item in data["items"]:
            link = item.get("link", "")
            if "zillow.com/homedetails" in link:
                return link

    return None

# ✅ Extract ZPID from Zillow URL
def extract_zpid(link):
    """Extracts ZPID from Zillow URL."""
    match = re.search(r'/(\d+)_zpid', link)
    return match.group(1) if match else None

# ✅ Route: Search Zillow
@routes.route('/search', methods=['POST'])
def search_address():
    """Searches Zillow for property details by address."""
    data = request.json
    address = data.get("address")

    if not address:
        return jsonify({"error": "Missing address"}), 400

    zillow_link = search_zillow_link(address)
    zpid = extract_zpid(zillow_link) if zillow_link else None

    return jsonify({"address": address, "zillow_link": zillow_link, "zpid": zpid})

# ✅ Route: Enrich Property Data
@routes.route('/enrich', methods=['POST'])
def enrich_property():
    """Fetches enriched property data using Scrapeak API."""
    data = request.json
    zpid = data.get("zpid")

    if not zpid:
        return jsonify({"error": "Missing ZPID"}), 400

    response = requests.get("https://app.scrapeak.com/v1/scrapers/zillow/property",
                            params={"api_key": SCRAPEAK_API_KEY, "zpid": zpid})

    if response.status_code == 200:
        return jsonify({"zpid": zpid, "data": response.json().get("data", {})})
    
    return jsonify({"error": "Failed to retrieve data from Scrapeak"})
