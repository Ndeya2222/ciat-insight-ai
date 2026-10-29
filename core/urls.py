from django.contrib.auth import views as auth
from django.urls import path
from . import views as v
urlpatterns = [
    path("", v.dashboard, name="dashboard"),
    path("connexion/", auth.LoginView.as_view(template_name="core/login.html"), name="login"),
    path("deconnexion/", auth.LogoutView.as_view(), name="logout"),
    path("projets/", v.project_list, name="project_list"),
    path("projets/nouveau/", v.project_create, name="project_create"),
    path("projets/export.xlsx", v.project_export, name="project_export"),
    path("projets/importer/", v.project_import, name="project_import"),
    path("rapport.pdf", v.report_pdf, name="report_pdf"),
    path("projets/<int:pk>/", v.project_detail, name="project_detail"),
    path("projets/<int:pk>/modifier/", v.project_edit, name="project_edit"),
    path("projets/<int:pk>/supprimer/", v.project_delete, name="project_delete"),
    path("assistant/", v.assistant, name="assistant"),
]
