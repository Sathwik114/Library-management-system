from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import forms,models
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib import auth
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.core.mail import send_mail
from librarymanagement.settings import EMAIL_HOST_USER
from datetime import date
from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.db.models import Q  # Add this import
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .models import IssuedBook, Book


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/index.html')

#for showing signup/login button for student


def book_list(request):
    books = Book.objects.all()
    books_with_index = list(enumerate(books, start=1))
    return render(request, 'book_list.html', {'books_with_index': books_with_index})

def logout_view(request):
    logout(request)
    return redirect('index')  # Change 'index' to your homepage URL name


def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/studentclick.html')

#for showing signup/login button for teacher
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/adminclick.html')



def adminsignup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()


            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)

            return HttpResponseRedirect('adminlogin')
    return render(request,'library/adminsignup.html',{'form':form})






def studentsignup_view(request):
    form1=forms.StudentUserForm()
    form2=forms.StudentExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST)
        form2=forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            user2=f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

        return HttpResponseRedirect('studentlogin')
    return render(request,'library/studentsignup.html',context=mydict)




def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

def afterlogin_view(request):
    if is_admin(request.user):
        return render(request,'library/adminafterlogin.html')
    else:
        return render(request,'library/studentafterlogin.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def addbook_view(request):
    if request.method == "POST":
        names = request.POST.getlist('name')
        editions = request.POST.getlist('edition')
        numbers = request.POST.getlist('number')
        isbns = request.POST.getlist('isbn')
        authors = request.POST.getlist('author')
        t_books = request.POST.getlist('t_book')
        racks = request.POST.getlist('rack')
        categories = request.POST.getlist('category')

        books = []
        for name, edition, number,rack, isbn, t_book, author, category in zip(names, editions, numbers, racks, isbns, t_books, authors, categories):
            try:
                t_book = int(t_book)
            except ValueError:
                t_book = 1  # Default to 1 if not valid

            if name and edition and number and isbn and rack and t_book and author and category:
                books.append(models.Book(
                    name=name,
                    edition=edition,
                    number=number,
                    isbn=isbn,
                    rack=rack,
                    t_book=t_book,
                    author=author,
                    category=category
                ))

        models.Book.objects.bulk_create(books)
        return render(request, 'library/bookadded.html')

    return render(request, 'library/addbook.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewbook_view(request):
    search_query = request.GET.get('search', '')  # Get search query from the GET request

    # Fetch books, optionally filter them based on search query
    books = models.Book.objects.all()

    # If a search query is provided, filter books based on the query
    if search_query:
        books = books.filter(
            Q(name__icontains=search_query) | 
            Q(author__icontains=search_query) | 
            Q(category__icontains=search_query) | 
            Q(isbn__icontains=search_query)
        )

    return render(request, 'library/viewbook.html', {'books': books, 'search_query': search_query})






@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def issuebook_view(request):
    form = forms.IssuedBookForm()
    if request.method == 'POST':
        form = forms.IssuedBookForm(request.POST)
        if form.is_valid():
            isbn = request.POST.get('isbn2')
            enrollment = request.POST.get('enrollment2')

            try:
                book = models.Book.objects.get(isbn=isbn)
                if book.t_book > 0:
                    # Decrease book count
                    book.t_book -= 1
                    book.save()

                    # Save issued book record
                    issued_book = models.IssuedBook(isbn=isbn, enrollment=enrollment)
                    issued_book.save()

                    messages.success(request, 'Book issued successfully!')
                    return render(request, 'library/bookissued.html')
                else:
                    messages.error(request, 'Book not available! Count is zero.')
            except models.Book.DoesNotExist:
                messages.error(request, 'Book with provided ISBN not found.')
    return render(request, 'library/issuebook.html', {'form': form})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewissuedbook_view(request):
    issuedbooks=models.IssuedBook.objects.all()
    li=[]
    for ib in issuedbooks:
        issdate=str(ib.issuedate.day)+'-'+str(ib.issuedate.month)+'-'+str(ib.issuedate.year)
        expdate=str(ib.expirydate.day)+'-'+str(ib.expirydate.month)+'-'+str(ib.expirydate.year)
        #fine calculation
        days=(date.today()-ib.issuedate)
        print(date.today())
        d=days.days
        fine=0
        if d>15:
            day=d-15
            fine=day*10


        books=list(models.Book.objects.filter(isbn=ib.isbn))
        students=list(models.StudentExtra.objects.filter(enrollment=ib.enrollment))
        i=0
        for l in books:
            t=(students[i].get_name,students[i].enrollment,books[i].name,books[i].author,issdate,expdate,fine)
            i=i+1
            li.append(t)

    return render(request,'library/viewissuedbook.html',{'li':li})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewstudent_view(request):
    students=models.StudentExtra.objects.all()
    return render(request,'library/viewstudent.html',{'students':students})


@login_required(login_url='studentlogin')
def viewissuedbookbystudent(request):
    try:
        student = models.StudentExtra.objects.get(user_id=request.user.id)
    except models.StudentExtra.DoesNotExist:
        return render(request, 'library/viewissuedbookbystudent.html', {
            'li1': [],
            'li2': [],
            'error': 'Student profile not found. Please contact admin.'
        })

    issuedbooks = models.IssuedBook.objects.filter(enrollment=student.enrollment)

    li1 = []
    li2 = []

    for ib in issuedbooks:
        books = models.Book.objects.filter(isbn=ib.isbn)
        for book in books:
            t = (request.user, student.enrollment, student.branch, book.name, book.author)
            li1.append(t)

        # Format dates
        issdate = ib.issuedate.strftime('%d-%m-%Y')
        expdate = ib.expirydate.strftime('%d-%m-%Y')

        # Fine calculation
        days_diff = (date.today() - ib.issuedate).days
        fine = max(0, (days_diff - 15) * 10)

        t = (issdate, expdate, fine)
        li2.append(t)

    return render(request, 'library/viewissuedbookbystudent.html', {
        'li1': li1,
        'li2': li2
    })

def aboutus_view(request):
    return render(request,'library/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message, EMAIL_HOST_USER, ['wapka1503@gmail.com'], fail_silently = False)
            return render(request, 'library/contactussuccess.html')
    return render(request, 'library/contactus.html', {'form':sub})
