import pandas as pd
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from playwright.async_api import async_playwright
import os

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

# Define address-related keywords
ADDRESS_KEYWORDS = ["address", "street"]
CITY_KEYWORDS = ["city", "town"]
STATE_KEYWORDS = ["state"]
ZIP_KEYWORDS = ["zip", "zipcode", "postal"]

def detect_address_columns(df):
    """Detect relevant address fields in the uploaded spreadsheet."""
    address_col = next((col for col in df.columns if any(word in col.lower() for word in ADDRESS_KEYWORDS)), None)
    city_col = next((col for col in df.columns if any(word in col.lower() for word in CITY_KEYWORDS)), None)
    state_col = next((col for col in df.columns if any(word in col.lower() for word in STATE_KEYWORDS)), None)
    zip_col = next((col for col in df.columns if any(word in col.lower() for word in ZIP_KEYWORDS)), None)

    return address_col, city_col, state_col, zip_col

def construct_search_url(address, city, state, zip_code):
    """Generate a Google search link for Zillow results."""
    query = f"{address}, {city}, {state} {zip_code} site:zillow.com"
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    return search_url

@app.post("/api/process/")
async def process_csv(file: UploadFile = File(...)):
    try:
        # Determine file extension
        filename = file.filename.lower()
        if filename.endswith(".xlsx"):
            df = pd.read_excel(file.file, engine="openpyxl")
        elif filename.endswith(".xls"):
            df = pd.read_excel(file.file, engine="xlrd")
        elif filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload .xlsx, .xls, or .csv")

        # Detect address-related columns
        address_col, city_col, state_col, zip_col = detect_address_columns(df)

        if not address_col or not city_col or not state_col or not zip_col:
            return JSONResponse(
                content={"message": "Missing address-related columns in the spreadsheet."}, status_code=400
            )

        # Create Zillow search links
        df["Zillow_Search_Link"] = df.apply(
            lambda row: construct_search_url(
                row[address_col], row[city_col], row[state_col], row[zip_col]
            ), axis=1
        )

        # Save the updated file
        output_path = "processed_results.csv"
        df.to_csv(output_path, index=False)

        return FileResponse(output_path, filename="updated_addresses.csv")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/api/")
def read_root():
    return {"message": "FastAPI is running! at /api/"}

async def process_csv(file: UploadFile = File(...)):
    output_path = "processed_results.csv"
    df.to_csv(output_path, index=False)

    # Check if file exists before returning
    if not os.path.exists(output_path):
        raise HTTPException(status_code=500, detail="File not found")

    return FileResponse(output_path, filename="updated_addresses.csv")
async def search_zillow(address):
    """Search for a Zillow link using Google search"""
    search_query = f'site:zillow.com "{address}"'
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.google.com/search?q={search_query}", timeout=60000)
        await page.wait_for_selector("a", timeout=10000)
        
        links = await page.locator("a").evaluate_all("elements => elements.map(el => el.href)")
        zillow_links = [link for link in links if "zillow.com" in link]
        
        await browser.close()
        return zillow_links[0] if zillow_links else "No Match"

@app.post("/api/process/")
async def process_csv(file: UploadFile = File(...)):
    """Process the uploaded CSV file, search Zillow, and return updated CSV."""
    df = pd.read_csv(file.file)
    df["Zillow Link"] = await asyncio.gather(*(search_zillow(addr) for addr in df["Address"]))

    output_path = "processed_results.csv"
    df.to_csv(output_path, index=False)
    
    return FileResponse(output_path, filename="updated_addresses.csv")
