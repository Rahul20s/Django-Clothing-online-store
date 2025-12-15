from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('chat-widget/', views.chat_widget, name='chat_widget'),
    path('send-message/', views.send_message, name='send_message'),
]
