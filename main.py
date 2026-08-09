import random
import secrets
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from playwright.async_api import async_playwright
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PaymentRequest(BaseModel):
    session_token: str
    api_key: str

class KeyGenRequest(BaseModel):
    limit: int = 5

# Runtime memory storage for API Keys
API_DATABASE = {
    "my_secret_key_123": {"limit": 5, "used": 0}
}

INDIAN_ADDRESSES = [
    {"address": "Flat 101, Boring Road", "city": "Patna", "state": "BR", "postal": "800001"},
    {"address": "B-21, Connaught Place", "city": "New Delhi", "state": "DL", "postal": "110001"},
    {"address": "A-12, MG Road", "city": "Mumbai", "state": "MH", "postal": "400001"},
    {"address": "5th Cross, Indiranagar", "city": "Bengaluru", "state": "KA", "postal": "560001"},
    {"address": "14, Park Street", "city": "Kolkata", "state": "WB", "postal": "700001"}
]

# Root Endpoint (Not Found error fix karne ke liye)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head><title>ChatGPT Automation API</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>ChatGPT Automation Backend is Live!</h1>
            <p>API documentation ke liye <a href="/docs">/docs</a> par jayein.</p>
        </body>
    </html>
    """

# Admin Endpoint: Saari keys aur unka status dekhne ke liye
@app.get("/admin/keys")
async def get_all_keys():
    return {"status": "success", "keys": API_DATABASE}

# Admin Endpoint: Nayi API Key generate karne ke liye
@app.post("/generate-key")
async def generate_api_key(data: KeyGenRequest):
    new_key = f"sk_live_{secrets.token_hex(8)}"
    API_DATABASE[new_key] = {
        "limit": data.limit,
        "used": 0
    }
    return {
        "status": "success",
        "api_key": new_key,
        "limit": data.limit
    }

@app.post("/start-checkout")
async def start_checkout(data: PaymentRequest):
    if data.api_key not in API_DATABASE:
        raise HTTPException(status_code=401, detail="Invalid API Key!")
    
    key_info = API_DATABASE[data.api_key]
    if key_info["used"] >= key_info["limit"]:
        raise HTTPException(
            status_code=403, 
            detail=f"API Limit Reached! Allowed: {key_info['limit']}, Used: {key_info['used']}"
        )
    
    key_info["used"] += 1
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        await context.add_cookies([
            {
                "name": "__Secure-next-auth.session-token",
                "value": data.session_token,
                "domain": ".chatgpt.com",
                "path": "/",
                "secure": True,
                "httpOnly": True,
            }
        ])
        
        page = await context.new_page()
        
        try:
            await page.goto("https://chatgpt.com/?action=show_upgrade")
            await page.wait_for_load_state("networkidle")
            
            try:
                await page.select_option("select[name='country']", "IN", timeout=5000)
            except Exception:
                pass

            random_addr = random.choice(INDIAN_ADDRESSES)
            try:
                await page.fill("input[name='addressLine1']", random_addr["address"])
                await page.fill("input[name='postalCode']", random_addr["postal"])
                await page.select_option("select[name='state']", random_addr["state"])
            except Exception:
                pass

            try:
                payment_frame = page.frame_locator("iframe[title*='Secure payment input frame']")
                upi_option = payment_frame.locator("text=UPI")
                if await upi_option.is_visible(timeout=5000):
                    await upi_option.click()
            except Exception:
                pass

            await page.wait_for_timeout(10000)
            await browser.close()
            
            remaining = key_info["limit"] - key_info["used"]
            return {
                "status": "success", 
                "message": "Automation completed.",
                "limit_remaining": remaining
            }
            
        except Exception as e:
            await browser.close()
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    
