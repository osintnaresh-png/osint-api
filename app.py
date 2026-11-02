from flask import Flask, jsonify, request, render_template_string
import requests
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Number API only. Override these with environment variables if needed.
# Use only an API/provider you are authorized to access.
NUMBER_API_BASE = os.getenv(
    "NUMBER_API_BASE",
    "https://api.naxupdate.workers.dev/api/number-info"
)
NUMBER_API_KEY = os.getenv("NUMBER_API_KEY", "1Week")

# Standard Browser Headers to bypass security / Cloudflare blocks
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://api.sarkariallupdates.com/"
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
                <label style="color: #2ea043; margin-bottom: 10px;">⚡ Number API Quick Link</label>
                <a href="/api/lookup?number=8348725603" target="_blank">📱 Test Number API</a>
            </div>
        </div>
    </div>

    <!-- Main Dashboard UI -->
    <div class="main-content">
        <div class="container">
            <img src="https://t4.ftcdn.net/jpg/09/57/39/33/360_F_957393357_C2VcgHKUrwPjpdk0aMQY0DRsX434ySCZ.jpg" alt="Logo">
            <h1>Info Portal</h1>
            <div class="subtitle">System Online Running</div>
            <form action="/api/lookup" method="get" style="margin: 18px 0; text-align: left;">
                <label for="number" style="display:block; margin-bottom:8px; color:#8b949e;">📱 Number API Lookup</label>
                <input id="number" name="number" type="text" inputmode="numeric"
                       pattern="[0-9]{10}" maxlength="10" minlength="10"
                       placeholder="Enter 10-digit mobile number" required
                       style="width:100%; box-sizing:border-box; padding:10px; background:#0d1117; color:#c9d1d9; border:1px solid #30363d; border-radius:5px; margin-bottom:8px;">
                <input type="hidden" name="format" value="json">
                <button type="submit" style="width:100%; padding:10px; background:#238636; color:white; border:0; border-radius:5px; cursor:pointer;">Search Number API</button>
            </form>
            <div class="status-box">
                <p style="margin: 0 0 10px 0; font-size: 12px; color: #8b949e;"><strong>MODULE STATUS:</strong></p>
                <span class="badge active">Number API Configured</span>
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
            
            if(user === "admin" && pass === "nani9090") {
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
def lookup_number():
    number = request.args.get('number', '').strip()

    if not (number.isdigit() and len(number) == 10):
        return jsonify({"error": "Enter a valid 10-digit mobile number."}), 400

    if not NUMBER_API_KEY:
        return jsonify({"error": "Number API key is not configured."}), 503

    try:
        response = requests.get(
            NUMBER_API_BASE,
            params={"key": NUMBER_API_KEY, "number": number},
            headers=COMMON_HEADERS,
            timeout=15
        )
        try:
            data = response.json()
        except ValueError:
            data = {"raw_response": response.text}

        if response.status_code != 200:
            return jsonify({
                "error": "Number API request failed",
                "status_code": response.status_code,
                "details": data
            }), 502

        return jsonify(data)
    except requests.RequestException as exc:
        return jsonify({"error": f"Number API connection failed: {str(exc)}"}), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
