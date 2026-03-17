GitHub Code Review Bot

C'est quoi ce projet ?

Ce projet est un bot intelligent qui s'intègre directement à GitHub. Son rôle est d'analyser automatiquement le code écrit par un développeur lorsqu'il soumet une Pull Request.

Une Pull Request c'est une demande de fusion de code. Concrètement, quand un développeur termine une modification, il ne l'intègre pas directement dans le projet principal. Il crée une copie, fait ses changements dessus, puis demande à l'équipe de vérifier avant d'accepter.

Ce bot automatise l' étape de vérification. Dès qu'une Pull Request est ouverte ou modifiée, le bot détecte automatiquement les lignes de code modifiées, les envoie à une intelligence artificielle et poste une analyse complète directement comme commentaire sur la Pull Request.

L'analyse couvre 3 domaines :
- *Sécurité* : mots de passe écrits directement dans le code, données sensibles exposées, injections SQL
- *Performance*: boucles inutiles, mauvaise complexité, optimisations possibles
- *Propreté* : nommage peu clair, code dupliqué, fonctions trop longues



Comment ça fonctionne techniquement ?

Voici le chemin parcouru à chaque Pull Request :


Une Pull Request est ouverte sur GitHub
            ↓
GitHub envoie une notification au serveur via ngrok
            ↓
Le serveur FastAPI reçoit la notification
            ↓
Le bot récupère les lignes de code modifiées via l'API GitHub
            ↓
Le code est envoyé à l'IA (Groq / LLaMA 3.3) pour analyse
            ↓
L'IA retourne son analyse
            ↓
Le bot poste l'analyse comme commentaire sur la Pull Request




Les outils utilisés

- *Python* — le langage de programmation utilisé
- *FastAPI* — outil Python qui permet de créer un serveur web facilement
- *Uvicorn* — le moteur qui fait tourner le serveur FastAPI
- *ngrok* — outil qui expose un serveur local sur internet pour que GitHub puisse lui envoyer des notifications
- *Groq* — plateforme gratuite qui donne accès à l'IA LLaMA 3.3 de Meta
- *GitHub API* — permet au bot de lire le code modifié et de poster des commentaires



Prérequis

Avant de commencer, il faut disposer de :
- Un ordinateur avec Windows
- Une connexion internet
- Un compte GitHub (gratuit) → https://github.com
- Un compte Groq (gratuit) → https://console.groq.com
- Un compte ngrok (gratuit) → https://ngrok.com



Installation

Étape 1 — Installer Python
Installer python sur https://www.python.org

Pour vérifier que Python est bien installé, ouvrez PowerShell et tapez : *python --version*

Vous devriez voir la version de python que vous avez s'afficher 

Étape 2 — Installer Git
Installer git sur https://git-scm.com/downloads

Pour vérifier que Git est bien installé, ouvrez PowerShell et tapez : *git --version*

Vous devriez voir la version de git que vous avez s'afficher 

Étape 3 — Installer ngrok

1. Cliquez sur le lien https://ngrok.com et créez un compte gratuit
2. Une fois connecté, allez dans le menu *Getting Started* > *Your Authtoken*
3. Copiez votre token
4. Téléchargez ngrok pour Windows sur la même page
5. Extrayez le fichier .zip téléchargé
6. Ouvrez PowerShell dans le dossier où vous avez extrait ngrok et tapez : *ngrok config add-authtoken COLLEZ_VOTRE_TOKEN_PRECEDEMMENT_COPIER_ICI*


Étape 4 — Cloner le projet

Ouvrez PowerShell et tapez ces commandes une par une :

*git clone https://github.com/lovelyakoha/github-code-reviewer.git*


*cd github-code-reviewer*



Étape 5 — Créer l'environnement virtuel


Dans PowerShell tapez : *python -m venv venv* et *venv\Scripts\Activate.ps1*

Ca peut arriver qu'une erreur de permission s'affiche,si c'est le cas,tapez d'abord :

*Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned* et réessayez.

Quand l'environnement est activé, vous verrez `(venv)` au début de la ligne dans PowerShell.


Étape 6 — Installer les dépendances

Tapez dans le terminal, *pip install fastapi uvicorn requests python-dotenv* pour installer les dependances.

Étape 7 — Créer le fichier .env

Le fichier `.env` contient les clés privées (a ne pas partager).

Dans PowerShell tapez : *New-Item .env -ItemType File*


Ensuite ouvrez le fichier `.env` dans VS Code et collez exactement ceci dedans :

*GITHUB_SECRET=secret123
 GITHUB_TOKEN=votre_token_github
 GROQ_API_KEY=votre_clé_groq*


Vous remplacerez `votre_token_github` et `votre_clé_groq` dans les étapes suivantes.


Étape 8 — Créer un token GitHub

1. Connectez-vous sur **github.com**
2. Cliquez sur votre photo de profil en haut à droite ensuite sur  **Settings**
3. Dans le menu à gauche, descendez tout en bas et cliquez sur **Developer settings**
4. Cliquez sur **Personal access tokens** > **Fine-grained tokens**
5. Cliquez sur **Generate new token**
6. Remplissez les champs :
   - **Token name** : `code-review-bot`
   - **Expiration** : 90 days (selon votre preference)
   - **Repository access** : sélectionnez **Only select repositories** et choisissez votre repo
7. Descendez jusqu'à **Permissions** > **Repository permissions**
8. Trouvez **Issues** → cliquez sur le menu déroulant et sélectionnez **Read and Write**
9. Trouvez **Pull requests** → cliquez sur le menu déroulant et sélectionnez **Read and Write**
10. Cliquez sur **Generate token** en bas de la page
11. Copiez le token immédiatement (il disparait juste apres )
12. Ouvrez votre fichier `.env` et remplacez `votre_token_github` par le token copié


Étape 9 — Créer une clé Groq

La clé Groq permet au bot d'utiliser l'IA pour analyser le code.

1. Allez sur **console.groq.com** et créez un compte gratuit
2. Une fois connecté, cliquez sur **API Keys** dans le menu à gauche
3. Cliquez sur **Create API Key**
4. Donnez lui un nom 
5. Copiez la clé affichée
6. Ouvrez votre fichier `.env` et remplacez `votre_clé_groq` par la clé copiée



## Lancement du bot

Étape 10 — Lancer ngrok

Ouvrez un premier PowerShell et tapez : *ngrok http 8000*


ngrok va afficher quelque chose comme ceci :
Forwarding   https://abc123.ngrok-free.app -> http://localhost:8000


Copiez l'URL `https://abc123.ngrok-free.app`, vous en aurez besoin à l'étape 12.

Laissez ce terminal ouvert, ne le fermez pas.



Étape 11 — Lancer le serveur
Ouvrez un deuxième PowerShell et tapez ces commandes une par une :

*cd github-code-reviewer
 venv\Scripts\Activate.ps1
 uvicorn app.main:app --reload*

Le serveur est prêt quand ce message apparaît : *Application startup complete.*
Laissez ce terminal ouvert aussi, ne le fermez pas.


Étape 12 — Configurer le webhook GitHub
Le webhook est ce qui permet à GitHub d'envoyer une notification au serveur à chaque Pull Request.

1. Allez sur votre repo GitHub
2. Cliquez sur **Settings** ensuite dans le menu à gauche cliquez sur **Webhooks** et sur **Add webhook**
3. Remplissez les champs :
   - **Payload URL** : collez votre URL ngrok de l'etape 10 et ajoutez `/webhook` à la fin
     Exemple : `https://abc123.ngrok-free.app/webhook`
   - **Content type** : cliquez sur le menu déroulant et sélectionnez `application/json`
   - **Secret** : tapez `secret123`
   - Dans la section **Which events would you like to trigger this webhook?** cochez **Let me select individual events**, décochez tout et cochez uniquement **Pull requests**
4. Cliquez sur **Add webhook**

A chaque fois que ngrok est redémarré, il génère une nouvelle URL différente. Il faudra revenir dans Settings > Webhooks, cliquer sur le webhook et mettre à jour le Payload URL avec la nouvelle URL ngrok.


## Tester le bot

Étape 13 — Créer une Pull Request de test

1. Allez sur votre repo GitHub
2. Créez un nouveau fichier `test.py`
3. Collez ce code dedans :

```
python
import os

# Mauvaise pratique : mots de passe et clés secrètes en dur dans le code
password = "admin123"
secret_key = "abc123secret"
api_key = "sk-1234567890abcdef"
db_password = "root1234"

# Faille de sécurité : injection SQL possible
def get_user(db, user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return query

# Faille de sécurité : injection SQL possible
def get_orders(db, status):
    query = "SELECT * FROM orders WHERE status = '" + status + "'"
    return query

# Mauvaise performance : boucle imbriquée inutile O(n²)
def calculer_total(nombres):
    result = []
    for i in range(len(nombres)):
        for j in range(len(nombres)):
            result.append(nombres[i] * nombres[j])
    return result

# Mauvaise performance : recalcul inutile à chaque itération
def trouver_maximum(liste):
    maximum = 0
    for i in range(len(liste)):
        if liste[i] > maximum:
            maximum = liste[i]
        total = sum(liste)
    return maximum

# Mauvaise propreté : nom de fonction peu clair
def a(x, y, z):
    return x + y + z

# Mauvaise propreté : nom de variable peu clair
def traitement(d):
    r = []
    for i in d:
        if i > 0:
            r.append(i * 2)
    return r

# Mauvaise propreté : conditions trop imbriquées
def verifier(x, y, z, w):
    if x > 0:
        if y > 0:
            if z > 0:
                if w > 0:
                    return x + y + z + w
                else:
                    return 0
            else:
                return 0
        else:
            return 0
    else:
        return 0

# Mauvaise propreté : code dupliqué
def calculer_prix_client1(prix, quantite):
    total = prix * quantite
    tva = total * 0.2
    total_ttc = total + tva
    print("Total TTC client 1 :", total_ttc)
    return total_ttc

def calculer_prix_client2(prix, quantite):
    total = prix * quantite
    tva = total * 0.2
    total_ttc = total + tva
    print("Total TTC client 2 :", total_ttc)
    return total_ttc
```

4. Cliquez sur **Commit Changes** en haut a droite
5. En bas de la page cochez **Create a new branch** au lieu de commit sur main
6. Cliquez sur **Propose new file**
7. Cliquez sur **Create pull request**

Quelques secondes après, le bot va automatiquement poster un commentaire avec l'analyse complète du code sur la Pull Request !
 
Cette etape propose juste un code generer avec plein d'erreur pour tester l'IA. C'est juste une etape de verification.


## Structure du projet


github-code-reviewer/
├── app/
│   ├── main.py                  # Point d'entrée du serveur
│   ├── api/
│   │   └── webhook.py           # Reçoit les événements GitHub
│   └── services/
│       └── github_service.py    # Logique principale du bot
├── .env                         # Clés API (à créer manuellement, ne pas partager)
├── .gitignore                   # Liste des fichiers exclus de GitHub
└── README.md                    # Ce fichier




## En cas de problème

**Le serveur ne démarre pas**
→ Vérifiez que le venv est bien activé avec `venv\Scripts\Activate.ps1` et que `(venv)` apparaît dans le terminal.

**Le bot ne réagit pas à la Pull Request**
→ Vérifiez que ngrok tourne dans un terminal, que le serveur tourne dans un autre terminal, et que l'URL dans le webhook GitHub correspond bien à l'URL ngrok actuelle.

**Erreur 401**
→ Le token GitHub n'est pas chargé. Vérifiez que le fichier `.env` existe bien à la racine du projet et qu'il contient le bon token.

**Erreur 403**
→ Le token GitHub n'a pas les bons droits. Recréez un token avec Issues et Pull requests en Read and Write.
