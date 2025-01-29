import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
import os
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

# Permitir conexões do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, defina a URL do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

# SEU TOKEN DO HUGGING FACE (NÃO EXPONHA PUBLICAMENTE)
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# Nome do modelo na API (tente Mistral se Falcon estiver lento)
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

# Dicionário de gírias gamer
GIRIAS_GAMER = {giria["term"].lower(): giria["meaning"] for giria in [
    {"term": "Mec",
     "meaning": "Refere-se a habilidades manuais e técnicas no jogo, como execução precisa de comandos."},
    {"term": "Trotos", "meaning": "Algo ou alguém muito forte ou apelão."},
    {"term": "Tankar", "meaning": "Absorver dano no lugar dos aliados, geralmente com um personagem 'tanque'."},
    {"term": "Arrasta", "meaning": "Convite para jogar ou carregar alguém para a vitória."},
    {"term": "Vou de base", "meaning": "Significa que o jogador foi eliminado/morto ou está retornando à base."},
    {"term": "Nerf", "meaning": "Quando algo no jogo é enfraquecido."},
    {"term": "Buff", "meaning": "Quando algo é fortalecido ou melhorado."},
    {"term": "Carry", "meaning": "Jogador que carrega o time para a vitória, geralmente o que mais causa dano."},
    {"term": "Feedar", "meaning": "Quando alguém morre várias vezes, fortalecendo o adversário."},
    {"term": "GG", "meaning": "Good Game, usado para dizer que o jogo foi bom ou que está perdido."},
    {"term": "Tiltar", "meaning": "Ficar frustrado ou bravo durante o jogo, afetando o desempenho."},
    {"term": "Noob", "meaning": "Jogador iniciante ou inexperiente, usado pejorativamente às vezes."},
    {"term": "Tryhard", "meaning": "Jogador que se esforça ao extremo para ganhar, às vezes provocativo."},
    {"term": "Meta", "meaning": "Estratégias ou personagens mais eficientes no momento."},
    {"term": "Farmar", "meaning": "Focar em acumular recursos ou dinheiro no jogo."},
    {"term": "Jukes", "meaning": "Desviar ou enganar os inimigos com habilidade ou movimentação."},
    {"term": "Rushar", "meaning": "Avançar rapidamente para atacar ou dominar um local."},
    {"term": "Camper", "meaning": "Jogador que fica escondido esperando o inimigo passar."},
    {"term": "Hitmarker", "meaning": "Quando você acerta um tiro, mas não elimina o inimigo."},
    {"term": "One shot", "meaning": "Quando alguém elimina o inimigo com um único golpe ou tiro."},
    {"term": "Stompar", "meaning": "Dominar completamente o adversário ou time inimigo."},
    {"term": "Ulti", "meaning": "Refere-se à habilidade suprema de um personagem."},
    {"term": "Lagado", "meaning": "Jogador com conexão ruim, que fica travando ou se movendo de forma estranha."},
    {"term": "Smurf", "meaning": "Conta alternativa usada por jogadores experientes para jogar em níveis mais baixos."},
    {"term": "Tá free", "meaning": "Algo fácil de conquistar ou fazer."},
    {"term": "Chitado", "meaning": "Jogador que está usando trapaças ou hacks."},
    {"term": "Zerado", "meaning": "Quando você não tem recursos ou está sem itens/vida."},
    {"term": "God", "meaning": "Algo muito bom, perfeito."},
    {"term": "Espalma", "meaning": "Usado para jogadores que se jogam sem controle."},
    {"term": "Apelar", "meaning": "Quando alguém usa táticas consideradas injustas ou personagens apelões."},
    {"term": "Flick", "meaning": "Movimento rápido e preciso para mirar."},
    {"term": "Backdoor", "meaning": "Atacar o objetivo principal sem que o inimigo perceba."},
    {"term": "Puxar wave", "meaning": "Levar os minions ou mobs para avançar no mapa."},
    {"term": "Splitar", "meaning": "Jogar separado do time para pressionar outra parte do mapa."},
    {"term": "Gank", "meaning": "Emboscada ou ataque surpresa a um jogador inimigo."},
    {"term": "Kite", "meaning": "Atacar enquanto recua para manter distância do inimigo."},
    {"term": "Ward", "meaning": "Item que dá visão do mapa."},
    {"term": "Snowball", "meaning": "Jogador ou time que fica muito forte e domina o jogo após pequenas vantagens."},
    {"term": "Ace", "meaning": "Eliminar todos os inimigos da rodada sozinho."},
    {"term": "Clutch", "meaning": "Virar uma rodada sozinho contra vários adversários."},
    {"term": "Prefire", "meaning": "Atirar antes de ver o inimigo, prevendo sua posição."},
    {"term": "Eco", "meaning": "Rodada em que o time não compra equipamentos para economizar."},
    {"term": "Aggro", "meaning": "Atração do inimigo para atacar você, controle de ameaças."},
    {"term": "Healer", "meaning": "Personagem ou jogador responsável por curar o time."},
    {"term": "Grindar", "meaning": "Jogar repetidamente para ganhar experiência ou recursos."},
    {"term": "Lootar", "meaning": "Pegar recursos, armas ou itens no mapa."},
    {"term": "Safe", "meaning": "Zona segura onde o jogador não toma dano."},
    {"term": "Drop", "meaning": "Lugar ou item que cai no mapa com recursos importantes."}
]}


# Função para enviar mensagem à API da Hugging Face
def get_ai_response(prompt):
    url = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    payload = {"inputs": prompt, "parameters": {"max_length": 100}}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                return result[0]["generated_text"]
            return "A IA não conseguiu gerar uma resposta válida."

        elif response.status_code == 503:
            return "A IA está sobrecarregada. Tente novamente mais tarde."

        else:
            return f"Erro na API da Hugging Face: {response.status_code} - {response.text}"

    except requests.exceptions.RequestException as e:
        return f"Erro ao conectar à Hugging Face: {str(e)}"


# Rota HTTP para testes
@app.get("/")
def read_root():
    return {"message": "Chat sobre gírias gamer funcionando com IA via API!"}


# 🔥 **Registrando o WebSocket corretamente**
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print('passei aqui')

    await websocket.send_text("Bem-vindo ao chatGG, digite o jargão gamer que voce tem dúvida!")

    while True:
        data = await websocket.receive_text()

        try:
            # Verifica se a entrada é JSON
            message_data = json.loads(data)
            user_message = message_data.get("message", "").strip().lower()
        except json.JSONDecodeError:
            user_message = data.strip().lower()  # Caso seja um texto simples

        # Se for uma gíria conhecida, responde direto
        if user_message in GIRIAS_GAMER:
            response_text = f"{user_message.capitalize()}: {GIRIAS_GAMER[user_message]}"
        else:
            # IA responde se não for uma gíria conhecida
            response_text = get_ai_response(f"Explique a gíria gamer: {user_message}. Responda de forma curta.")

        await websocket.send_text(response_text)
