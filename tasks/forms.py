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
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["email"].required = True


class CustomUserUpdateForm(forms.ModelForm):
    """Form to update user info (excluding username & password)."""
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class TaskForm(forms.ModelForm):
    collaborators = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),  # dynamically filled in __init__
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',  # Select2 multi-select
            'multiple': 'multiple',
            'data-placeholder': 'Select one or more collaborators',
        })
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "due_date",
            "assigned_to",
            "is_completed",
            "collaborators",
            "attachment",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter task title",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter task details...",
            }),
            "due_date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control",
            }),
            "assigned_to": forms.Select(attrs={
                "class": "form-control",
            }),
            "is_completed": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
            "attachment": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
        }

    def __init__(self, *args, **kwargs):
        # ✅ Pop current user (passed from view)
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # ✅ Limit collaborators to all users except the current one
        if user:
            self.fields["collaborators"].queryset = CustomUser.objects.exclude(pk=user.pk)
        else:
            self.fields["collaborators"].queryset = CustomUser.objects.all()

        # ✅ Add consistent Bootstrap style to all (except select2)
        for name, field in self.fields.items():
            if name != "collaborators":
                if not isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs.setdefault("class", "form-control")

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Add a comment...',
                'class': 'form-control',
            }),
        }

class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email address',
        })
    )