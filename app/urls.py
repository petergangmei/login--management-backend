from django.urls import path
from .views import home, login_user, get_active_sessions, logout_session, refresh_token

urlpatterns = [
    path('', home, name='home'),
    path('api/login/', login_user, name='login'),
    path('api/token/refresh/', refresh_token, name='token-refresh'),
    path('api/sessions/', get_active_sessions, name='active-sessions'),
    path('api/logout/', logout_session, name='logout-session'),
]
