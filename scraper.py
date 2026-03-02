import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

print("---------------------------------")
print("🚀 EREN MONITOR: Iniciando coleta...")
print("---------------------------------")

url = 'https://produto.mercadolivre.com.br/MLB-6217333392-cadeira-gamer-ergonmica-reclinavel-com-apoio-para-os-pes-_JM'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

try:
    print("📡 Acessando o site...")
    response = requests.get(url, headers=headers)
    site = BeautifulSoup(response.text, 'html.parser')

    # SELETOR BLINDADO: Busca a tag de preço pelo formato de dinheiro do ML
    container = site.find('span', class_='andes-money-amount__fraction')
    
    if container:
        preco_raw = container.text.strip().replace('.', '')
        preco_num = float(preco_raw.replace(',', '.'))
        print(f"💰 SUCESSO! Valor: R$ {preco_raw}")

        # Salva no Banco de Dados
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO precos (produto, preco_texto, preco_num, data_coleta) VALUES (?, ?, ?, ?)",
                       ("Cadeira Gamer", f"R$ {preco_raw}", preco_num, datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit()
        conn.close()
        print("✅ Dados gravados com sucesso!")
    else:
        # Se falhar, imprime o HTML para a gente ver o que mudou
        print("❌ ERRO: O seletor de preço falhou. O site mudou o layout.")
        
except Exception as e:
    print(f"❌ ERRO NO CÓDIGO: {e}")