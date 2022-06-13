from django.contrib.auth import logout
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('users:signup')
    template_name = 'users/signup.html'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        send_mail('Подтверждение регистрации на Yatube',
                  f'{first_name} {last_name}, вы зарегистрированы!',
                  'Yatube.ru <admin@yatube.ru>', [email], fail_silently=False)
        return super().form_valid(form)


def send_mail_ls(email):
    send_mail('Подтверждение регистрации Yatube', 'Вы зарегистрированы!',
              'Yatube.ru <admin@yatube.ru>', [email], fail_silently=False)


def pagelogout(request):
    if request.method == "POST":
        logout(request)

        return redirect('users:logout')
