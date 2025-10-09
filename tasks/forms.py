
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Task, Comment

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

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role']  # exclude username & password

    # Optional: Add Bootstrap classes
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "assigned_to", "is_completed", "attachment"]
        widgets = {
            "due_date": forms.DateTimeInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']