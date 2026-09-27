"""
URL configuration for Note_markdown project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from grammer import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Feature 1: Grammar check
    path('check-grammar/', views.check_grammar, name='check_grammar'),
    path('notes/<int:id>/grammar/', views.check_note_grammar, name='check_note_grammar'),

    # Features 2 & 3: Save and List notes
    path('notes/', views.notes_list, name='notes_list'),
    path('notes/<int:id>/', views.note_detail, name='note_detail'),

    # Feature 4: Render Markdown note as HTML
    path('notes/<int:id>/render/', views.markdown_html, name='markdown_html'), 
    path('notes/<int:id>/html/', views.markdown_html, name='markdown_html_alias'),
]
