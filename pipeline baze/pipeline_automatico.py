import subprocess
import sys
import os
import time
from datetime import datetime

BASE_DIR = r"C:\pipeline baze"
SCRIPT = "pipeline_baze.py"
LOG_FILE = os.path.join(BASE_DIR, "pipeline_log.txt")

def run_pipeline():
    python_exe = sys.executable
    script_path = os.path.join(BASE_DIR, SCRIPT)

    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"--- Início da execução: {datetime.now()} ---\n")
        log.write(f"Rodando {SCRIPT}...\n")

        resultado = subprocess.run(
            [python_exe, script_path],
            capture_output=True,
            text=True
        )
        
        if resultado.returncode == 0:
            log.write("Pipeline executado com sucesso!\n")
            log.write(f"{SCRIPT} finalizado com sucesso.\n")
        else:
            log.write(f"ERRO ao rodar {SCRIPT}!\n")

        log.write(f"--- Fim da execução: {datetime.now()} ---\n\n")

if __name__ == "__main__":
    while True:
        run_pipeline()
        time.sleep(900)