from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_text, force_bytes
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from Nemeku import settings
from .token import generatorToken
from .forms import UserRegistrationForm

def home(request):
    return render(request, 'comptes/index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Envoi mail de bienvenue
            subject = "Bienvenue sur Nemeku !"
            message = f"Bienvenue {user.first_name} {user.last_name},\n\nNous sommes ravis de vous compter parmi la communauté de Nemeku !\n\nMerci,\nL'équipe de support Nemeku"
            from_email = settings.EMAIL_HOST_USER
            to_list = [user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)

            # Email de confirmation
            current_site = get_current_site(request)
            email_subject = "Confirmation de l'adresse mail"
            message_confirm = render_to_string('emailconfirm.html', {
                'name': user.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generatorToken.make_token(user),
            })
            email = EmailMessage(email_subject, message_confirm, settings.EMAIL_HOST_USER, [user.email])
            email.fail_silently = False
            email.send()

            messages.success(request, 'Votre compte a été créé avec succès. Veuillez vérifier votre email pour l\'activer.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'comptes/register.html', {'form': form})

def logIn(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Votre compte n\'est pas activé.')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'comptes/login.html')

def logOut(request):
    logout(request)
    messages.success(request, 'Vous vous êtes déconnecté avec succès. Revenez vite !')
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and generatorToken.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Votre compte a été activé avec succès. Vous pouvez maintenant vous connecter.')
        return redirect('login')
    else:
        messages.error(request, 'Erreur lors de l\'activation du compte.')
        return redirect('home')