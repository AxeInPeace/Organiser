from django.shortcuts import render, render_to_response
from django.contrib.auth.models import User

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout

def get_reg_form(request, signin=False):
    if signin:
        passcheck = None
        name = None
    else:
        passcheck = request.POST.get('passcheck')
        name = request.POST.get('login')


    dict = {
        'mail': request.POST.get('mail'),
        'password': request.POST.get('pass'),
        'check_pass': passcheck,
        'name': name,
    }
    return dict

def check_mail_unique(mail):
    found = User.objects.filter(email=mail)
    if len(found) == 0:
        return True
    return False

def check_pass_correct(password):
    if password.isupper() or password.islower() or password.isalpha() or password.isdigit() or len(password) < 7:
        return False
    return True

def check_double_pass(f_p, s_p):
    if f_p == s_p:
        return True
    return False

def registration(request):
    if request.method == 'GET':
        return render(request, 'registration/signup.html')
    if request.method == 'POST':
        form = get_reg_form(request)
        if (check_mail_unique(form["mail"]) and
            check_pass_correct(form["password"]) and
            check_double_pass(form["check_pass"], form["password"])):
            try:
                print(form["mail"], form["mail"], form["password"])
                new_user = User.objects.create_user(form["mail"], form["mail"], form["password"])
                new_user.last_name = form["name"]
                new_user.save()
            except:
                context = {
				    "message": "Ошибка на стороне сервера",
                    "user": None,
			    }
                return render(request, 'registration/formsended.html', context)
            context = {
                "message": "Пользователь успешно добавлен",
                "user": new_user.last_name,
            }
        else:
            context = {
                "message": "Некорректно отправленная форма, попробуйте ещё раз",
                "user": None,
            }
        return render(request, 'registration/formsended.html', context)



def signin(request):
    if request.method == 'GET':
        return render(request, 'registration/signin.html')
    if request.method == 'POST':
        form = get_reg_form(request, True)
        try:

            user = authenticate(username=form['mail'], password=form['password'])
            print (user)
        except:
            context={
                "message": "Пользователь не найден, проверьте правильность ввода логина и пароля."
            }
            return render(request, 'registration/signin.html', context)
        login(request, user)
        return HttpResponseRedirect("/")


def signout(request):
    logout(request)
    return HttpResponseRedirect("/")

def ajax_email(data):
    mail = data.GET['mail']
    return JsonResponse({ 'answer': check_mail_unique(mail)})

def ajax_pass(data):
    password = data.GET['pass']
    return JsonResponse({ 'answer': check_pass_correct(password)})

def ajax_check_pass(data):
    fp = data.GET['pass']
    sp = data.GET['passcheck']
    return JsonResponse({ 'answer': check_double_pass(fp, sp)})

