from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from ckeditor.fields import RichTextField

# Create your models here.

JOURNAL_CAT = (
      ("Global Journal of Modern Research and Emerging Trends (GJ-MRET)","Global Journal of Modern Research and Emerging Trends (GJ-MRET)"),
      ("International journal of public relations and social sciences (IJPRSS)","International journal of public relations and social sciences (IJPRSS)"),
)

class Journal(models.Model):
    journal_name = models.CharField(max_length=1000)
    journal_slug = models.SlugField(unique=True, blank=True, null=True, help_text="Leave blank to auto-populate")
    journal_abbreviation = models.CharField(max_length=1000, help_text="e.g: IJPRSS")
    journal_cover = CloudinaryField('image')
    journal_description = RichTextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.journal_name
    
    def save(self, *args, **kwargs):
        if not self.journal_slug:
            self.journal_slug = slugify(self.journal_name)
        super().save(*args, **kwargs)
    

class Volume(models.Model):
    volume = models.CharField(max_length=1000, help_text="e.g: vol. 1")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.volume


class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    article_title = models.CharField(max_length=1000)
    article_slug = models.SlugField(unique=True, blank=True, null=True, help_text="Leave blank to auto-populate")
    journal_category = models.ForeignKey(Journal, blank=True, null=True, on_delete=models.CASCADE)
    co_authors = models.CharField(max_length=1000, blank=True, null=True, help_text="seprate each co-authors with comma")
    article_keywords = models.CharField(max_length=1000, help_text="seprate each keywords with comma")
    article_abstract = models.TextField()
    #article_file = models.FileField(upload_to="articles")
    article_file = CloudinaryField('file', resource_type='raw')
    article_volume = models.ForeignKey(Volume, blank=True, null=True, on_delete=models.CASCADE)
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

