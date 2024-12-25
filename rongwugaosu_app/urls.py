from django.urls import path
from .views.login_views import LoginView

urlpatterns = [
    path('user/login', LoginView.login, name='login'),
    path('user/get_portrayal', LoginView.get_portrayal, name='get_portrayal'),

]
