import requests
import os


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Headers pour les appels à l'API GitHub
headers_github = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


def process_github_event(event_type: str, payload: dict):
    print("Type d'événement reçu :", event_type)

    if event_type == "push":
        print("PUSH détecté, on ne fait rien pour l'instant")

    elif event_type == "pull_request":
        print("PULL REQUEST détectée")

        action = payload.get("action")
        pr = payload.get("pull_request", {})

        title = pr.get("title")
        author = pr.get("user", {}).get("login")
        url = pr.get("html_url")
        pr_number = pr.get("number")
        repo_full_name = payload.get("repository", {}).get("full_name")

        print(f"Action : {action}")
        print(f"Titre : {title}")
        print(f"Auteur : {author}")
        print(f"URL : {url}")

        # On analyse seulement quand la PR est ouverte ou mise à jour
        if action not in ["opened", "synchronize"]:
            return {"status": "ignored"}

        # On récupère les fichiers modifiés dans la PR
        diff = get_pr_diff(repo_full_name, pr_number)

        if not diff:
            print("Aucun diff trouvé, on arrête")
            return {"status": "no diff"}

        # On envoie le diff à Gemini pour analyse
        analyse = analyze_with_ai(diff)

        # On poste le résultat comme commentaire sur la PR
        post_comment(repo_full_name, pr_number, analyse)

        return {
            "status": "processed",
            "pr_title": title,
            "author": author
        }

    return {"status": "ignored"}


def get_pr_diff(repo_full_name: str, pr_number: int):
    # On appelle l'API GitHub pour avoir la liste des fichiers modifiés
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files"
    response = requests.get(url, headers=headers_github)

    if response.status_code != 200:
        print("Erreur lors de la récupération du diff :", response.status_code)
        return None

    files = response.json()
    diff_text = ""

    for file in files:
        filename = file.get("filename")
        patch = file.get("patch", "")

        # patch contient les lignes ajoutées/supprimées
        diff_text += f"\n\nFichier : {filename}\n{patch}"

    return diff_text


def analyze_with_ai(diff: str):
    # On prépare le prompt qu'on envoie à Gemini
    prompt = f"""Analyse ce code et dis-moi s'il y a des problèmes dans ces 3 domaines :

1. Securite : mots de passe en dur, donnees sensibles exposees, failles connues
2. Performance : boucles inutiles, mauvaise complexite, optimisations possibles
3. Proprete : code duplique, nommage peu clair, fonctions trop longues

Pour chaque probleme trouve, precise la ligne et propose une correction.
Si le code est correct, dis-le simplement.

Voici le code modifie :
{diff}"""

    # URL de l'API Gemini avec la clé en paramètre
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    # On formate la requête comme Gemini l'attend
    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, json=body)

    if response.status_code != 200:
        print("Erreur Gemini :", response.status_code, response.text)
        return "Erreur lors de l'analyse du code."

    data = response.json()

    # On récupère le texte dans la réponse de Gemini
    return data["candidates"][0]["content"]["parts"][0]["text"]


def post_comment(repo_full_name: str, pr_number: int, comment_text: str):
    # On poste un commentaire sur la PR via l'API GitHub
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"

    body = f"## Analyse automatique du code\n\n{comment_text}"

    response = requests.post(url, headers=headers_github, json={"body": body})

    if response.status_code == 201:
        print("Commentaire posté avec succès")
    else:
        print("Erreur lors du post du commentaire :", response.status_code)