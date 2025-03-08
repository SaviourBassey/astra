from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('my-articles/', views.DashboardMyArticlesView.as_view(), name="dashboard_my_articles_view"),
    path('under-review/', views.DashboardUnderReviewView.as_view(), name="dashboard_under_review_view"),
]
