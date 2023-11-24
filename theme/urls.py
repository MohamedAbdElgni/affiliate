from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('php-scripts/php-scripts', views.php_scripts, name='php_scripts'),
    path('detail/<slug:slug>', views.script_detail, name='detail'),
    path('result/', views.search_view, name='search'),
    path('pages/<int:page>', views.search_in_pages, name='search_in_pages'),
    path('<str:cat>/<str:sub_cat>', views.main_category, name='main_category'),
    path('<str:cat>/<str:sub_cat>/<int:page>', views.main_category_in_pages, name='main_category_in_pages'),
    path('php-scripts/<str:cats>', views.category_list, name='category_list'),
    path('page404/', views.page404, name='page404'),
    path('privacy/', views.privacy, name='privacy'),
    path('download/', views.download, name='download'),
    path('dmca/', views.dmca, name='dmca'),
]
