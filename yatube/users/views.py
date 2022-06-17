from typing import Optional
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url: Optional[str] = reverse_lazy('posts:index')
    template_name: str = 'users/signup.html'
