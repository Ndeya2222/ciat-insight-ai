from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

STATUS = [("soumis", "Soumis"), ("evaluation", "En évaluation"), ("selectionne", "Sélectionné"),
    ("incubation", "En incubation"), ("proto_cours", "Prototype en cours"), ("proto_ok", "Prototype réalisé"),
    ("termine", "Terminé"), ("suspendu", "Suspendu"), ("rejete", "Rejeté")]
# Règles d'évolution du statut
TRANSITIONS = {"soumis": ["evaluation", "rejete"], "evaluation": ["selectionne", "rejete"],
    "selectionne": ["incubation", "suspendu"], "incubation": ["proto_cours", "suspendu"],
    "proto_cours": ["proto_ok", "suspendu"], "proto_ok": ["termine", "suspendu"],
    "suspendu": ["incubation"], "termine": [], "rejete": []}
ACTIVE = ["incubation", "proto_cours"]
CLOSED = ["termine", "rejete"]
DOMAINS = [("tic", "TIC, numérique, IA et données"), ("meca", "Mécanique, fabrication, maintenance"),
    ("agri", "Agriculture et environnement"), ("energie", "Énergie et énergies renouvelables"),
    ("pharma", "Pharmaceutique et biomédical"), ("edu", "Éducation et formation"),
    ("services", "Services aux collectivités et entrepreneuriat")]


class Cohort(models.Model):
    name = models.CharField("Nom", max_length=80, unique=True)
    start_date = models.DateField("Début")
    class Meta:
        ordering = ["start_date"]
    def __str__(self): return self.name


class Project(models.Model):
    title = models.CharField("Titre", max_length=200)
    description = models.TextField("Description", blank=True)
    problem = models.TextField("Problème à résoudre", blank=True)
    solution = models.TextField("Solution proposée", blank=True)
    owner = models.CharField("Porteur du projet", max_length=120)
    domain = models.CharField("Domaine", max_length=20, choices=DOMAINS)
    cohort = models.ForeignKey(Cohort, on_delete=models.PROTECT, related_name="projects", verbose_name="Cohorte")
    submitted_on = models.DateField("Date de soumission")
    selected_on = models.DateField("Date de sélection", null=True, blank=True)
    status = models.CharField("Statut", max_length=20, choices=STATUS, default="soumis")
    progress = models.PositiveSmallIntegerField("Progression (%)", default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    objectives = models.TextField("Objectifs", blank=True)
    deadline = models.DateField("Date limite", null=True, blank=True)
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="mentored", verbose_name="Mentor")
    budget = models.DecimalField("Budget prévisionnel (XOF)", max_digits=14, decimal_places=0, default=0,
        validators=[MinValueValidator(0)])
    updated_at = models.DateTimeField("Dernière mise à jour", auto_now=True)
    is_demo = models.BooleanField("Donnée fictive", default=False)
    class Meta:
        ordering = ["-submitted_on", "title"]
        indexes = [models.Index(fields=["status"]), models.Index(fields=["domain"])]
    def __str__(self): return self.title
    @property
    def late_milestones(self):
        return self.milestones.filter(done_date__isnull=True, due_date__lt=timezone.localdate()).count()
    @property
    def deadline_passed(self):
        return bool(self.deadline and self.deadline < timezone.localdate() and self.status not in CLOSED)
    @property
    def is_late(self):
        return self.status not in CLOSED and (self.deadline_passed or self.late_milestones > 0)


class Milestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField("Titre", max_length=200)
    description = models.TextField("Description", blank=True)
    due_date = models.DateField("Date prévue")
    done_date = models.DateField("Date de réalisation", null=True, blank=True)
    comment = models.TextField("Commentaire", blank=True)
    proof = models.CharField("Preuve / document (lien)", max_length=300, blank=True)
    class Meta:
        ordering = ["due_date"]
        constraints = [models.UniqueConstraint(fields=["project", "title"], name="uniq_milestone")]
    @property
    def state(self):
        if self.done_date: return "Réalisé"
        return "En retard" if self.due_date < timezone.localdate() else "Prévu"
    def __str__(self): return f"{self.project} – {self.title}"


class Partner(models.Model):
    name = models.CharField("Nom", max_length=150, unique=True)
    kind = models.CharField("Type", max_length=60)
    sector = models.CharField("Secteur", max_length=100, blank=True)
    contact = models.CharField("Contact professionnel", max_length=200, blank=True)
    status = models.CharField("Statut", max_length=10, choices=[("actif", "Actif"), ("inactif", "Inactif")], default="actif")
    projects = models.ManyToManyField(Project, blank=True, related_name="partners")
    def __str__(self): return self.name


class Funding(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="fundings")
    source = models.CharField("Source", max_length=150)
    amount = models.DecimalField("Montant", max_digits=14, decimal_places=0, validators=[MinValueValidator(1)])
    currency = models.CharField("Devise", max_length=3, default="XOF")
    date = models.DateField("Date")
    status = models.CharField("Statut", max_length=12, choices=[("obtenu", "Obtenu"), ("attente", "En attente")], default="obtenu")
    comment = models.CharField("Commentaire", max_length=250, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["project", "source", "date", "amount"], name="uniq_funding")]
    def __str__(self): return f"{self.source} – {self.amount} {self.currency}"


class ChangeLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    text = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created"]


class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.TextField(max_length=500)
    answer = models.TextField()
    mode = models.CharField(max_length=10, default="demo")
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created"]


class ImportLog(models.Model):
    """Traçabilité des importations de données."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    filename = models.CharField(max_length=200)
    created = models.PositiveIntegerField(default=0)
    errors = models.PositiveIntegerField(default=0)
    at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-at"]
