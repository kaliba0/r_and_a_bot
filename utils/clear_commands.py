import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
CLIENT_ID = os.getenv("CLIENT_ID")

base_url = "https://discord.com/api/v10"
headers = {
    "Authorization": f"Bot {TOKEN}",
    "Content-Type": "application/json"
}

if __name__ == "__main__":
    print("Début de la suppression des commandes (/) globales et de guilde...")

    # Suppression des commandes globales
    global_url = f"{base_url}/applications/{CLIENT_ID}/commands"
    global_commands = requests.get(global_url, headers=headers)
    if global_commands.status_code == 200:
        for cmd in global_commands.json():
            delete_url = f"{base_url}/applications/{CLIENT_ID}/commands/{cmd['id']}"
            del_resp = requests.delete(delete_url, headers=headers)
            if del_resp.status_code == 204:
                print(f"Commande globale supprimée : {cmd['name']}")
            else:
                print(f"Erreur lors de la suppression de la commande globale {cmd['name']}")
    else:
        print("Impossible de récupérer les commandes globales.")

    # Suppression des commandes de guilde
    guild_url = f"{base_url}/applications/{CLIENT_ID}/guilds/{GUILD_ID}/commands"
    guild_commands = requests.get(guild_url, headers=headers)
    if guild_commands.status_code == 200:
        for cmd in guild_commands.json():
            delete_url = f"{base_url}/applications/{CLIENT_ID}/guilds/{GUILD_ID}/commands/{cmd['id']}"
            del_resp = requests.delete(delete_url, headers=headers)
            if del_resp.status_code == 204:
                print(f"Commande de guilde supprimée : {cmd['name']}")
            else:
                print(f"Erreur lors de la suppression de la commande de guilde {cmd['name']}")
    else:
        print("Impossible de récupérer les commandes de guilde.")

    print("Toutes les commandes (/) ont été correctement supprimées.")
