import socket
import requests
import subprocess
import os
from playsound import playsound

# === CONFIGURAZIONE ===

api_key = "sk_5a63eaea8efe97798a22292e157f3d7d478a37a50383e821"
voice_id = "cgSgspJ2msm6clMCkdW9"

oauth_token = "oauth:33egy08tlmvwg0uyd5zjynpmtzhqii"  # Devi lasciare "oauth:" davanti
nickname = "jetuchiha3"
channel = "#jetuchiha3"

excluded_users = [
    "streamelements", "nightbot", "streamlabs", "sery_bot",
    "jetuchihaia", "soundalerts"
]

excluded_words = [
    "Best viewers on", "cheap viewers", "dio", "negro", "frocio"
]

# === CONNESSIONE A TWITCH ===

sock = socket.socket()
sock.connect(("irc.chat.twitch.tv", 6667))
sock.send(f"PASS {oauth_token}\r\n".encode('utf-8'))
sock.send(f"NICK {nickname}\r\n".encode('utf-8'))
sock.send(f"JOIN {channel}\r\n".encode('utf-8'))

print(f"Connesso a {channel}!")

# === LOOP PRINCIPALE ===

while True:
    resp = sock.recv(2048).decode('utf-8')

    # Rispondi ai PING
    if resp.startswith("PING"):
        sock.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
        continue

    # Ignora messaggi di sistema (tipo 001, 002, ecc.)
    if resp.startswith(":tmi.twitch.tv"):
        continue

    # Processa solo i veri messaggi
    if "PRIVMSG" in resp:
        try:
            username = resp.split('!', 1)[0][1:].lower()
            message = resp.split('PRIVMSG', 1)[1].split(':', 1)[1].strip()

            print(f"[{username}] {message}")

            # Filtra utenti
            if username in excluded_users:
                print(f"Ignorato utente {username}")
                continue

            # Filtra messaggi con parole proibite
            if any(word.lower() in message.lower() for word in excluded_words):
                print(f"Ignorato messaggio per parola proibita")
                continue

            # Cancella output.mp3 vecchio se esiste
            output_path = "output.mp3"
            if os.path.exists(output_path):
                os.remove(output_path)

            # Crea richiesta API
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            data = {
                "text": message,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }

            response = requests.post(url, headers=headers, json=data)

            if response.status_code != 200:
                print(f"Errore nella richiesta API: {response.text}")
                continue

            # Salva il nuovo file
            with open(output_path, "wb") as f:
                f.write(response.content)

            # Riproduci l'audio
            playsound(output_path)

        except Exception as e:
            print(f"Errore: {e}")
