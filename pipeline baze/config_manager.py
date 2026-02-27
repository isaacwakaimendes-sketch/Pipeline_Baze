import json
import os
from datetime import datetime

class ConfigManager:
    def __init__(self, caminho_config):
        self.caminho_config = caminho_config
        self.config = self.carregar_config()
        self.validar_config()
    
    def carregar_config(self):
        try:
            with open(self.caminho_config, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERRO: Arquivo de configuração não encontrado em {self.caminho_config}")
            print("Criando arquivo com configurações padrão...")
            return self.criar_config_padrao()
        except json.JSONDecodeError as e:
            print(f"ERRO: Arquivo de configuração inválido: {e}")
            print("Verifique se o JSON está bem formatado.")
            raise
    
    def validar_config(self):
        required_keys = ['apis', 'caminhos', 'mapa']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Configuração inválida: chave '{key}' não encontrada")
        
        for api_nome, api_config in self.config['apis'].items():
            if 'url' not in api_config:
                raise ValueError(f"Configuração da API '{api_nome}' não tem URL definida")
    
    def salvar_config(self, config_nova=None):
        if config_nova:
            self.config = config_nova
        
        if os.path.exists(self.caminho_config):
            backup_dir = self.config['caminhos']['backup']
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_nome = f"config_backup_{timestamp}.json"
            backup_path = os.path.join(backup_dir, backup_nome)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            print(f"Backup da configuração salvo em: {backup_path}")
        
        with open(self.caminho_config, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        print("Configuração salva com sucesso!")
    
    def criar_config_padrao(self):
        config_padrao = {
            "apis": {},
            "caminhos": {},
            "mapa": {}
        }
        self.salvar_config(config_padrao)
        return config_padrao
    
    def get_api_config(self, api_nome):
        return self.config['apis'].get(api_nome, {})
    
    def get_caminho(self, caminho_nome):
        return self.config['caminhos'].get(caminho_nome, "")
    
    def get_mapa_config(self):
        return self.config.get('mapa', {})