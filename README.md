# CIAT Insight AI — « Des données aux décisions »
Tableau de bord décisionnel du CIAT (Projet 3, ISEP Amadou Trawaré). Django 5.1, Bootstrap 5, Chart.js, openpyxl.

## Installation (Windows : `py -m venv venv` puis `venv\Scripts\activate`)
```
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo          # données FICTIVES, sans doublon si relancé
python manage.py runserver          # http://127.0.0.1:8000
python manage.py test               # 18 tests
```
Comptes de démonstration (mot de passe `Demo@CIAT2026` en local, ou la valeur de `DEMO_PASSWORD`) : `admin_demo`, `coord_demo`, `analyste_demo`, `mentor_demo`.
Premier administrateur réel : `python manage.py createsuperuser`. Changez/supprimez les comptes démo en production.

## Import et rapport
- **Importer** (coordonnateur/admin) : `/projets/importer/`, modèle `sample_import.csv`. Colonnes `titre, porteur, domaine, cohorte, date_soumission, budget` ; aperçu, rapport d'erreurs, confirmation explicite, doublons jamais écrasés, journal des imports.
- **Rapport PDF** : bouton « Rapport PDF » (tableau de bord et liste), avec filtres, période, constats, recommandations, limites et mention « Document de démonstration ».
- Tests : 22.

## Rôles (contrôlés côté serveur)
| Rôle | Droits |
|---|---|
| Administrateur (superuser) | Tout, y compris /admin |
| Coordonnateur | Tableau de bord, CRUD projets, jalons/financements/partenaires/cohortes via /admin, exports |
| Data Analyst | Lecture, filtres, assistant, export Excel (pas de création/suppression) |
| Mentor | Uniquement ses projets ; modifie progression et description |

## Définition des indicateurs
- **Candidatures reçues** = nombre de projets enregistrés (chaque projet provient d'une candidature) dans le périmètre filtré.
- **Sélectionnés** = projets avec une date de sélection. **Actifs** = statuts En incubation + Prototype en cours.
- **Prototypes réalisés** = statuts Prototype réalisé + Terminé. **Terminés** = statut Terminé.
- **En retard** = projet non clos (ni Terminé ni Rejeté) dont la date limite est dépassée OU ayant un jalon non réalisé après son échéance.
- **Partenariats actifs** = partenaires « actif » liés à au moins un projet du périmètre.
- **Financements** = somme des financements « Obtenu » en XOF (un financement unique par projet/source/date/montant).
- **Taux de sélection** = sélectionnés ÷ (sélectionnés + rejetés) ; **taux d'achèvement** = terminés ÷ sélectionnés. Affiché « n/d » si le dénominateur est 0.

## Assistant IA
Les chiffres sont calculés par `core/services.py` (ORM, fonctions contrôlées, aucun SQL libre). Sans `AI_API_KEY`, la réponse est calculée et étiquetée « mode démonstration ». Avec une clé, les faits calculés sont envoyés (titres de projets, sans noms de porteurs) au fournisseur pour reformulation ; en cas d'échec, retour automatique au mode démonstration. Limite : 10 questions/minute/utilisateur. Historique supprimable par l'utilisateur.

## Déploiement (exemple : Render)
Fichiers fournis : `render.yaml` (service web + base PostgreSQL), `build.sh`, `Procfile`, `requirements.txt` (gunicorn, psycopg, whitenoise).
1. Créez un dépôt GitHub et envoyez-y le projet : `git init && git add . && git commit -m "CIAT Insight AI" && git remote add origin <URL> && git push -u origin main`.
2. Sur render.com : **New → Blueprint**, choisissez le dépôt ; Render lit `render.yaml`, crée la base et le service.
3. Attendez la fin du build ; l'adresse `https://ciat-insight-ai-xxxx.onrender.com` est le lien à donner au jury.
4. Le mot de passe des comptes démo (`DEMO_PASSWORD`) est généré : lisez-le dans *Environment* du service. Pour une vraie mise en production, mettez `SEED_DEMO=0` et créez l'administrateur avec `python manage.py createsuperuser` (onglet *Shell*).
5. Pour activer l'IA : renseignez `AI_API_KEY` (sinon mode démonstration).
Vérifiez les conditions du plan gratuit (mise en veille, durée de la base) avant la date du jury. Tout autre hébergeur Django + PostgreSQL convient (variables : `DEBUG=0`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DATABASE_URL`).

## Identité visuelle
Logo ISEP Amadou Trawaré extrait du document d'évaluation (`core/static/core/img/`), couleurs brun et beige de ce logo. Le nom « CIAT Insight AI » est un logo textuel provisoire ; aucun logo officiel du CIAT n'a été inventé.

## Pas encore réalisé (étapes suivantes)
Export des graphiques en image, CRUD jalons/financements dans l'interface (disponible via /admin), détail multi-provider IA, documentation complète (rapport, guide, dictionnaire de données, journal des prompts), déploiement public. Aucune audit de sécurité indépendant n'a été réalisé.
