from dotenv import load_dotenv
import os


load_dotenv()


github_secret = os.getenv("GITHUB_SECRET")

print("La clé GitHub est :", github_secret)
