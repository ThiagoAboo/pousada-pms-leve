#!/data/data/com.termux/files/usr/bin/bash
# Script para iniciar o servidor Flask e o ngrok

# Cores
VERDE='\033[0;32m'
AMARELO='\033[1;33m'
AZUL='\033[0;34m'
VERMELHO='\033[0;31m'
RESET='\033[0m'

cd ~/pousada-pms-leve

echo -e "${AZUL}🌐 Iniciando servidor Flask na porta 5000...${RESET}"

# Verifica se já há um processo Flask rodando
if pgrep -f "python app.py" > /dev/null; then
    echo -e "${AMARELO}⚠️ Servidor Flask já está rodando. Encerrando processo anterior...${RESET}"
    pkill -f "python app.py"
    sleep 2
fi

# Inicia o Flask em background e salva o PID
python app.py > flask.log 2>&1 &
FLASK_PID=$!
echo -e "${VERDE}✅ Flask iniciado (PID: $FLASK_PID)${RESET}"

# Aguarda alguns segundos para o Flask subir
sleep 3

# Inicia o ngrok
echo -e "${AZUL}🔗 Iniciando ngrok...${RESET}"
ngrok http 5000 --log=stdout > ngrok.log 2>&1 &
NGROK_PID=$!

# Aguarda o ngrok estabelecer conexão
sleep 3

# Extrai a URL pública do ngrok a partir do log
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o 'https://[^"]*\.ngrok-free\.app' | head -1)

if [ -n "$NGROK_URL" ]; then
    echo -e "${VERDE}✅ ngrok rodando (PID: $NGROK_PID)${RESET}"
    echo -e "${AZUL}🌍 URL pública: ${VERDE}$NGROK_URL${RESET}"
    echo -e "${AMARELO}📱 Compartilhe este link com quem quiser acessar o sistema.${RESET}"
else
    echo -e "${VERMELHO}❌ Não foi possível obter a URL do ngrok. Verifique se ele está rodando corretamente.${RESET}"
    echo -e "${AMARELO}🔍 Acesse http://127.0.0.1:4040 para ver o status.${RESET}"
fi

echo -e "${AMARELO}⚠️ Pressione Ctrl+C para encerrar o ngrok e o servidor Flask.${RESET}"

# Função de limpeza ao sair
cleanup() {
    echo -e "${AMARELO}🛑 Encerrando processos...${RESET}"
    kill $FLASK_PID 2>/dev/null
    kill $NGROK_PID 2>/dev/null
    echo -e "${VERDE}✅ Processos encerrados.${RESET}"
    exit 0
}

trap cleanup SIGINT

# Mantém o script rodando para que o trap funcione
while true; do
    sleep 1
done