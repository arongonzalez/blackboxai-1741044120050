from flask import render_template, jsonify
from flask_login import login_required
import requests
from bs4 import BeautifulSoup
import re
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_bcv_rate():
    try:
        url = 'https://www.bcv.org.ve/'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            dollar_div = soup.find('div', {'id': 'dolar'})
            if dollar_div:
                rate_text = dollar_div.get_text(strip=True)
                rate_match = re.search(r'(\d+[,\.]\d+)', rate_text)
                if rate_match:
                    return float(rate_match.group(1).replace(',', '.'))
    except Exception as e:
        print(f"Error fetching BCV rate: {e}")
    return 35.00

def init_pos_routes(app):
    @app.route('/pos')
    @login_required
    def pos():
        return render_template('pos.html', exchange_rate=get_bcv_rate())

    @app.route('/get_exchange_rate')
    def get_exchange_rate():
        return jsonify({'rate': get_bcv_rate()})

    return app
