from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from ckeditor.fields import RichTextField
from django.utils import timezone
from supabase import create_client
from decouple import config
import time

# Create your models here.


class Volume(models.Model):
    number = models.PositiveIntegerField(help_text="Volume number")
    year = models.PositiveIntegerField(help_text="e.g., 2025")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Volume {self.number}, {self.year}"
    

class Issue(models.Model):
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE, related_name="issues")
    number = models.PositiveIntegerField(help_text="Issue number")
    month = models.CharField(max_length=20, help_text="e.g., 'March', 'May'")
    publish_date = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Issue {self.number}, {self.month}, {self.volume}"


class Journal(models.Model):
    journal_name = models.CharField(max_length=1000)
    journal_slug = models.SlugField(unique=True, blank=True, null=True, help_text="Leave blank to auto-populate")
    journal_abbreviation = models.CharField(max_length=1000, help_text="e.g: IJPRSS")
    journal_ISSN = models.CharField(max_length=1000)
    journal_cover = CloudinaryField('image')
    journal_description = RichTextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.journal_name
    
    def save(self, *args, **kwargs):
        if not self.journal_slug:
            self.journal_slug = slugify(self.journal_name)
        super().save(*args, **kwargs)


class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    journal_category = models.ForeignKey(Journal, blank=True, null=True, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="articles", null=True, blank=True)
    article_title = models.CharField(max_length=1000)
    article_slug = models.SlugField(max_length=1000, unique=True, blank=True, null=True, help_text="Leave blank to auto-populate")
    co_authors = models.CharField(max_length=1000, blank=True, null=True, help_text="seprate each co-authors with comma")
    article_keywords = models.CharField(max_length=1000, help_text="seprate each keywords with comma")
    article_DOI = models.CharField(max_length=1000, blank=True, null=True)
    article_abstract = models.TextField()
    article_file_url = models.URLField(blank=True, null=True)
    article_file_size = models.PositiveIntegerField(blank=True, null=True, help_text="File size in bytes", editable=False)
    article_file = models.FileField(upload_to="articles/", blank=True, null=True)
    # article_volume = models.ForeignKey(Volume, blank=True, null=True, on_delete=models.CASCADE)
    publish = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(blank=True, null=True, help_text="Leave blank to auto-populate")

    def __str__(self):
        return self.article_title
    
    def abstract_snippet(self):
        if len(self.article_abstract) > 260:
            return self.article_abstract[:260] + "..."
        else:
            return self.article_abstract
        
    def get_upload_filename(self):
        slug = self.article_slug or generate_unique_slug(self.article_title)
        return f"articles/{slug}.pdf"
    
    def save(self, *args, **kwargs):
        print("Started")
        is_new = not self.pk
        old_file_name = None

        if not is_new:
            try:
                old_instance = Article.objects.get(pk=self.pk)
                if old_instance.article_file:
                    old_file_name = old_instance.article_file.name
            except Article.DoesNotExist:
                pass

        # Handle published_at timestamp
        if self.pk:
            orig = Article.objects.get(pk=self.pk)
            if not orig.publish and self.publish:
                self.published_at = timezone.now()
        else:
            if self.publish:
                self.published_at = timezone.now()

        # Generate slug if missing
        if not self.article_slug:
            self.article_slug = generate_unique_slug(self.article_title)

        # ✅ Upload only if file is new OR changed
        if self.article_file and hasattr(self.article_file, 'file'):
            if is_new or self.article_file.name != old_file_name:
                if self.article_file.name.endswith(".pdf"):
                    self.article_file.seek(0)
                    self.article_file_size = self.article_file.size

                    supabase_url = config('SUPABASE_URL')
                    supabase_key = config('SUPABASE_KEY')
                    supabase = create_client(supabase_url, supabase_key)

                    file_content = self.article_file.read()
                    file_name = f"{self.article_slug}.pdf"
                    path = f"articles/{file_name}"

                    try:
                        response = supabase.storage.from_("astra-bucket").upload(
                            path=path,
                            file=file_content,
                            file_options={
                                "cache-control": "3600",
                                "upsert": "true",  # only overwrite if update
                                "content-type": "application/pdf"
                            }
                        )
                    except Exception as e:
                        raise ValueError(f"Supabase upload failed: {e}")

                    # Refresh cache-buster every upload
                    public_url = supabase.storage.from_("astra-bucket").get_public_url(path)
                    cache_buster = int(time.time())
                    self.article_file_url = f"{public_url}?v={cache_buster}"

                    self.article_file = None  # don’t save locally
                else:
                    self.article_file = None

        super().save(*args, **kwargs)

        


def generate_unique_slug(title):
    base_slug = slugify(title)
    unique_slug = base_slug
    counter = 1
    while Article.objects.filter(article_slug=unique_slug).exists():
        unique_slug = f"{base_slug}-{counter}"
        counter += 1
    return unique_slug