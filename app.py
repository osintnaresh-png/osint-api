from flask import Flask, jsonify, request, render_template_string
import requests

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Base API URLs
IFSC_API_BASE = "https://priyanshuexploits.vercel.app/api/ifsc/"
AADHAAR_API_BASE = "https://api.naxupdate.workers.dev/api/aadhaar-info"
VEHICLE_API_BASE = "https://api.allprinthub.in/api"

# Standard Browser Headers to bypass security / Cloudflare blocks
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://api.allprinthub.in/"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Info Dashboard</title>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: monospace; margin: 0; padding: 0; }
        
        /* Hamburger Three Lines Button */
        .menu-btn { position: fixed; top: 20px; left: 20px; background: #21262d; border: 1px solid #30363d; color: #58a6ff; font-size: 24px; padding: 10px 15px; cursor: pointer; border-radius: 6px; z-index: 1001; transition: 0.2s; }
        .menu-btn:hover { background: #30363d; }
        
        /* Sidebar Drawer */
        .sidebar { height: 100%; width: 320px; position: fixed; z-index: 1000; top: 0; left: -320px; background-color: #161b22; border-right: 1px solid #30363d; overflow-x: hidden; transition: 0.3s; padding-top: 70px; box-shadow: 5px 0 15px rgba(0,0,0,0.5); text-align: left; }
        .sidebar.active { left: 0; }
        .sidebar h2 { color: #58a6ff; font-size: 16px; padding: 0 20px; margin-bottom: 15px; }
        .sidebar .section { padding: 15px 20px; border-bottom: 1px solid #30363d; }
        .sidebar label { font-size: 12px; color: #8b949e; display: block; margin-bottom: 8px; font-weight: bold; }
        .sidebar input[type="text"], .sidebar input[type="password"] { width: 100%; padding: 8px; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; border-radius: 4px; box-sizing: border-box; margin-bottom: 8px; font-family: monospace; }
        .sidebar button { background: #238636; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; width: 100%; font-weight: bold; font-family: monospace; }
        .sidebar button:hover { background: #2ea043; }
        .logout-btn { background: #f85149 !important; }
        .logout-btn:hover { background: #da3633 !important; }
        
        /* Protected Links Section (Hidden by default) */
        .protected-content { display: none; margin-top: 15px; padding-top: 15px; border-top: 1px dashed #30363d; }
        
        .sidebar a { display: block; color: #58a6ff; text-decoration: none; font-size: 11px; margin: 8px 0; word-break: break-all; background: #21262d; padding: 6px; border-radius: 4px; border: 1px solid #30363d; }
        .sidebar a:hover { background: #30363d; text-decoration: underline; }

        /* Main Dashboard */
        .main-content { display: flex; justify-content: center; align-items: center; height: 100vh; text-align: center; }
        .container { max-width: 450px; background: #161b22; padding: 30px; border-radius: 10px; border: 1px solid #30363d; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        img { width: 90px; height: 90px; border-radius: 50%; border: 2px solid #58a6ff; margin-bottom: 20px; object-fit: cover; }
        h1 { color: #58a6ff; margin-bottom: 5px; font-size: 22px; }
        .subtitle { color: #8b949e; margin-bottom: 20px; font-size: 13px; }
        .status-box { margin: 20px 0; padding: 15px; background: #21262d; border-radius: 6px; text-align: left; border: 1px solid #30363d; }
        .badge { display: inline-block; padding: 4px 8px; margin: 4px; border-radius: 4px; font-size: 11px; font-weight: bold; }
        .active { background: #238636; color: white; }
        .footer { margin-top: 25px; font-size: 12px; color: #8b949e; border-top: 1px solid #30363d; padding-top: 15px; }
    </style>
</head>
<body>

    <!-- Three Lines Menu Button -->
    <div class="menu-btn" onclick="toggleSidebar()">☰</div>

    <!-- Sidebar Drawer Menu -->
    <div id="sidebar" class="sidebar">
        <h2>📊 Dashboard Control</h2>
        
        <!-- Login / Logout Option Section -->
        <div class="section">
            <label>🔐 Authentication</label>
            
            <!-- Login Form -->
            <div id="loginForm">
                <input type="text" id="username" placeholder="Username">
                <input type="password" id="password" placeholder="Password">
                <button onclick="handleLogin()">Login</button>
            </div>

            <!-- Logout Form (Hidden initially) -->
            <div id="logoutForm" style="display: none;">
                <p style="color: #2ea043; font-size: 12px; margin-bottom: 10px; font-weight: bold;">🟢 Status: Logged In</p>
                <button class="logout-btn" onclick="handleLogout()">Logout</button>
            </div>

            <!-- Protected Quick Lookup Links Section -->
            <div id="protectedLinks" class="protected-content">
                <label style="color: #2ea043; margin-bottom: 10px;">⚡ Quick Links (&format=text)</label>
                <a href="/api/lookup?ifsc=SBIN0000794&aadhaar=123412341234&vehicle=KL41V3504&format=text" target="_blank">🔗 Full Lookup</a>
                <a href="/api/lookup?ifsc=SBIN0000794&format=text" target="_blank">🏦 IFSC: SBIN0000794</a>
                <a href="/api/lookup?aadhaar=123412341234&format=text" target="_blank">🪪 ID Lookup</a>
                <a href="/api/lookup?vehicle=KL41V3504&format=text" target="_blank">🚗 Vehicle: KL41V3504</a>
            </div>
        </div>
    </div>

    <!-- Main Dashboard UI -->
    <div class="main-content">
        <div class="container">
            <img src="https://t4.ftcdn.net/jpg/09/57/39/33/360_F_957393357_C2VcgHKUrwPjpdk0aMQY0DRsX434ySCZ.jpg" alt="Logo">
            <h1>Info Portal</h1>
            <div class="subtitle">System Online Running</div>
            <div class="status-box">
                <p style="margin: 0 0 10px 0; font-size: 12px; color: #8b949e;"><strong>MODULE STATUS:</strong></p>
                <span class="badge active">IFSC Active</span>
                <span class="badge active">ID Active</span>
                <span class="badge active">Vehicle Active</span>
            </div>
            <div class="footer">
                <p>Developer: <strong>Admin</strong></p>
            </div>
        </div>
    </div>

    <script>
        function toggleSidebar() {
            document.getElementById("sidebar").classList.toggle("active");
        }

        function handleLogin() {
            const user = document.getElementById("username").value;
            const pass = document.getElementById("password").value;
            
            if(user === "admin" && pass === "nani1234") {
                localStorage.setItem("wolf_logged_in", "true");
                showLoggedInState();
                alert("Login Successful! Links Unlocked.");
            } else {
                alert("Invalid Username or Password!");
            }
        }

        function handleLogout() {
            localStorage.removeItem("wolf_logged_in");
            document.getElementById("username").value = "";
            document.getElementById("password").value = "";
            showLoggedOutState();
            alert("Logged out successfully! Links Locked.");
        }

        function showLoggedInState() {
            document.getElementById("loginForm").style.display = "none";
            document.getElementById("logoutForm").style.display = "block";
            document.getElementById("protectedLinks").style.display = "block";
        }

        function showLoggedOutState() {
            document.getElementById("loginForm").style.display = "block";
            document.getElementById("logoutForm").style.display = "none";
            document.getElementById("protectedLinks").style.display = "none";
        }

        window.onload = function() {
            if(localStorage.getItem("wolf_logged_in") === "true") {
                document.getElementById("username").value = "admin";
                document.getElementById("password").value = "wolf1234";
                showLoggedInState();
            } else {
                showLoggedOutState();
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/lookup', methods=['GET'])
def lookup_all():
    ifsc_code = request.args.get('ifsc')
    aadhaar_num = request.args.get('aadhaar')
    vehicle_num = request.args.get('vehicle')
    out_format = request.args.get('format', 'json')

    results = {}

    # 1. IFSC API Call
    if ifsc_code:
        try:
            url = f"{IFSC_API_BASE}{ifsc_code}?format=text"
            res = requests.get(url, headers=COMMON_HEADERS, timeout=10)
            results['ifsc'] = res.text if res.status_code == 200 else f"Failed (Status: {res.status_code})"
        except Exception as e:
            results['ifsc'] = f"Error: {str(e)}"

    # 2. Aadhaar API Call
    if aadhaar_num:
        try:
            params = {"key": "1Week", "aadhaar": aadhaar_num}
            res = requests.get(AADHAAR_API_BASE, params=params, headers=COMMON_HEADERS, timeout=15)
            if res.status_code == 200:
                try:
                    data = res.json()
                except Exception:
                    data = res.text
            else:
                data = f"Security/Block Error (Status Code: {res.status_code})"
            results['aadhaar'] = data
        except Exception as e:
            results['aadhaar'] = f"Error: {str(e)}"

    # 3. Vehicle API Call (Updated with new AllPrintHub API)
    if vehicle_num:
        try:
            params = {"": "challan", "key": "Ronak_api", "v": vehicle_num}
            res = requests.get(VEHICLE_API_BASE, params=params, headers=COMMON_HEADERS, timeout=15)
            if res.status_code == 200:
                try:
                    data = res.json()
                except Exception:
                    data = res.text
            else:
                data = f"Failed (Status: {res.status_code})"
            results['vehicle'] = data
        except Exception as e:
            results['vehicle'] = f"Error: {str(e)}"

    # Format=text support
    if out_format == 'text':
        formatted_text = "========================================\n"
        formatted_text += "          SYSTEM REPORT                 \n"
        formatted_text += "========================================\n\n"

        if ifsc_code and 'ifsc' in results:
            formatted_text += str(results['ifsc']) + "\n\n"

        if vehicle_num and 'vehicle' in results:
            formatted_text += "--- 🚗 VEHICLE CHALLAN REPORT ---\n"
            v_data = results['vehicle']
            if isinstance(v_data, dict):
                for k, v in v_data.items():
                    formatted_text += f"{k} : {v}\n"
            else:
                formatted_text += str(v_data) + "\n"
            formatted_text += "\n"

        if aadhaar_num and 'aadhaar' in results:
            formatted_text += "--- 🪪 ID INTELLIGENCE REPORT ---\n"
            a_data = results['aadhaar']
            formatted_text += str(a_data) + "\n"

        return app.response_class(formatted_text, mimetype='text/plain')

    return jsonify(results)
