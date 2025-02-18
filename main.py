import pandas as pd
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from playwright.async_api import async_playwright
import os

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

# Define address-related keywords
ADDRESS_KEYWORDS = ["address", "street", "city", "state", "zip", "location"]

def detect_address_columns(df):
    """Detect columns related to addresses dynamically."""
    address_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ADDRESS_KEYWORDS)]
    return address_columns

@app.post("/api/process/")
async def process_csv(file: UploadFile = File(...)):
    try:
        # Read the uploaded file into a DataFrame
        df = pd.read_excel(file.file)  # Use `pd.read_csv(file.file)` if it's a CSV

        # Detect address columns
        address_columns = detect_address_columns(df)

        if not address_columns:
            raise HTTPException(status_code=400, detail="No address-related columns found in the spreadsheet.")

        # For testing, print the detected columns
        print(f"Detected address columns: {address_columns}")

        # Here, you would add logic to search Zillow using these columns
        # (for now, we will just return the detected columns)

        # Save processed results (optional)
        output_path = "processed_results.csv"
        df.to_csv(output_path, index=False)

        return {"message": "Address columns detected", "columns": address_columns}
    
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
