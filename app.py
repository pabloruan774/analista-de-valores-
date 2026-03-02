from flask import Flask, render_template, request, jsonify
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

def buscar_dados():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        # Busca últimos 10 para a tabela e todos para o gráfico
        cursor.execute("SELECT produto, preco_texto, imagem, link, data_coleta FROM precos ORDER BY id DESC LIMIT 10")
        tabela = cursor.fetchall()
        cursor.execute("SELECT preco_num, data_coleta FROM precos ORDER BY id ASC")
        dados_grafico = cursor.fetchall()
    return tabela, [d[0] for d in dados_grafico], [d[1] for d in dados_grafico]

def buscar_stats():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(preco_num), MIN(preco_num), COUNT(*) FROM precos")
        media, minimo, total = cursor.fetchone()
    return {"media": round(media, 2) if media else 0, "minimo": minimo if minimo else 0, "total": total}

@app.route('/')
def index():
    tabela, precos, datas = buscar_dados()
    stats = buscar_stats()
    return render_template('index.html', historico=tabela, eixos_y=precos, eixos_x=datas, stats=stats)

@app.route('/add_link', methods=['POST'])
def add_link():
    url_usuario = request.json.get('url')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url_usuario, headers=headers)
        site = BeautifulSoup(response.text, 'html.parser')
        # Seletor Blindado: Tenta meta tag primeiro (mais estável)
        preco_meta = site.find('meta', itemprop='price')
        if preco_meta:
            preco_num = float(preco_meta['content'])
        else:
            preco_raw = site.find('span', class_='andes-money-amount__fraction').text.replace('.', '').replace(',', '.')
            preco_num = float(preco_raw)

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO precos (produto, preco_texto, preco_num, data_coleta) VALUES (?, ?, ?, ?)",
                           ("Produto Novo", f"R$ {preco_num}", preco_num, datetime.now().strftime("%d/%m %H:%M")))
            conn.commit()
        return jsonify({"status": "success", "message": f"Capturado: R$ {preco_num}"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Falha na captura. Verifique o link."}), 400

@app.route('/reset', methods=['POST'])
def reset_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute("DELETE FROM precos")
    return jsonify({"status": "success", "message": "Histórico limpo!"})

if __name__ == '__main__':
    app.run(debug=True)