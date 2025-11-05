from django import forms

from .models import SiteSettings


def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value in (None, ""):
        return False
    return str(value).lower() in {"true", "1", "on", "yes"}


class SiteSettingsForm(forms.ModelForm):
    registration_requires_invite = forms.TypedChoiceField(
        label="Require invitation to register",
        choices=[
            ("False", "Open registration"),
            ("True", "Invite only"),
        ],
        widget=forms.RadioSelect(),
        coerce=str_to_bool,
    )

    class Meta:
        model = SiteSettings
        fields = ["registration_requires_invite"]
        help_texts = {
            "registration_requires_invite": SiteSettings._meta.get_field(
                "registration_requires_invite"
            ).help_text
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current = (
            self.instance.registration_requires_invite
            if getattr(self, "instance", None)
            else False
        )
        self.initial.setdefault(
            "registration_requires_invite", "True" if current else "False"
        )

    def clean_registration_requires_invite(self):
        return bool(self.cleaned_data["registration_requires_invite"])
