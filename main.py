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

# Professional Dashboard & Login UI with Show/Hide Password & Copy Key Option
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ChatGPT Automation Pro Panel</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #090d16;
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
                max-width: 650px;
                background: #111827;
                padding: 30px;
                border-radius: 16px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
                border: 1px solid #1f2937;
            }
            h2 {
                color: #38bdf8;
                text-align: center;
                margin-bottom: 25px;
                font-weight: 600;
            }
            .hidden { display: none !important; }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                font-size: 13px;
                margin-bottom: 6px;
                color: #9ca3af;
                font-weight: 500;
            }
            .password-wrapper {
                position: relative;
            }
            input {
                width: 100%;
                padding: 12px;
                background: #030712;
                border: 1px solid #374151;
                color: white;
                border-radius: 8px;
                box-sizing: border-box;
                font-size: 14px;
            }
            input:focus {
                border-color: #38bdf8;
                outline: none;
            }
            .toggle-eye {
                position: absolute;
                right: 12px;
                top: 50%;
                transform: translateY(-50%);
                cursor: pointer;
                color: #9ca3af;
                font-size: 16px;
                user-select: none;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #0284c7;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.2s;
                font-size: 14px;
            }
            button:hover { background: #0369a1; }
            .key-card {
                background: #030712;
                border: 1px solid #1f2937;
                padding: 16px;
                border-radius: 10px;
                margin-bottom: 12px;
            }
            .key-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-family: monospace;
                color: #38bdf8;
                font-size: 13px;
                word-break: break-all;
                background: #111827;
                padding: 8px 12px;
                border-radius: 6px;
                border: 1px solid #1f2937;
            }
            .badge-active { color: #4ade80; background: rgba(74, 222, 128, 0.1); padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
            .badge-exhausted { color: #f87171; background: rgba(248, 113, 113, 0.1); padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
            .stats-row {
                display: flex;
                justify-content: space-between;
                font-size: 13px;
                color: #9ca3af;
                margin-top: 12px;
            }
            .actions-row {
                display: flex;
                gap: 10px;
                margin-top: 12px;
                align-items: center;
            }
            .btn-sm {
                padding: 7px 14px;
                font-size: 12px;
                width: auto;
                background: #374151;
            }
            .btn-sm:hover { background: #4b5563; }
            .btn-copy { background: #047857; }
            .btn-copy:hover { background: #065f46; }
            .error-msg { color: #f87171; text-align: center; font-size: 13px; margin-top: 10px; }
            .success-box {
                background: rgba(14, 165, 233, 0.1);
                border: 1px solid #0284c7;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 15px;
                font-size: 13px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
        </style>
    </head>
    <body>

    <div class="container">
        <!-- LOGIN SECTION -->
        <div id="loginSection">
            <h2>🔐 Admin Login</h2>
            <div class="form-group">
                <label>Admin Password</label>
                <div class="password-wrapper">
                    <input type="password" id="adminPassword" placeholder="Enter password (default: admin123)">
                    <span class="toggle-eye" onclick="togglePasswordVisibility()">👁️</span>
                </div>
            </div>
            <button onclick="handleLogin()">Login to Dashboard</button>
            <div id="loginError" class="error-msg"></div>
        </div>

        <!-- DASHBOARD SECTION -->
        <div id="dashboardSection" class="hidden">
            <h2>🚀 API Key Manager Pro</h2>
            
            <div style="background: #030712; padding: 20px; border-radius: 10px; margin-bottom: 25px; border: 1px solid #1f2937;">
                <h3 style="margin-top:0; color:#f8fafc; font-size:15px; margin-bottom: 12px;">Generate New API Key</h3>
                <div class="form-group">
                    <label>Limit (Max Automation Uses)</label>
                    <input type="number" id="keyLimit" value="5" min="1">
                </div>
                <button onclick="generateKey()">Generate Key</button>
                <div id="genResultContainer" style="margin-top: 15px;"></div>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="color:#f8fafc; font-size:15px; margin:0;">Active & Exhausted Keys</h3>
                <button class="btn-sm" onclick="loadKeys()" style="background: #1f2937;">🔄 Refresh</button>
            </div>
            
            <div id="keysList">Loading keys...</div>
        </div>
    </div>

    <script>
        function togglePasswordVisibility() {
            const pwdInput = document.getElementById('adminPassword');
            if (pwdInput.type === 'password') {
                pwdInput.type = 'text';
            } else {
                pwdInput.type = 'password';
            }
        }

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
                        ? '<span class="badge-exhausted">Exhausted</span>' 
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
                            <span>Remaining: <b style="color: ${info.limit - info.used > 0 ? '#38bdf8' : '#f87171'}">${info.limit - info.used}</b></span>
                        </div>
                        <div class="actions-row">
                            <button class="btn-sm btn-copy" onclick="copyToClipboard('${key}')">📋 Copy Key</button>
                            <input type="number" id="inc_${key}" value="5" min="1" style="width: 70px; padding: 6px; text-align: center;">
                            <button class="btn-sm" onclick="increaseLimit('${key}')">➕ Add Limit</button>
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
                const resultDiv = document.getElementById('genResultContainer');
                resultDiv.innerHTML = `
                    <div class="success-box">
                        <span style="font-family:monospace; word-break:break-all; margin-right:10px;"><b>New Key:</b> ${data.api_key}</span>
                        <button class="btn-sm btn-copy" style="width:auto; white-space:nowrap;" onclick="copyToClipboard('${data.api_key}')">📋 Copy</button>
                    </div>
                `;
                loadKeys();
            }
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert("API Key copied successfully!");
            }).catch(err => {
                alert("Failed to copy text.");
            });
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
