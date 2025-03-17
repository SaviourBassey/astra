from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path('', views.HomeView.as_view(), name="home_view"),
    path('about-us/', views.AboutView.as_view(), name="about_view"),
    path('publication-policies/', views.PublicationPoliciesView.as_view(), name="publication_policies_view"),
    path('editorial-board/', views.EditorialBoardView.as_view(), name="editorial_board_view"),
    path('articles/all-articles/', views.ArticleListView.as_view(), name="all_articles_view"),
    path('articles/submit-article/', views.SubmitArticleView.as_view(), name="submit_article_view"),
    path('articles/<str:SLUG>/', views.ArticleDetailView.as_view(), name="article_detail_view"),
    path('journals/<str:SLUG>/', views.JournalDetailView.as_view(), name="journal_detail_view"),
]
