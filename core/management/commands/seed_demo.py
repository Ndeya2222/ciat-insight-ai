import os
import random
from datetime import timedelta
from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import DOMAINS, TRANSITIONS, ChangeLog, Cohort, Funding, Milestone, Partner, Project

STATUSES = ["soumis", "evaluation", "rejete", "selectionne", "incubation", "incubation", "proto_cours", "proto_cours",
            "proto_ok", "termine", "termine", "suspendu"]
OWNERS = ["Awa Diop", "Moussa Ba", "Fatou Ndiaye", "Cheikh Sow", "Aminata Fall", "Ibrahima Sarr", "Khady Gueye", "Omar Diallo"]


class Command(BaseCommand):
    help = "Charge des données FICTIVES de démonstration (idempotent : aucun doublon)."

    def handle(self, *a, **k):
        today = timezone.localdate()
        rnd = random.Random(42)
        # Groupes et comptes de démonstration
        perms = Permission.objects.filter(content_type__app_label="core")
        g_coord, _ = Group.objects.get_or_create(name="Coordonnateur"); g_coord.permissions.set(perms)
        g_an, _ = Group.objects.get_or_create(name="Data Analyst"); g_an.permissions.set(perms.filter(codename__startswith="view"))
        g_men, _ = Group.objects.get_or_create(name="Mentor")
        users = {}
        for name, grp, staff, sup in [("admin_demo", None, True, True), ("coord_demo", g_coord, True, False),
                                      ("analyste_demo", g_an, False, False), ("mentor_demo", g_men, False, False), ("mentor2_demo", g_men, False, False)]:
            u, created = User.objects.get_or_create(username=name, defaults={"is_staff": staff, "is_superuser": sup})
            if created: u.set_password(os.environ.get("DEMO_PASSWORD", "Demo@CIAT2026")); u.save()
            if grp: u.groups.add(grp)
            users[name] = u
        cohorts = [Cohort.objects.get_or_create(name=n, defaults={"start_date": d})[0] for n, d in
                   [("Cohorte 2024-2025 (fictive)", today - timedelta(days=700)), ("Cohorte 2025-2026 (fictive)", today - timedelta(days=330)),
                    ("Cohorte 2026-2027 (fictive)", today - timedelta(days=60))]]
        partners = [Partner.objects.get_or_create(name=n, defaults={"kind": t, "sector": s, "status": st})[0] for n, t, s, st in
                    [("Partenaire Démo A", "Entreprise", "Énergie", "actif"), ("Partenaire Démo B", "ONG", "Agriculture", "actif"),
                     ("Partenaire Démo C", "Institution", "Éducation", "actif"), ("Partenaire Démo D", "Entreprise", "TIC", "inactif")]]
        for i in range(24):
            title = f"[DÉMO] Projet {i + 1:02d}"
            coh = cohorts[min(i // 8, 2)]
            status = STATUSES[i % len(STATUSES)]
            sub = coh.start_date + timedelta(days=rnd.randint(0, 50))
            sel = sub + timedelta(days=rnd.randint(15, 40)) if status not in ("soumis", "evaluation", "rejete") else None
            prog = {"soumis": 0, "evaluation": 0, "rejete": 0, "selectionne": 5, "incubation": rnd.randint(15, 55), "proto_cours": rnd.randint(35, 80),
                    "proto_ok": rnd.randint(80, 95), "termine": 100, "suspendu": rnd.randint(10, 40)}[status]
            p, created = Project.objects.get_or_create(title=title, defaults=dict(
                owner=OWNERS[i % len(OWNERS)], domain=DOMAINS[i % len(DOMAINS)][0], cohort=coh, submitted_on=sub, selected_on=sel,
                status=status, progress=prog, description="Projet fictif pour la démonstration.", problem="Problème fictif.", solution="Solution fictive.",
                deadline=today + timedelta(days=rnd.randint(-45, 120)) if status not in ("soumis", "evaluation", "rejete") else None,
                mentor=users["mentor_demo" if i % 2 == 0 else "mentor2_demo"], budget=rnd.choice([1, 2, 3, 5]) * 1_000_000, is_demo=True))
            if not created: continue
            ChangeLog.objects.create(project=p, user=users["admin_demo"], text="Projet fictif créé (seed_demo)")
            if sel:
                for j, t in enumerate(["Cadrage", "Prototype v1", "Tests utilisateurs"]):
                    due = sel + timedelta(days=30 * (j + 1))
                    done = due - timedelta(days=2) if (prog >= 30 * (j + 1) or status == "termine") else None
                    Milestone.objects.create(project=p, title=t, due_date=due, done_date=done)
                if i % 3 != 2:
                    Funding.objects.create(project=p, source=rnd.choice(["Fonds démo 1", "Fonds démo 2", "Partenaire démo"]),
                                           amount=rnd.choice([500_000, 1_000_000, 2_000_000]), date=sel + timedelta(days=20), status="obtenu")
                if i % 5 == 0:
                    Funding.objects.create(project=p, source="Subvention démo (en attente)", amount=1_500_000, date=today, status="attente")
                p.partners.add(partners[i % 4])
        self.stdout.write(self.style.SUCCESS(f"Données de démonstration prêtes ({Project.objects.filter(is_demo=True).count()} projets). Comptes : admin_demo, coord_demo, analyste_demo, mentor_demo / Demo@CIAT2026"))
