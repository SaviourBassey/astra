from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Article


# Create your views here.


class DashboardMyArticlesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        author_article = Article.objects.filter(author=request.user, publish=True).order_by("-timestamp")
        context = {
            "author_article":author_article
        }
        return render(request, "dashboard/aticle-list.html", context)


class DashboardUnderReviewView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        author_article_under_review = Article.objects.filter(author=request.user, publish=False).order_by("-timestamp")
        context = {
            "author_article_under_review":author_article_under_review
        }
        return render(request, "dashboard/underreview.html", context)
    
    
