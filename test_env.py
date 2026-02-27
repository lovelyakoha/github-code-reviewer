from dotenv import load_dotenv
import os

# Charge le fichier .env
load_dotenv()

# Récupère la valeur de GITHUB_SECRET
github_secret = os.getenv("GITHUB_SECRET")

print("La clé GitHub est :", github_secret)
