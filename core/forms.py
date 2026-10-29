from django import forms
from .models import STATUS, TRANSITIONS, Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "problem", "solution", "owner", "domain", "cohort", "submitted_on",
                  "status", "progress", "objectives", "deadline", "mentor", "budget"]
        widgets = {"submitted_on": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
                   "deadline": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        cur = self.instance.status if self.instance.pk else "soumis"
        allowed = [cur] + TRANSITIONS[cur]
        if "status" in self.fields:
            self.fields["status"].choices = [c for c in STATUS if c[0] in allowed]
        for n, f in self.fields.items():
            f.widget.attrs["class"] = "form-select" if isinstance(f.widget, forms.Select) else "form-control"
    def clean(self):
        d = super().clean()
        if d.get("deadline") and d.get("submitted_on") and d["deadline"] < d["submitted_on"]:
            self.add_error("deadline", "La date limite ne peut pas précéder la date de soumission.")
        if d.get("status") == "termine" and d.get("progress") != 100:
            self.add_error("progress", "Un projet terminé doit avoir une progression de 100 %.")
        return d

class MentorProjectForm(ProjectForm):
    """Le mentor ne peut mettre à jour que la progression et la description."""
    class Meta(ProjectForm.Meta):
        fields = ["description", "progress"]
