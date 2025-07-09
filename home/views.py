from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.models import Article, Journal,  Volume, Issue
from supabase import create_client, Client
from decouple import config
from django.utils.text import slugify
import time
from django.contrib import messages
from collections import defaultdict



# Create your views here.

def generate_unique_slug(title):
    base_slug = slugify(title)
    unique_slug = base_slug
    counter = 1
    while Article.objects.filter(article_slug=unique_slug).exists():
        unique_slug = f"{base_slug}-{counter}"
        counter += 1
    return unique_slug


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

        journals = Journal.objects.all()
        volumes = Volume.objects.all()
        issues = Issue.objects.all()
        

        # Get filter values from request
        search_query = request.GET.get('search', '')
        journal_id = request.GET.get('journal')
        volume_id = request.GET.get('volume')
        issue_id = request.GET.get('issue')
        year = request.GET.get('year')
        submit = request.GET.get('submit')

        # Start with all articles
        articles = Article.objects.select_related('journal_category', 'issue__volume').filter(publish=True)

        if submit == "reset":
            return redirect("home:all_articles_view")

        # Apply filters
        if search_query:
            articles = articles.filter(article_title__icontains=search_query)
        if journal_id:
            articles = articles.filter(journal_category__id=journal_id)
        if volume_id:
            articles = articles.filter(issue__volume__id=volume_id)
        if issue_id:
            articles = articles.filter(issue__id=issue_id)
        if year:
            articles = articles.filter(issue__volume__year=year)


        context = {
            "all_article":articles,
            'journals': journals,
            'volumes': volumes,
            'issues': issues,
        }


        context = {
            'all_article': articles.distinct(),
            'journals': journals,
            'volumes': volumes,
            'issues': issues,
            'selected': {
                'journal': journal_id,
                'volume': volume_id,
                'issue': issue_id,
                'year': year,
                "query": search_query
            }
        }
        return render(request, "home/articles.html", context)
    

class ArticleDetailView(View):
    def get(self, request, SLUG, *args, **kwargs):
        try:
            article = Article.objects.get(article_slug=SLUG)
            co_author_list = (article.co_authors).split(",")
            print(co_author_list)
            related_articles = Article.objects.filter(journal_category=article.journal_category).exclude(id=article.id).order_by("-timestamp")[:3]
        except:
            article = None
            co_author_list = None
            related_articles = None
        context = {
            "article":article,
            "co_author_list":co_author_list,
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
        try:
            journal_cat_id = int(request.POST.get("journal_cat_id"))
            journal_category = Journal.objects.filter(id=journal_cat_id).first()
        except (ValueError, TypeError):
            journal_category = None

        co_authors = request.POST.get("co_authors", "").strip()
        article_keywords = request.POST.get("article_keywords", "").strip()
        article_abstract = request.POST.get("article_abstract", "").strip()
        article_file = request.FILES.get("article_file")

        # 🔒 Validate file
        if not article_file or article_file.content_type != 'application/pdf':
            print("HERE")
            messages.error(request, "Only PDF files are allowed.")
            return redirect("home:submit_article_view")

        # 🔄 Generate unique file name
        file_name = generate_unique_slug(article_title) + ".pdf"
        path = f"articles/{file_name}"

        # 📡 Connect to Supabase
        supabase_url = config('SUPABASE_URL')
        supabase_key = config('SUPABASE_KEY')
        supabase: Client = create_client(supabase_url, supabase_key)

        try:
            file_content = article_file.read()
            # 📤 Upload the file
            response = supabase.storage.from_("astra-bucket").upload(
                file=file_content,
                path=path,
                file_options={
                    "cache-control": "3600",
                    "upsert": "false",
                    "content-type": "application/pdf"
                }
            )

            # 🌍 Get public URL with cache busting
            public_url = supabase.storage.from_("astra-bucket").get_public_url(path)
            public_url += f"?v={int(time.time())}"

            # 📏 Get file size in bytes
            article_file_size = article_file.size

            # 📝 Create the article
            Article.objects.create(
                author=request.user,
                article_title=article_title,
                journal_category=journal_category,
                co_authors=co_authors,
                article_keywords=article_keywords,
                article_abstract=article_abstract,
                article_file=None,  # Prevent local storage
                article_file_url=public_url,
                article_file_size=article_file_size,
            )

            messages.success(request, "Article submitted successfully.")
            return redirect("dashboard:dashboard_under_review_view")

        except Exception as e:
            print("Error during article upload:", e)
            messages.error(request, "An unexpected error occurred.")
            return redirect("home:submit_article_view")

    


class PublicationPoliciesView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "home/publication_policies.html")
    
    
class EditorialBoardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "home/editorial_board.html")
    
    