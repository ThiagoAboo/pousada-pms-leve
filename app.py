from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import os
from scraper import consultar_airbnb, LISTING_ID

app = Flask(__name__)

# Definição dos quartos (apenas para descrições e capacidade)
ROOMS = {
    "1503584633402633674": {
        "name": "Suíte Costa Azul",
        "description": "tem uma varanda excepcional com vista mar, somada com uma rede para relaxar em uma vista maravilhosa do mar, que dá para ser apreciado deitado na cama. O quarto conta com frigobar, cafeteira, e ar-condicionado. Este quarto possui uma cama de casal. (Não tem piscina e nem tv). possibilitando 2 pessoas.",
        "max_guests": 2
    },
    "1535677362018464574": {
        "name": "Suíte Praia da Tartaruga",
        "description": "preparada para descansar, tendo um ambiente mais silencioso. Conta com uma cama de casal, e uma beliche com duas camas de solteiro, ventilador, cafeteira, tv e frigobar. (Não tem piscina, nem ar-condicionado). possibilitando 4 pessoas.",
        "max_guests": 4
    },
    "1507145359441207299": {
        "name": "Suíte Praia da Baleia",
        "description": "dispõe de varanda com vista mar, piscina de borda infinita, churrasqueira, frigobar, cafeteira, ventilador, tv, mesa externa, e tudo isso privativo no quarto, somente vocês irão utilizar. Este quarto conta com 1 cama de casal e duas camas de solteiro. (Não tem ar-condicionado). possibilitando 4 pessoas.",
        "max_guests": 4
    }
}

def validar_minimo_noites(checkin_date, noites):
    dia_semana = checkin_date.weekday()
    if dia_semana in [4, 5] and noites < 2:
        return False, "Reservas com check-in na sexta ou sábado exigem mínimo de 2 diárias."
    return True, ""

@app.route('/')
def index():
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    return render_template('index.html',
                           today=today.strftime('%Y-%m-%d'),
                           tomorrow=tomorrow.strftime('%Y-%m-%d'))

@app.route('/consultar', methods=['POST'])
def consultar():
    try:
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        adultos = int(request.form['adultos'])
        criancas = int(request.form.get('criancas', 0))
        bebes = int(request.form.get('bebes', 0))
        pets = int(request.form.get('pets', 0))
        desconto = float(request.form.get('desconto', 12)) / 100

        checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
        noites = (checkout_date - checkin_date).days

        if checkout_date <= checkin_date:
            return jsonify({'error': 'Check-out deve ser após check-in'}), 400
        if noites > 30:
            return jsonify({'error': 'Máximo 30 noites'}), 400

        valido, msg = validar_minimo_noites(checkin_date, noites)
        if not valido:
            return jsonify({'error': msg}), 400

        # Consultar Airbnb em tempo real
        resultados = consultar_airbnb(checkin, checkout, adultos, criancas, bebes, pets)

        all_suites = []
        prices_with_discount = {}

        for room_id, room_info in ROOMS.items():
            data = resultados.get(room_id, {})
            preco = data.get('price')
            disponivel = data.get('available', False)

            # Verificar capacidade
            total_hospedes = adultos + criancas
            capacidade_excedida = total_hospedes > room_info['max_guests']

            if disponivel and preco:
                preco_com_desconto = preco * (1 - desconto)
                prices_with_discount[room_id] = preco_com_desconto
            else:
                preco_com_desconto = 0

            all_suites.append({
                'id': room_id,
                'name': room_info['name'],
                'description': room_info['description'],
                'price': preco if preco else 0,
                'price_with_discount': preco_com_desconto,
                'available': disponivel and preco is not None,
                'url': f"https://www.airbnb.com.br/rooms/{LISTING_ID}/room-details?guests={adultos+criancas}&adults={adultos}&children={criancas}&infants={bebes}&check_in={checkin}&check_out={checkout}&room_id={room_id}&room_origin=room_section&s=67",
                'capacidade_excedida': capacidade_excedida
            })

        # Gerar mensagem WhatsApp (igual à anterior, só ajustar)
        mensagem = gerar_mensagem_whatsapp(
            checkin, checkout, adultos, criancas, bebes, pets, noites,
            all_suites, desconto * 100
        )

        return jsonify({
            'success': True,
            'all_suites': all_suites,
            'whatsapp_message': mensagem
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def gerar_mensagem_whatsapp(checkin, checkout, adultos, criancas, bebes, pets, noites, all_suites, desconto_percent):
    checkin_fmt = datetime.strptime(checkin, '%Y-%m-%d').strftime('%d/%m/%Y')
    checkout_fmt = datetime.strptime(checkout, '%Y-%m-%d').strftime('%d/%m/%Y')
    checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
    is_weekend = checkin_date.weekday() in [4, 5]

    mensagem = f"""🏨 *POUSADA DOS SONHOS COSTA AZUL*
🌊 *Consulta de Disponibilidade*

📅 *PERÍODO:*
• Check-in: {checkin_fmt} (14h)
• Check-out: {checkout_fmt} (11h)
• Total de noites: {noites} noites
{ '⚠️ *Mínimo de 2 noites para fins de semana aplicado*' if is_weekend else '' }

👥 *HÓSPEDES:*
• Adultos: {adultos}
• Crianças: {criancas}
• Bebês: {bebes}
• Pets: {pets}

━━━━━━━━━━━━━━━━━━━━━
"""

    quartos_disponiveis = 0
    for suite in all_suites:
        if suite['available']:
            quartos_disponiveis += 1
            mensagem += f"""

*{suite['name']}*
{suite['description']}

💰 *PREÇOS:*
• Original: R$ {suite['price']:,.2f}
• Com {desconto_percent:.0f}% desconto: R$ {suite['price_with_discount']:,.2f}

🔗 Link: {suite['url']}

━━━━━━━━━━━━━━━━━━━━━"""

    if quartos_disponiveis == 0:
        mensagem += "\n\n❌ *Nenhum quarto disponível para as datas selecionadas*\n"

    mensagem += """

💳 *CONDIÇÕES DE PAGAMENTO:*
• Opção 1: 50% no ato da reserva + 50% no check-in
• Opção 2: 100% à vista com {}% de desconto

📱 *PIX PARA PAGAMENTO:*
pousadadossonhoscostaazul@gmail.com

✅ *PARA RESERVAR:*
1. Escolha a suíte desejada.
2. Faça o pagamento da entrada de 50% ou o valor de 100% com desconto.
3. Envie o comprovante por este WhatsApp.
4. Informe os dados do titular.
5. Receba a confirmação.

🌊 *Política de Cancelamento:*
• Cancelamento grátis até 14 dias antes.
• Após, 50% do valor.
• No dia ou não comparecimento, sem reembolso.

Agradecemos o contato!
Equipe Pousada dos Sonhos ✨""".format(desconto_percent)

    return mensagem

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)