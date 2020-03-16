from django.shortcuts import render,redirect,get_object_or_404

#django built in user creation form / Log in
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

#django built in user model
from django.contrib.auth.models import User

#for existing username error to catch
from django.db import IntegrityError

#for user to keep log in after created a new user/ log out function / Authenticate
from django.contrib.auth import login,logout,authenticate

#for custom form model
from .forms import TodoForm

#to show todo lists
from .models import Todo

#for complete to do date
from django.utils import timezone

#use for making function to be avaliable only if user is logged in
from django.contrib.auth.decorators import login_required


#404 erro
# def handler404(request):
#     return render(request, 'todo_app/404.html', status=404)

#home page
def home(request):
    return render(request,'todo_app/home.html')

#sign up new user
def signupuser(request):
    if request.method == "GET":
        my_dict = {"form":UserCreationForm()}
        return render(request, "todo_app/signupuser.html",my_dict)
    else:
        #create new user
        username = request.POST["username"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 == password2:
            try:
               user = User.objects.create_user(username=username,password=password1)
               user.save()

               login(request,user)
               return redirect('currenttodos')

            except IntegrityError:
                #username already taken
                error_msg = 'Username is already taken. Please choose a different Username.'
                my_dict = {"form":UserCreationForm(),'error':error_msg}  
                return render(request, "todo_app/signupuser.html",my_dict)   
        else:
             #password didn't match
             error_msg = 'Password did not match.'
             my_dict = {"form":UserCreationForm(),'error':error_msg}  
             return render(request, "todo_app/signupuser.html",my_dict)


#log in user
def loginuser(request):
    if request.method == "GET":
        my_dict = {"form":AuthenticationForm()}
        return render(request, "todo_app/login.html",my_dict)
    else:
        #check username and password
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request,username=username,password=password)

        #invalid user
        if user == None:
            error_msg = 'Invalid Username and Password'
            my_dict = {"form":AuthenticationForm(),'error':error_msg}  
            return render(request, "todo_app/login.html",my_dict)
        else:
            #username and password are ok
            login(request,user)
            return redirect('currenttodos')
               

#log out user
@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


#create new todo
@login_required
def createtodos(request):
    if request.method == "GET":
        my_dict = {"form":TodoForm()}
        return render(request, "todo_app/createtodos.html",my_dict)
    else:
        try:
            form = TodoForm(request.POST)
        
            #don't save the info to DB yes as userid need to be added
            new_todo = form.save(commit=False)

            #add user
            new_todo.user = request.user

            new_todo.save()
            return redirect('currenttodos')

        except ValueError:
            error_msg = 'There is something wrong with the data. Please try again.'
            my_dict = {"form":TodoForm(),'error':error_msg}

            return render(request,'todo_app/createtodos.html',my_dict)


#list existing todos
@login_required
def currenttodos(request):
    todo_list = Todo.objects.filter(user=request.user,completed_date__isnull=True)

    my_dict = {'todo_list':todo_list}
    return render(request,'todo_app/currenttodos.html',my_dict)


#list completed todos
@login_required
def completedtodos(request):
    todo_list = Todo.objects.filter(user=request.user,completed_date__isnull=False).order_by('-completed_date')

    my_dict = {'todo_list':todo_list}
    return render(request,'todo_app/completedtodos.html',my_dict)


#view details of todo
@login_required
def viewtodo(request,todo_pk):
    todo = get_object_or_404(Todo,pk=todo_pk,user=request.user)

    if request.method == 'GET':
        #get the instance of todo as TodoForm object       
        form = TodoForm(instance=todo)
        #pass it to display
        my_dict = {'todo':todo, 'form':form}
        return render(request,'todo_app/viewtodo.html',my_dict)
    else:
        try:
            form = TodoForm(request.POST,instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            error_msg = 'There is something wrong with the data. Please try again.'
            my_dict = {"form":TodoForm(),'error':error_msg}

            return render(request,'todo_app/viewtodo.html',my_dict)


#complete the to do item
@login_required
def completetodo(request,todo_pk):
    todo = get_object_or_404(Todo,pk=todo_pk,user=request.user)

    if request.method == 'POST':
        todo.completed_date = timezone.now();
        todo.save()
        return redirect('currenttodos')


#delete to do item
@login_required
def deletetodo(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')
