#!/data/data/com.termux/files/usr/bin/bash
# Script de instalação do Pousada PMS no Termux

# Cores para output
VERDE='\033[0;32m'
AMARELO='\033[1;33m'
AZUL='\033[0;34m'
VERMELHO='\033[0;31m'
RESET='\033[0m'

echo -e "${AZUL}🚀 Iniciando instalação do Pousada PMS...${RESET}"

# 1. Atualizar pacotes e instalar dependências básicas
echo -e "${AMARELO}📦 Atualizando pacotes e instalando Python, Git, wget, nano...${RESET}"
pkg update -y && pkg upgrade -y
pkg install -y python python-pip git wget nano

# 2. Clonar o repositório (substitua pela URL do seu repositório)
echo -e "${AMARELO}📂 Clonando repositório do GitHub...${RESET}"
git clone https://github.com/ThiagoAboo/pousada-pms-leve.git ~/pousada-pms-leve
cd ~/pousada-pms-leve

# 3. Instalar dependências Python
echo -e "${AMARELO}🐍 Instalando dependências Python...${RESET}"
pip install -r requirements.txt

# 4. Baixar e instalar o ngrok
echo -e "${AMARELO}📡 Baixando ngrok...${RESET}"
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz
tar xzf ngrok-v3-stable-linux-arm64.tgz
mv ngrok /data/data/com.termux/files/usr/bin/
chmod +x /data/data/com.termux/files/usr/bin/ngrok
rm ngrok-v3-stable-linux-arm64.tgz

# 5. Configurar token do ngrok (solicitar ao usuário)
echo -e "${AZUL}🔑 Agora você precisa configurar seu token do ngrok.${RESET}"
echo -e "${AZUL}👉 Acesse https://dashboard.ngrok.com/get-started/your-authtoken, copie seu token.${RESET}"
read -p "Cole seu token do ngrok: " NGROK_TOKEN
ngrok config add-authtoken "$NGROK_TOKEN"

echo -e "${VERDE}✅ Instalação concluída com sucesso!${RESET}"
echo -e "${VERDE}▶️ Para iniciar o servidor e o ngrok, execute: ./start.sh${RESET}"