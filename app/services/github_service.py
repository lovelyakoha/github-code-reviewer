import requests
import os
import time
import jwt

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
APP_ID = os.getenv("GITHUB_APP_ID")


def get_jwt_token():
    private_key = os.getenv("GITHUB_PRIVATE_KEY")
    if "\\n" in private_key:
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
        print("Erreur lors de la recuperation du token d'installation :", response.status_code)
        print("Reponse GitHub :", response.text)
        return None

    return response.json().get("token")


def process_github_event(event_type: str, payload: dict):
    print("Type d'evenement recu :", event_type)

    if event_type == "push":
        print("PUSH detecte, on ne fait rien pour l'instant")

    elif event_type == "pull_request":
        print("PULL REQUEST detectee")

        action = payload.get("action")
        pr = payload.get("pull_request", {})

        title = pr.get("title")
        author = pr.get("user", {}).get("login")
        url = pr.get("html_url")
        pr_number = pr.get("number")
        repo_full_name = payload.get("repository", {}).get("full_name")
        installation_id = payload.get("installation", {}).get("id") or 124139049

        print(f"Action : {action}")
        print(f"Titre : {title}")
        print(f"Auteur : {author}")
        print(f"URL : {url}")
        print(f"Installation ID utilise : {installation_id}")

        if action not in ["opened", "synchronize"]:
            return {"status": "ignored"}

        token = get_installation_token(installation_id)

        if not token:
            print("Impossible de recuperer le token d'installation")
            return {"status": "error"}

        diff = get_pr_diff(repo_full_name, pr_number, token)

        if not diff:
            print("Aucun diff trouve, on arrete")
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
        print("Erreur lors de la recuperation du diff :", response.status_code)
        return None

    files = response.json()
    diff_text = ""

    for file in files:
        filename = file.get("filename")
        patch = file.get("patch", "")
        diff_text += f"\n\nFichier : {filename}\n{patch}"

    return diff_text


def analyze_with_ai(diff: str):
    prompt = f"""Tu es un assistant expert en revue de code. Analyse le code ci-dessous et identifie les problemes dans ces 3 domaines.

Reponds UNIQUEMENT en Markdown valide, avec cette structure exacte :

## Analyse automatique du code

### Securite
Pour chaque probleme trouve :
- **Probleme** : description claire du probleme et la ligne concernee
- **Correction** : explication de la correction
- **Exemple** :
```python
// code corrige ici
```

### Performance
Pour chaque probleme trouve :
- **Probleme** : description claire du probleme et la ligne concernee
- **Correction** : explication de la correction
- **Exemple** :
```python
// code corrige ici
```

### Proprete
Pour chaque probleme trouve :
- **Probleme** : description claire du probleme et la ligne concernee
- **Correction** : explication de la correction
- **Exemple** :
```python
// code corrige ici
```

### Conclusion
Resume en 1-2 phrases.

Si aucun probleme n'est detecte dans un domaine, ecris : "Aucun probleme detecte."

Voici le code a analyser :
{diff}"""

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Tu es un expert en revue de code. Tu reponds uniquement en Markdown bien structure. Tu n'ajoutes jamais de texte en dehors de la structure demandee."},
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

    response = requests.post(url, headers=headers, json={"body": comment_text})

    if response.status_code == 201:
        print("Commentaire poste avec succes")
    else:
        print("Erreur lors du post du commentaire :", response.status_code)