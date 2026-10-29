#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
# Données fictives de démonstration (mettre SEED_DEMO=0 pour une vraie mise en production)
if [ "${SEED_DEMO:-1}" = "1" ]; then python manage.py seed_demo; fi
