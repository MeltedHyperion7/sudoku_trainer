from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'solver/$', views.solver, name='solver'),
    url(r'engine/$', views.SudokuEngineView.as_view(), name='engine')
]