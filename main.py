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

class IncreaseLimitRequest(BaseModel):
    api_key: str
    extra_limit: int

# Runtime memory storage for API Keys
API_DATABASE = {
    "sk_live_my_secret_key_123": {"limit": 5, "used": 0}
}

INDIAN_ADDRESSES = [
    {"address": "Flat 101, Boring Road", "city": "Patna", "state": "BR", "postal": "800001"},
    {"address": "B-21, Connaught Place", "city": "New Delhi", "state": "DL", "postal": "110001"},
    {"address": "A-12, MG Road", "city": "Mumbai", "state": "MH", "postal": "400001"},
    {"address": "5th Cross, Indiranagar", "city": "Bengaluru", "state": "KA", "postal": "560001"},
    {"address": "14, Park Street", "city": "Kolkata", "state": "WB", "postal": "700001"}
]

# Professional Dashboard & Login UI
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ChatGPT Automation Admin Panel</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #0f172a;
                color: #f8fafc;
                margin: 0;
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .container {
                width: 100%;
                max-width: 600px;
                background: #1e293b;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
                border: 1px solid #334155;
            }
            h2 {
                color: #38bdf8;
                text-align: center;
                margin-bottom: 20px;
            }
            .hidden { display: none !important; }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                font-size: 14px;
                margin-bottom: 5px;
                color: #94a3b8;
            }
            input {
                width: 100%;
                padding: 10px;
                background: #0f172a;
                border: 1px solid #475569;
                color: white;
                border-radius: 6px;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 10px;
                background: #0ea5e9;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.2s;
            }
            button:hover { background: #0284c7; }
            .key-card {
                background: #0f172a;
                border: 1px solid #334155;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
            .key-header {
                display: flex;
                justify-content: space-between;
                font-weight: bold;
                color: #38bdf8;
                font-size: 14px;
                word-break: break-all;
            }
            .badge-active { color: #22c55e; background: rgba(34, 197, 94, 0.1); padding: 2px 8px; border-radius: 4px; font-size: 12px; }
            .badge-exhausted { color: #ef4444; background: rgba(239, 68, 68, 0.1); padding: 2px 8px; border-radius: 4px; font-size: 12px; }
            .stats-row {
                display: flex;
                justify-content: space-between;
                font-size: 13px;
                color: #94a3b8;
                margin-top: 8px;
            }
            .actions-row {
                display: flex;
                gap: 10px;
                margin-top: 10px;
            }
            .btn-sm {
                padding: 5px 10px;
                font-size: 12px;
                background: #334155;
            }
            .btn-sm:hover { background: #475569; }
            .error-msg { color: #ef4444; text-align: center; font-size: 14px; margin-top: 10px; }
            .success-msg { color: #22c55e; text-align: center; font-size: 14px; margin-top: 10px; }
        </style>
    </head>
    <body>

    <div class="container">
        <!-- LOGIN SECTION -->
        <div id="loginSection">
            <h2>🔐 Admin Login</h2>
            <div class="form-group">
                <label>Admin Password</label>
                <input type="password" id="adminPassword" placeholder="Enter password (default: admin123)">
            </div>
            <button onclick="handleLogin()">Login</button>
            <div id="loginError" class="error-msg"></div>
        </div>

        <!-- DASHBOARD SECTION -->
        <div id="dashboardSection" class="hidden">
            <h2>🚀 API Key Manager</h2>
            
            <div style="background: #0f172a; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #334155;">
                <h3 style="margin-top:0; color:#f8fafc; font-size:16px;">Generate New API Key</h3>
                <div class="form-group">
                    <label>Limit (Max Uses)</label>
                    <input type="number" id="keyLimit" value="5" min="1">
                </div>
                <button onclick="generateKey()">Generate Key</button>
                <div id="genResult" class="success-msg"></div>
            </div>

            <h3 style="color:#f8fafc; font-size:16px;">Existing API Keys Status</h3>
            <div id="keysList">Loading...</div>
            <button onclick="loadKeys()" style="margin-top: 15px; background: #334155;">Refresh Keys</button>
        </div>
    </div>

    <script>
        function handleLogin() {
            const pwd = document.getElementById('adminPassword').value;
            if (pwd === "admin123") {
                document.getElementById('loginSection').classList.add('hidden');
                document.getElementById('dashboardSection').classList.remove('hidden');
                loadKeys();
            } else {
                document.getElementById('loginError').innerText = "Incorrect Password! Try 'admin123'";
            }
        }

        async function loadKeys() {
            try {
                const res = await fetch('/admin/keys');
                const data = await res.json();
                const keysContainer = document.getElementById('keysList');
                keysContainer.innerHTML = '';

                for (const [key, info] of Object.entries(data.keys)) {
                    const isExhausted = info.used >= info.limit;
                    const badge = isExhausted 
                        ? '<span class="badge-exhausted">Limit Exhausted</span>' 
                        : '<span class="badge-active">Active</span>';

                    const card = document.createElement('div');
                    card.className = 'key-card';
                    card.innerHTML = `
                        <div class="key-header">
                            <span>${key}</span>
                            ${badge}
                        </div>
                        <div class="stats-row">
                            <span>Limit: <b>${info.limit}</b></span>
                            <span>Used: <b>${info.used}</b></span>
                            <span>Remaining: <b>${info.limit - info.used}</b></span>
                        </div>
                        <div class="actions-row">
                            <input type="number" id="inc_${key}" value="5" min="1" style="width: 80px; padding: 4px;">
                            <button class="btn-sm" onclick="increaseLimit('${key}')">Increase Limit</button>
                        </div>
                    `;
                    keysContainer.appendChild(card);
                }
            } catch (err) {
                document.getElementById('keysList').innerText = "Failed to load keys.";
            }
        }

        async function generateKey() {
            const limit = parseInt(document.getElementById('keyLimit').value) || 5;
            const res = await fetch('/generate-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ limit })
            });
            const data = await res.json();
            if(res.ok) {
                document.getElementById('genResult').innerText = `New Key: ${data.api_key}`;
                loadKeys();
            }
        }

        async function increaseLimit(apiKey) {
            const extraInput = document.getElementById(`inc_${apiKey}`);
            const extra_limit = parseInt(extraInput.value) || 5;

            const res = await fetch('/admin/increase-limit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey, extra_limit })
            });
            if(res.ok) {
                loadKeys();
            } else {
                alert("Failed to increase limit!");
            }
        }
    </script>

    </body>
    </html>
    """

@app.get("/admin/keys")
async def get_all_keys():
    return {"status": "success", "keys": API_DATABASE}

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

@app.post("/admin/increase-limit")
async def increase_api_limit(data: IncreaseLimitRequest):
    if data.api_key not in API_DATABASE:
        raise HTTPException(status_code=404, detail="API Key not found!")
    API_DATABASE[data.api_key]["limit"] += data.extra_limit
    return {
        "status": "success",
        "new_limit": API_DATABASE[data.api_key]["limit"]
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
            await page.goto("https://chatgpt.com/?action=show_upgrade", timeout=60000)
            await page.wait_for_load_state("domcontentloaded", timeout=60000)
            
            try:
                await page.select_option("select[name='country']", "IN", timeout=10000)
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
                if await upi_option.is_visible(timeout=10000):
                    await upi_option.click()
            except Exception:
                pass

            await page.wait_for_timeout(5000)
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
