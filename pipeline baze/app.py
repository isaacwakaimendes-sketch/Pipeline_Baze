from flask import Flask, jsonify, render_template
import pandas as pd
import json
from datetime import datetime
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "Dados_Baze.xlsx")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def carregar_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def traduzir_valores(chave, valor):
    """Traduz valores específicos para português"""
    traducoes = {
        'Tipo Veículo': {
            'car': 'Automóvel',
            'bus': 'Autocarro',
            'truck': 'Camião',
            'bicycle': 'Bicicleta',
            'motorcycle': 'Motociclo',
            'twoWheeledVehicle': 'Motociclo'
        },
        'Nível Qualidade': {
            'good': 'Bom',
            'moderate': 'Moderado',
            'poor': 'Fraco',
            'unhealthy': 'Insalubre',
            'very unhealthy': 'Muito Insalubre',
            'hazardous': 'Perigoso'
        },
        'Status': {
            'parked': 'Estacionado',
            'moving': 'Em movimento',
            'stopped': 'Parado',
            'available': 'Disponível'
        },
        'Tipo Local': {
            'outdoor': 'Exterior',
            'indoor': 'Interior'
        }
    }
    
    if chave in traducoes and valor in traducoes[chave]:
        return traducoes[chave][valor]
    return valor

def ler_excel():
    config = carregar_config()
    dados_api = {}
    stats = {}
    
    if not os.path.exists(EXCEL_FILE):
        return {"apis": {}, "stats": {"ultima_atualizacao": "N/A"}, "config": config}
    
    try:
        excel = pd.ExcelFile(EXCEL_FILE)
        sheet_para_api = {v: k for k, v in config['excel']['sheet_names'].items()}
        
        for sheet in excel.sheet_names:
            api_key = sheet_para_api.get(sheet)
            if not api_key:
                continue
            
            df = pd.read_excel(excel, sheet)
            api_config = config['apis'].get(api_key, {})
            registros = []
            
            for _, row in df.iterrows():
                dados = row.to_dict()
                
                lat = float(dados.get('Latitude', 0)) if pd.notna(dados.get('Latitude')) else 0
                lon = float(dados.get('Longitude', 0)) if pd.notna(dados.get('Longitude')) else 0
                
                local = dados.get('Nome') or 'Local'
                if pd.isna(local):
                    local = 'Local'
                
                data = dados.get('Data/Hora', 'N/A')
                if pd.isna(data):
                    data = 'N/A'
                
                info = {}
                for k, v in dados.items():
                    if k not in ['Latitude', 'Longitude', 'Nome', 'Data/Hora']:
                        if pd.notna(v) and v != 'N/A':
                            info[k] = traduzir_valores(k, v)
                
                registros.append({
                    'lat': lat,
                    'lon': lon,
                    'local': str(local),
                    'data_hora': str(data),
                    'cor': api_config.get('cor', '#3498db'),
                    'dados': info
                })
            
            if registros:
                dados_api[api_key] = registros
                stats[api_key] = len(registros)
    
    except Exception as e:
        print(f"Erro: {e}")
    
    if os.path.exists(EXCEL_FILE):
        stats['ultima_atualizacao'] = datetime.fromtimestamp(os.path.getmtime(EXCEL_FILE)).strftime('%d/%m/%Y %H:%M')
    
    return {"apis": dados_api, "stats": stats, "config": config}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mapa')
def mapa():
    return render_template('mapa.html')

@app.route('/api/dados')
def api_dados():
    return jsonify(ler_excel())

if __name__ == '__main__':
    print("Servidor: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)