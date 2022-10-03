from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from Assesment import settings
from django.contrib.sites.shortcuts import get_current_site
from . tokens import *

# Create your views here.
def index(request):
    return render(request, 'Loginpage/index.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        passwd = request.POST['passwd']
        # for authenticating by the static files
        user = authenticate(username=username, password=passwd) # this fn() returns none or not none response

        if user is not None:
            login(request, user)
            fname = user.first_name   # this for displaying the user name on the page frontend
            return render(request, 'Loginpage/index.html', {'fname': fname})
        else:
            messages.error(request, "Wrong Credentials")
            return redirect('index')

    return render(request, 'Loginpage/signin.html')





def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST.get('fname', False)
        lname = request.POST.get('lname', False)
        email = request.POST['email']
        passwd = request.POST['passwd']
        confirmpass = request.POST['confirmpass']

        if User.objects.filter(username = username):
            messages.error(request, "Username already exist. Please try some other authentications")
            return redirect('index')

        if User.objects.filter(email=email):
            messages.error(request, "Email already registered")
            return redirect('index')

        if len(username)>10:
            messages.error(request, 'length should be less than 10 characters')

        if passwd != confirmpass:
            messages.error(request, 'Password is different')

        if not username.isalnum():
            messages.error(request, 'Username must be Alpha-numeric')
            return redirect('index')

        myuser =User.objects.create_user(username, email, passwd)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False

        myuser.save()

        messages.success(request, "Your account has been created. ThankYou! \n We have sent you a confirmation Email.\n Please check and Verify it, for your account activation.")

        # Email message

        subject = "Welcome to ____ website --login info"
        message = "Hello " + myuser.first_name + "!! \n " + "Welcome and Thanku for registration. \n We have sent you a email for the authentication.\n Please confirm your Email address for activating your Account. \n \n Thanking You \n Abhishek Pathak"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email Confirmation

        current_site = get_current_site(request)
        email_subject = "Confirm your email @ THIS_WEBSITE  - Django Login Page!!"
        message2 = render_to_string('email_confirmation.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token' : generateToken.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email]
        )
        email.fail_silently = True
        email.send()

        return redirect('signin')
    return render(request, 'Loginpage/signup.html')

def signout(request):
    logout(request)
    messages.success(request, "Logout Successfully!")
    return redirect('index')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_encode(uidb64))
        myuser = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_activate = True
        myuser.save()
        login(request, myuser)
        return redirect('index')
    else:
        return render(request, 'activation_fail.html')