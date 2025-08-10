from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from library import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    path('', views.home_view),
    path('logout/', LogoutView.as_view(template_name='library/index.html'), name='logout'),

    path('adminclick', views.adminclick_view),
    path('studentclick', views.studentclick_view),
    path('adminsignup', views.adminsignup_view),
    path('studentsignup', views.studentsignup_view),
    path('adminlogin', LoginView.as_view(template_name='library/adminlogin.html')),
    path('studentlogin', LoginView.as_view(template_name='library/studentlogin.html')),
    path('afterlogin', views.afterlogin_view),

    path('addbook', views.addbook_view, name='addbook'),
    path('viewbook', views.viewbook_view, name='viewbook'),
    path('issuebook', views.issuebook_view),
    path('viewissuedbook', views.viewissuedbook_view),
    path('viewstudent', views.viewstudent_view),
    path('viewissuedbookbystudent', views.viewissuedbookbystudent),

    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),
]
