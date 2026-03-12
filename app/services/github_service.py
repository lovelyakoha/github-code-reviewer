import requests
import os


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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

        
        if action not in ["opened", "synchronize"]:
            return {"status": "ignored"}

        
        diff = get_pr_diff(repo_full_name, pr_number)

        if not diff:
            print("Aucun diff trouvé, on arrête")
            return {"status": "no diff"}

        
        analyse = analyze_with_ai(diff)

        
        post_comment(repo_full_name, pr_number, analyse)

        return {
            "status": "processed",
            "pr_title": title,
            "author": author
        }

    return {"status": "ignored"}


def get_pr_diff(repo_full_name: str, pr_number: int):
    
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

    # URL de l'API Groq
    url = "https://api.groq.com/openai/v1/chat/completions"

    # Headers avec la clé Groq
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


def post_comment(repo_full_name: str, pr_number: int, comment_text: str):

    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"

    body = f"## Analyse automatique du code\n\n{comment_text}"

    response = requests.post(url, headers=headers_github, json={"body": body})

    if response.status_code == 201:
        print("Commentaire posté avec succès")
    else:
        print("Erreur lors du post du commentaire :", response.status_code)