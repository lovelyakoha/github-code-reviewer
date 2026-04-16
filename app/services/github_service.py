import requests
import os
import time
import jwt

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
APP_ID = os.getenv("GITHUB_APP_ID")


def get_jwt_token():
    private_key = os.getenv("GITHUB_PRIVATE_KEY")
    private_key = private_key.replace("\\n", "\n")

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": APP_ID
    }

    return jwt.encode(payload, private_key, algorithm="RS256")


def get_installation_token(installation_id: int):
    jwt_token = get_jwt_token()

    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.post(url, headers=headers)

    if response.status_code != 201:
        print("Erreur lors de la récupération du token d'installation :", response.status_code)
        return None

    return response.json().get("token")


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
        installation_id = payload.get("installation", {}).get("id") or 116956499

        print(f"Action : {action}")
        print(f"Titre : {title}")
        print(f"Auteur : {author}")
        print(f"URL : {url}")

        if action not in ["opened", "synchronize"]:
            return {"status": "ignored"}

        token = get_installation_token(installation_id)

        if not token:
            print("Impossible de récupérer le token d'installation")
            return {"status": "error"}

        diff = get_pr_diff(repo_full_name, pr_number, token)

        if not diff:
            print("Aucun diff trouvé, on arrête")
            return {"status": "no diff"}

        analyse = analyze_with_ai(diff)

        post_comment(repo_full_name, pr_number, analyse, token)

        return {
            "status": "processed",
            "pr_title": title,
            "author": author
        }

    return {"status": "ignored"}


def get_pr_diff(repo_full_name: str, pr_number: int, token: str):
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Erreur lors de la récupération du diff :", response.status_code)
        return None

    files = response.json()
    diff_text = ""

    for file in files:
        filename = file.get("filename")
        patch = file.get("patch", "")
        diff_text += f"\n\nFichier : {filename}\n{patch}"

    return diff_text


def analyze_with_ai(diff: str):
    prompt = f"""Analyse ce code et dis-moi s'il y a des problèmes dans ces 3 domaines :

1. Securite : mots de passe en dur, donnees sensibles exposees, failles connues
2. Performance : boucles inutiles, mauvaise complexite, optimisations possibles
3. Proprete : code duplique, nommage peu clair, fonctions trop longues

Pour chaque probleme trouve, precise la ligne et propose une correction.
Si le code est correct, dis-le simplement.

Voici le code modifie :
{diff}"""

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        print("Erreur Groq :", response.status_code, response.text)
        return "Erreur lors de l'analyse du code."

    data = response.json()
    return data["choices"][0]["message"]["content"]


def post_comment(repo_full_name: str, pr_number: int, comment_text: str, token: str):
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    body = f"## Analyse automatique du code\n\n{comment_text}"

    response = requests.post(url, headers=headers, json={"body": body})

    if response.status_code == 201:
        print("Commentaire posté avec succès")
    else:
        print("Erreur lors du post du commentaire :", response.status_code)