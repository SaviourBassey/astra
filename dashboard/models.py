from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.

JOURNAL_CAT = (
      ("Global Journal of Modern Research and Emerging Trends (GJ-MRET)","Global Journal of Modern Research and Emerging Trends (GJ-MRET)"),
      ("International journal of public relations and social sciences (IJPRSS)","International journal of public relations and social sciences (IJPRSS)"),
)

class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    article_title = models.CharField(max_length=1000)
    article_slug = models.SlugField(unique=True, blank=True, null=True)
    journal_category = models.CharField(max_length=1000, choices=JOURNAL_CAT, blank=True, null=True)
    co_authors = models.CharField(max_length=1000, blank=True, null=True)
    article_keywords = models.CharField(max_length=1000)
    article_abstract = models.TextField()
    article_file = models.FileField(upload_to="articles")
    publish = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article_title
    
    def abstract_snippet(self):
        if len(self.article_abstract) > 260:
            return self.article_abstract[:260] + "..."
        else:
            return self.article_abstract
        
    def save(self, *args, **kwargs):
        if not self.article_slug:
            self.article_slug = slugify(self.article_title)
        super().save(*args, **kwargs)

