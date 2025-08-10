from django.db import models
from django.contrib.auth.models import User
from datetime import datetime,timedelta

class StudentExtra(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    enrollment = models.CharField(max_length=40)
    branch = models.CharField(max_length=40)
    #used in issue book
    def __str__(self):
        return self.user.first_name+'['+str(self.enrollment)+']'
    @property
    def get_name(self):
        return self.user.first_name
    @property
    def getuserid(self):
        return self.user.id



class Book(models.Model):
    # Choices for book category
    catchoice = [
        ('education', 'Education'),
        ('entertainment', 'Entertainment'),
        ('comics', 'Comics'),
        ('biography', 'Biography'),
        ('history', 'History'),
        ('novel', 'Novel'),
        ('fantasy', 'Fantasy'),
        ('thriller', 'Thriller'),
        ('romance', 'Romance'),
        ('scifi', 'Sci-Fi')
    ]

    name = models.CharField(max_length=30)
    edition = models.CharField(max_length=20)
    isbn = models.CharField(max_length=20)
    number = models.CharField(max_length=20) 
    author = models.CharField(max_length=40)
    t_book=models.IntegerField(default=1) 
    rack = models.CharField(max_length=20, default=1) 
    category = models.CharField(max_length=30, choices=catchoice, default='education')

    def __str__(self):
        # String representation without index (index is dynamic in view/template)
        return f"{self.name} [{self.isbn}]"



def get_expiry():
    return datetime.today() + timedelta(days=15)
class IssuedBook(models.Model):
    #moved this in forms.py
    #enrollment=[(student.enrollment,str(student.get_name)+' ['+str(student.enrollment)+']') for student in StudentExtra.objects.all()]
    enrollment=models.CharField(max_length=30)
    #isbn=[(str(book.isbn),book.name+' ['+str(book.isbn)+']') for book in Book.objects.all()]
    isbn=models.CharField(max_length=30)
    issuedate=models.DateField(auto_now=True)
    expirydate=models.DateField(default=get_expiry)
    def __str__(self):
        return self.enrollment
