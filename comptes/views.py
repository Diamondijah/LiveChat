from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_text, force_bytes
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from Nemeku import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from .token import generatorToken
# Create your views here.

def home(request):
    return render(request, 'comptes/index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST['password']
        password1 = request.POST.get('password1')
        if User.objects.filter(username=username):
            messages.error(request, 'Ce nom a deja été pris')
            return redirect('register')
        if User.objects.filter(email=email):
            messages.error(request, 'Cet email a deja été pris')
            return redirect('register')
        if not username.isalnum():
            messages.error(request, 'le nom d\'utilisateur doit être alphanumérique')
            return redirect('register')
        if password!=  password1:
            messages.error(request, 'les mots de passe ne sont pas identiques')
            return redirect('register')
        
        mon_utilisateur = User.objects.create_user(username, email, password)
        mon_utilisateur.first_name = firstname
        mon_utilisateur.last_name = lastname
        mon_utilisateur.is_active  = False
        mon_utilisateur.save()
        messages.success(request, 'votre compte a ete créé avec succés')
        #Envoi mail  de bienvenu
        subject = "Bienvenue sur Nemeku !"
        message = "Bienvenue" + mon_utilisateur.first_name + mon_utilisateur.last_name + "\n Nous sommes ravis de vous compter parmi la communauté de Nemeku ! \n\n\n Merci \n\n l'équipe de support Nemeku"
        from_email = settings.EMAIL_HOST_USER
        to_list  = [mon_utilisateur.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

#Email de confirmation
        current_site = get_current_site(request)
        email_subject = "Confirmation de l'adresse mail"
        messageConfirm = render_to_string("emailconfirm.html", 
        {
            'name': mon_utilisateur.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(mon_utilisateur.pk)),
            'token': generatorToken.make_token(mon_utilisateur)
        })
        email = EmailMessage(
            email_subject,
            messageConfirm,
            settings.EMAIL_HOST_USER,
            [mon_utilisateur.email]
        )
        email.fail_silently = False
        email.send()



        return redirect('login')
    return render(request, 'comptes/register.html')

def logIn(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        my_user = User.objects.get(username=username)
        if user is not None:
            login(request, user)
            username = user.username            
            return render(request, 'comptes/index.html', {'username': username})
        elif my_user.is_active == False:
            messages.error(request, 'Votre compte n\'est pas activé')
            return redirect('login')
        else:
            messages.error(request, 'votre compte n\'existe pas')
            return redirect('login')
        
    return render(request, 'comptes/login.html')

def logOut(request):
    logout(request)
    messages.success(request, 'Nemeku nest pas pareil sans vous revenez en ligne')
    return redirect('home')
    #return render(request, 'comptes/logout.html')


def activate(request, uidb64, token):
    try: 
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist): 
        user = None

    if user is not None and generatorToken.check_token(user, token): 
        user.is_active = True
        user.save()
        messages.success(request, 'Votre compte a été activé avec succés')
        return redirect('login')
    else :
        messages.error(request, 'Erreur lors de l n\'activation')
        return redirect('home')