import requests
import pandas as pd
import json
from datetime import datetime
import os

def carregar_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def buscar_api(url):
    try:
        return requests.get(url, timeout=30).json()
    except:
        return []

def limpar_id(texto):
    if not texto or not isinstance(texto, str):
        return 'N/A'
    return texto.split(':')[-1]

def formatar_data(data_str):
    if not data_str:
        return 'N/A'
    try:
        if 'T' in data_str:
            dt = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
            return dt.strftime('%d/%m/%Y %H:%M')
    except:
        pass
    return data_str

def processar_airquality(dados):
    registros = []
    for item in dados:
        registro = {
            'ID': limpar_id(item.get('_entityId')),
            'Local': item.get('streetAddress', 'N/A'),
            'Concelho': item.get('areaServed', 'N/A'),
            'Data/Hora': formatar_data(item.get('dateObserved')),
            'Latitude': item.get('location_coordinates_lat', 0),
            'Longitude': item.get('location_coordinates_lon', 0),
            'Temperatura': item.get('temperature', 'N/A'),
            'Humidade': item.get('relativeHumidity', 'N/A'),
            'Nível Qualidade': item.get('airQualityLevel', 'N/A'),
            'Índice Qualidade': item.get('airQualityIndex', 'N/A'),
            'CO': item.get('co', 'N/A'),
            'NO': item.get('no', 'N/A'),
            'NO2': item.get('no2', 'N/A'),
            'SO2': item.get('so2', 'N/A'),
            'Velocidade Vento': item.get('windSpeed', 'N/A'),
            'Precipitação': item.get('precipitation', 'N/A')
        }
        registros.append(registro)
    return registros

def processar_madrid_poi(dados):
    registros = []
    for item in dados:
        registro = {
            'ID': limpar_id(item.get('_entityId')),
            'Nome': item.get('name', item.get('title', 'N/A')),
            'Latitude': item.get('location_coordinates_lat', 0),
            'Longitude': item.get('location_coordinates_lon', 0),
            'Capacidade': item.get('capacity', 'N/A'),
            'Ocupação': item.get('occupancy', 'N/A')
        }
        registros.append(registro)
    return registros

def processar_porto_poi(dados):
    registros = []
    for item in dados:
        registro = {
            'ID': limpar_id(item.get('_entityId')),
            'Nome': item.get('name', item.get('title', 'N/A')),
            'Categoria': item.get('category', 'N/A'),
            'Latitude': item.get('location_coordinates_lat', 0),
            'Longitude': item.get('location_coordinates_lon', 0),
            'Capacidade': item.get('capacity', 'N/A'),
            'Ocupação': item.get('occupancy', 'N/A')
        }
        registros.append(registro)
    return registros

def processar_portodigital_poi(dados):
    registros = []
    for item in dados:
        registro = {
            'ID': limpar_id(item.get('_entityId')),
            'Nome': item.get('name_pt', item.get('name', 'N/A')),
            'Endereço': item.get('address_streetAddress', 'N/A'),
            'Cidade': item.get('address_addressLocality', 'N/A'),
            'Latitude': item.get('location_coordinates_lat', 0),
            'Longitude': item.get('location_coordinates_lon', 0)
        }
        registros.append(registro)
    return registros

def processar_veiculos(dados):
    registros = []
    for item in dados:
        tipo = item.get('vehicleType', 'N/A')
        if tipo == 'twoWheeledVehicle':
            tipo = 'Motociclo'
            
        registro = {
            'ID': limpar_id(item.get('_entityId')),
            'Latitude': item.get('location_coordinates_lat', 0),
            'Longitude': item.get('location_coordinates_lon', 0),
            'Tipo Veículo': tipo,
            'Operador': item.get('description', 'N/A'),
            'Status': item.get('serviceStatus', 'N/A')
        }
        registros.append(registro)
    return registros

def salvar_excel(todos_dados, config):
    nome_arquivo = config['caminhos']['excel']
    
    with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
        for chave, dados in todos_dados.items():
            if dados:
                nome_aba = config['excel']['sheet_names'].get(chave, chave)
                df = pd.DataFrame(dados)
                df = df.fillna('N/A')
                df.to_excel(writer, sheet_name=nome_aba, index=False)
                print(f"{nome_aba}: {len(df)} registos")
    
    print(f"Excel guardado: {nome_arquivo}")

def run():
    config = carregar_config()
    
    urls = {
        'airquality_observed': 'https://api.iotbi.tech/api/v1/stellio_owm_ld/AirQualityObserved?appKey=estagio',
        'madrid_poi': 'https://api.iotbi.tech/api/v1/madrid/PointOfInterest?appKey=estagio',
        'porto_poi': 'https://api.iotbi.tech/api/v1/porto/PointOfInterest?appKey=estagio',
        'portodigital_poi': 'https://api.iotbi.tech/api/v1/portodigital/PointOfInterest?appKey=estagio',
        'portodigital_vehicle': 'https://api.iotbi.tech/api/v1/portodigital/Vehicle?appKey=estagio'
    }
    
    dados = {
        'airquality_observed': processar_airquality(buscar_api(urls['airquality_observed'])),
        'madrid_poi': processar_madrid_poi(buscar_api(urls['madrid_poi'])),
        'porto_poi': processar_porto_poi(buscar_api(urls['porto_poi'])),
        'portodigital_poi': processar_portodigital_poi(buscar_api(urls['portodigital_poi'])),
        'portodigital_vehicle': processar_veiculos(buscar_api(urls['portodigital_vehicle']))
    }
    
    salvar_excel(dados, config)
    print("Pipeline executado com sucesso!")

if __name__ == "__main__":
    run()