from flask import Flask, jsonify, request, render_template_string
import requests

app = Flask(__name__)

# Emojis & Box characters escape avvakunda direct ga print avvataniki
app.config['JSON_AS_ASCII'] = False

# Base API URLs
IFSC_API_BASE = "https://priyanshuexploits.vercel.app/api/ifsc/"
AADHAAR_API_BASE = "https://aadhar-xi.vercel.app/api/lookup"
VEHICLE_API_BASE = "https://api.sarkariallupdates.com/api"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wolf OSINT</title>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: monospace; text-align: center; padding: 40px; }
        .container { max-width: 600px; margin: auto; background: #161b22; padding: 30px; border-radius: 10px; border: 1px solid #30363d; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        img { width: 100px; height: 100px; border-radius: 50%; border: 2px solid #58a6ff; margin-bottom: 20px; object-fit: cover; }
        h1 { color: #58a6ff; margin-bottom: 5px; }
        .subtitle { color: #8b949e; margin-bottom: 20px; font-size: 14px; }
        .status-box { margin: 20px 0; padding: 15px; background: #21262d; border-radius: 6px; text-align: left; border: 1px solid #30363d; }
        .badge { display: inline-block; padding: 5px 10px; margin: 5px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .active { background: #238636; color: white; }
        .footer { margin-top: 25px; font-size: 13px; color: #8b949e; border-top: 1px solid #30363d; padding-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <img src="https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=200&h=200&fit=crop" alt="Wolf Logo">
        <h1>Wolf OSINT</h1>
        <div class="subtitle">System Online Running</div>
        <div class="status-box">
            <p><strong>Module Status:</strong></p>
            <span class="badge active">IFSC Active</span>
            <span class="badge active">Aadhaar Active</span>
            <span class="badge active">Vehicle Active</span>
        </div>
        <div class="footer">
            <p>Developer: <strong>Wolf OSINT</strong></p>
        </div>
    </div>
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
            res = requests.get(url, timeout=10)
            results['ifsc'] = res.text if res.status_code == 200 else "Failed"
        except Exception as e:
            results['ifsc'] = f"Error: {str(e)}"

    # 2. Aadhaar API Call
    if aadhaar_num:
        try:
            params = {"id": aadhaar_num, "format": "card"}
            res = requests.get(AADHAAR_API_BASE, params=params, timeout=15)
            try:
                data = res.json()
            except Exception:
                data = res.text
            results['aadhaar'] = data
        except Exception as e:
            results['aadhaar'] = f"Error: {str(e)}"

    # 3. Vehicle API Call
    if vehicle_num:
        try:
            params = {"": "ultra_vehicle", "key": "demo", "xr": vehicle_num}
            res = requests.get(VEHICLE_API_BASE, params=params, timeout=15)
            try:
                data = res.json()
            except Exception:
                data = res.text
            results['vehicle'] = data
        except Exception as e:
            results['vehicle'] = f"Error: {str(e)}"

    # Format=text isthe actual line breaks tho clean report vasthundi
    if out_format == 'text':
        formatted_text = "========================================\n"
        formatted_text += "          WOLF OSINT REPORT             \n"
        formatted_text += "========================================\n\n"

        if ifsc_code and 'ifsc' in results:
            formatted_text += str(results['ifsc']) + "\n\n"

        if vehicle_num and 'vehicle' in results:
            formatted_text += "--- 🚗 VEHICLE RC INTELLIGENCE REPORT ---\n"
            v_data = results['vehicle']
            if isinstance(v_data, dict):
                for k, v in v_data.items():
                    formatted_text += f"{k} : {v}\n"
            else:
                formatted_text += str(v_data) + "\n"
            formatted_text += "\n"

        if aadhaar_num and 'aadhaar' in results:
            formatted_text += "--- 🪪 AADHAAR INTELLIGENCE REPORT ---\n"
            a_data = results['aadhaar']
            formatted_text += str(a_data) + "\n"

        return app.response_class(formatted_text, mimetype='text/plain')

    return jsonify(results)
