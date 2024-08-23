from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from .models import Profile
from quiz.models import QuizSubmission


# Create your views here.



def register(request):
    if request.user.is_authenticated:
        return redirect('profile', request.user.username)


    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            # check if email is not same
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Already Used. Try to Login.")
                return redirect('register')
            
            # check if username is not same
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username Already Taken.")
                return redirect('register')
            
            else:
                # create user
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # log in the user and redirect to profile
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)


                # create profile for new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model)
                new_profile.save()
                return redirect('profile', username)
        else:
            messages.info(request, "Password Not Matching.")
            return redirect('register')

    context = {}
    return render(request, "register.html", context)

@login_required
def profile(request, username):

    # profile user
    user_object2 = get_object_or_404(User, username=username)
    user_profile2 = get_object_or_404(Profile, user=user_object2)

    submissions = QuizSubmission.objects.filter(user=user_object2)

    context = {"user_profile2": user_profile2, "submissions":submissions}
    return render(request, "profile.html", context)

@login_required
def editProfile(request):

    user_object = request.user
    user_profile = request.user.profile

    if request.method == "POST":
        # Image
        if request.FILES.get('profile_img') is not None:
            user_profile.profile_img = request.FILES.get('profile_img')
            user_profile.save()

        # Email
        if request.POST.get('email') is not None:
            email = request.POST.get('email')
            if email != user_object.email:  # Only check if email is different
                if User.objects.filter(email=email).exclude(id=user_object.id).exists():
                    messages.info(request, "Email already used by another user, choose a different one!")
                    return redirect('edit_profile')
                else:
                    user_object.email = email
                    user_object.save()

        # Username
        if request.POST.get('username') is not None:
            username = request.POST.get('username')
            users_with_username = User.objects.filter(username=username).exclude(id=user_object.id)

            if not users_with_username.exists():
                user_object.username = username
                user_object.save()
            else:
                messages.info(request, "Username already taken by another user, choose a unique one!")
                return redirect('edit_profile')

        # Firstname and Lastname
        user_object.first_name = request.POST.get('firstname')
        user_object.last_name = request.POST.get('lastname')
        user_object.save()

        # Location, Bio, Gender
        user_profile.location = request.POST.get('location')
        user_profile.gender = request.POST.get('gender')
        user_profile.bio = request.POST.get('bio')
        user_profile.save()

        return redirect('profile', user_object.username)

    context = {"user_profile": user_profile}
    return render(request, 'profile-edit.html', context)


@login_required
def deleteProfile(request):

    user_object = request.user
    user_profile = request.user.profile

    if request.method == "POST":
        user_profile.delete()
        user_object.delete()
        return redirect('logout')

    return render(request, 'confirm.html')


def login(request):
    if request.user.is_authenticated:
        return redirect('profile', request.user.username)

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('profile', username)
        else:
            messages.info(request, 'Credentials Invalid!')
            return redirect('login')

    return render(request, "login.html")

@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')