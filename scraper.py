import requests
import json
import re
from datetime import datetime

LISTING_ID = "1503584633402633674"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

def extrair_dados_json(html):
    """Extrai o JSON com os dados da página (preços, disponibilidade)."""
    padrao = r'window\.__PRELOADED_STATE__\s*=\s*({.*?});'
    match = re.search(padrao, html, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None

def consultar_airbnb(checkin, checkout, adultos, criancas=0, bebes=0, pets=0):
    """
    Consulta o Airbnb em tempo real extraindo dados dos scripts JSON.
    Retorna um dicionário com os resultados dos 3 quartos.
    """
    guests = adultos + criancas
    url = f"https://www.airbnb.com.br/rooms/{LISTING_ID}?guests={guests}&adults={adultos}&children={criancas}&infants={bebes}&check_in={checkin}&check_out={checkout}"

    print(f"🌐 Consultando: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return {}

    dados = extrair_dados_json(html)
    if not dados:
        print("❌ Não foi possível extrair os dados JSON da página.")
        return {}

    room_ids = ["1503584633402633674", "1535677362018464574", "1507145359441207299"]
    resultados = {}

    # Para cada quarto, faz uma requisição individual para pegar preço e disponibilidade
    for room_id in room_ids:
        url_room = f"https://www.airbnb.com.br/rooms/{LISTING_ID}/room-details?guests={guests}&adults={adultos}&children={criancas}&infants={bebes}&check_in={checkin}&check_out={checkout}&room_id={room_id}&room_origin=room_section&s=67"
        try:
            resp = requests.get(url_room, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            html_room = resp.text
            dados_room = extrair_dados_json(html_room)
            if not dados_room:
                resultados[room_id] = {"available": False, "price": None}
                continue

            pricing = dados_room.get('pdpListingDetail', {}).get('pricingQuote', {})
            price_total = pricing.get('total', {}).get('amount')
            is_available = pricing.get('available', True)

            if price_total:
                resultados[room_id] = {
                    "available": is_available,
                    "price": float(price_total)
                }
            else:
                resultados[room_id] = {"available": False, "price": None}

        except Exception as e:
            print(f"❌ Erro ao consultar quarto {room_id}: {e}")
            resultados[room_id] = {"available": False, "price": None}

    return resultados