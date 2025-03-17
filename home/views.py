from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.models import Article

# Create your views here.

class HomeView(View):
    def get(self, request, *args, **kwargs):
        featured_article = Article.objects.filter(featured=True).order_by("-timestamp")

        # Split the articles into chunks of 3
        grouped_features_articles = [featured_article[i:i+3] for i in range(0, len(featured_article), 3)]

        context = {
            "grouped_features_articles":grouped_features_articles
        }
        return render(request, "home/index.html", context)
    

class AboutView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "home/aboutus.html")
    

class ArticleListView(View):
    def get(self, request, *args, **kwargs):
        filter_kwargs = {}

        # Loop through query parameters and add non-empty values to filter_kwargs
        for key, value in request.GET.items():
            if value:  # Only add non-empty parameters
                filter_kwargs[key] = value

        # Apply filters only if there are any filtering conditions
        if filter_kwargs:
            all_article = Article.objects.filter(**filter_kwargs).filter(publish=True).order_by("-timestamp")
            print("HERE 1")
        else:
            all_article = Article.objects.filter(publish=True).order_by("-timestamp")
            print("HERE 2")

        print(all_article)
        context = {
            "all_article":all_article
        }
        return render(request, "home/articles.html", context)
    

class ArticleDetailView(View):
    def get(self, request, SLUG, *args, **kwargs):
        try:
            article = Article.objects.get(article_slug=SLUG)
            related_articles = Article.objects.filter(journal_category=article.journal_category).exclude(id=article.id).order_by("-timestamp")[:3]
        except:
            article = None
            related_articles = None
        context = {
            "article":article,
            "related_articles":related_articles
        }
        return render(request, "home/articledetail.html", context)
    

class JournalListView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "home/index.html")
    

class SubmitArticleView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "home/submitarticle.html")
    
    def post(self, request, *args, **kwargs):
        article_title = request.POST.get("article_title")
        journal_cat = request.POST.get("journal_cat")
        co_authors = request.POST.get("co_authors")
        article_keywords = request.POST.get("article_keywords")
        article_abstract = request.POST.get("article_abstract")
        article_file = request.FILES.get("article_file")

        Article.objects.create(
            author = request.user,
            article_title = article_title,
            journal_category = journal_cat,
            co_authors = co_authors,
            article_keywords = article_keywords,
            article_abstract = article_abstract,
            article_file = article_file
        )
        return redirect("dashboard:dashboard_under_review_view")
    


class PublicationPoliciesView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "home/publication_policies.html")
    
    
class EditorialBoardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "home/editorial_board.html")
    

class GjmretView(View):
    def get(self, request, *args, **kwargs):
        related_articles = Article.objects.filter(journal_category="Global Journal of Modern Research and Emerging Trends (GJ-MRET)").order_by("-timestamp")[:3]
        context = {
            "related_articles":related_articles
        }
        return render(request, "home/gjmret.html", context)
    

class IjprssView(View):
    def get(self, request, *args, **kwargs):
        related_articles = Article.objects.filter(journal_category="International journal of public relations and social sciences (IJPRSS)").order_by("-timestamp")[:3]
        context = {
            "related_articles":related_articles
        }
        return render(request, "home/ijprss.html", context)