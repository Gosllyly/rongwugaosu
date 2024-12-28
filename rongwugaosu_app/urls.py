from django.urls import path

from .views import SimulateView
from .views.login_views import LoginView

urlpatterns = [
    path('user/login', LoginView.login, name='login'),
    path('user/get_portrayal', LoginView.get_portrayal, name='get_portrayal'),
    path('simulate/start_emulate', SimulateView.start_emulate, name='start_emulate'),

]
