
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """Signup form for CustomUser. Keep role internal (users are 'user' by default)."""
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap classes (optional)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
        # ensure email is required
        self.fields["email"].required = True
