from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.models import Article, Journal
from .imagekitconfig import imagekit
import os
import cloudinary.uploader
from collections import defaultdict

# Create your views here.

class HomeView(View):
    def get(self, request, *args, **kwargs):
        featured_article = Article.objects.filter(featured=True, publish=True).order_by("-timestamp")
        print(featured_article)

        # Split the articles into chunks of 3
        grouped_features_articles = [featured_article[i:i+3] for i in range(0, len(featured_article), 3)]

        all_journals = Journal.objects.all().order_by("-timestamp")


        # Code to group by year of issue
        articles = Article.objects.select_related('issue__volume').filter(publish=True).order_by('-timestamp')
    
        grouped_articles = defaultdict(list)

        for article in articles:
            if article.issue and article.issue.volume:
                year = article.issue.volume.year
                if len(grouped_articles[year]) < 10:
                    grouped_articles[year].append(article)

        # Sort years descending
        grouped_articles = dict(sorted(grouped_articles.items(), reverse=True))

        context = {
            "grouped_features_articles":grouped_features_articles,
            "all_journals":all_journals,
            'grouped_articles': grouped_articles
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
        else:
            all_article = Article.objects.filter(publish=True).order_by("-timestamp")

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
    

class JournalDetailView(View):
    def get(self, request, SLUG, *args, **kwargs):
        journal = Journal.objects.get(journal_slug=SLUG)
        related_articles = Article.objects.filter(journal_category=journal.id).order_by("-timestamp")[:3]
        context = {
            "related_articles":related_articles,
            "journal":journal
        }
        return render(request, "home/journal-detail.html", context)
    

class SubmitArticleView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        all_journals = Journal.objects.all().order_by("journal_name")
        context = {
            "all_journals": all_journals
        }
        return render(request, "home/submitarticle.html", context)
    
    def post(self, request, *args, **kwargs):
        article_title = request.POST.get("article_title")
        journal_cat_id = int(request.POST.get("journal_cat_id"))
        co_authors = request.POST.get("co_authors")
        article_keywords = request.POST.get("article_keywords")
        article_abstract = request.POST.get("article_abstract")
        article_file = request.FILES.get("article_file")

        # Ensure the journal category exists
        journal_id = Journal.objects.filter(id=journal_cat_id).first()

        file_url = None
        imagekit_url = None
        file_size = 0

        if article_file:
            file_extension = os.path.splitext(article_file.name)[1]
            safe_file_name = f"{article_title.replace(' ', '_').lower()}{file_extension}"

            # ✅ Read the file correctly using Django's file handling methods
            article_file.seek(0)  # Ensure the file pointer is at the beginning
            file_content = article_file.read()

            # ✅ Upload to ImageKit
            upload = imagekit.upload_file(
                file=file_content,  # ✅ Pass binary content, NOT a file path
                file_name=safe_file_name,
            )

            # ✅ Retrieve the uploaded file URL
            url = upload.response_metadata.raw["url"]
            print("Uploaded file URL:", url)

        # 🔹 Step 4: Save Article
        Article.objects.create(
            author=request.user,
            article_title=article_title,
            journal_category=journal_id,
            co_authors=co_authors,
            article_keywords=article_keywords,
            article_abstract=article_abstract,
            article_file=None,  # Save Cloudinary URL
            article_file_url=url,  # Save ImageKit URL
            article_file_size=file_size,  # Save file size in bytes
        )

        return redirect("dashboard:dashboard_under_review_view")
    


class PublicationPoliciesView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "home/publication_policies.html")
    
    
class EditorialBoardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "home/editorial_board.html")
    
    