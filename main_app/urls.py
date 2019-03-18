from django.urls import path, include
from .views import landing, nearbyhappyhours, restaurants

urlpatterns = [
    path('', landing.home, name='home'),
    path('about/', landing.about, name='about'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup', landing.signup, name='signup'),
    path('nearby/', nearbyhappyhours.nearby, name='nearby'),
    path('happyhour/', nearbyhappyhours.happyhour_index, name='index'),
    path('happyhour/<int:happyhour_id>/', nearbyhappyhours.happyhour_detail, name='detail'),
    path('happyhour/<int:happyhour_id>/add_photo/', nearbyhappyhours.add_photo, name='add_photo'),
    path('happyhour/create/', nearbyhappyhours.HappyhourCreate.as_view(), name='happyhour_create'),
    path('happyhour/<int:pk>/update/', nearbyhappyhours.HappyhourUpdate.as_view(), name='happyhour_update'),
    path('happyhour/<int:pk>/delete/', nearbyhappyhours.HappyhourDelete.as_view(), name='happyhour_delete'),
    path('restaurants/details', restaurants.check_restaurant, name='restaurant_details'),
]