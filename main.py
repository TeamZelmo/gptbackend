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

# Professional Root Dashboard with Buttons
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ChatGPT Automation Dashboard</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f172a, #1e293b);
                color: #f8fafc;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .card {
                background: rgba(30, 41, 59, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 16px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
                text-align: center;
                max-width: 450px;
                width: 90%;
            }
            h1 {
                margin-bottom: 10px;
                font-size: 24px;
                color: #38bdf8;
            }
            p {
                color: #94a3b8;
                font-size: 14px;
                margin-bottom: 30px;
            }
            .btn-container {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .btn {
                display: block;
                width: 100%;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: 600;
                text-decoration: none;
                border-radius: 8px;
                transition: all 0.3s ease;
                box-sizing: border-box;
            }
            .btn-primary {
                background-color: #0ea5e9;
                color: white;
            }
            .btn-primary:hover {
                background-color: #0284c7;
                box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
            }
            .btn-secondary {
                background-color: #334155;
                color: #f8fafc;
                border: 1px solid #475569;
            }
            .btn-secondary:hover {
                background-color: #475569;
                box-shadow: 0 4px 12px rgba(71, 85, 105, 0.4);
            }
            .status-badge {
                display: inline-block;
                width: 10px;
                height: 10px;
                background-color: #22c55e;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-text {
                font-size: 12px;
                color: #22c55e;
                margin-bottom: 20px;
                font-weight: 500;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <div>
                <span class="status-badge"></span>
                <span class="status-text">System Online & Active</span>
            </div>
            <h1>ChatGPT Automation</h1>
            <p>Manage your API keys, view documentation, and monitor automation statuses seamlessly.</p>
            
            <div class="btn-container">
                <a href="/docs" class="btn btn-primary">📖 API Documentation (Swagger)</a>
                <a href="/admin/keys" class="btn btn-secondary">🔑 View Active API Keys</a>
            </div>
        </div>
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
    
