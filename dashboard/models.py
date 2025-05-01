from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from ckeditor.fields import RichTextField
import cloudinary.uploader
import re
from home.imagekitconfig import imagekit
import os
from django.core.files.base import ContentFile

# Create your models here.


def slugify_filename(title):
    """Convert title to a clean filename (good for SEO)."""
    return re.sub(r'[^a-zA-Z0-9-_]', '-', title).lower()


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
    article_DOI = models.CharField(max_length=1000, blank=True, null=True)
    article_abstract = models.TextField()
    article_file_url = models.URLField(blank=True, null=True)
    article_file_size = models.PositiveIntegerField(blank=True, null=True, help_text="File size in bytes", editable=False)
    article_file = models.FileField(upload_to="articles/", blank=True, null=True)
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

    #    # Only upload if a new file is provided
    #     if self.article_file and hasattr(self.article_file, 'file'):
    #         print("HERE 1")
    #         file_extension = os.path.splitext(self.article_file.name)[1]
    #         safe_file_name = f"{self.article_title.replace(' ', '_').lower()}{file_extension}"


    #          # ✅ Read the file as binary and upload to ImageKit
    #         self.article_file.seek(0)  # Reset pointer to start
    #         file_content = self.article_file.read()  # Read file bytes

    #         # ✅ Use ContentFile to create a file-like object for ImageKit
    #         django_file = ContentFile(file_content, name=safe_file_name)

    #         upload = imagekit.upload_file(
    #             file=django_file.file,  # ✅ Pass a file-like object, not raw bytes
    #             file_name=safe_file_name,
    #         )

    #         # ✅ Retrieve the uploaded file URL and size
    #         url = upload.response_metadata.raw["url"]


            # print("Uploaded file URL:", url)

        super().save(*args, **kwargs)


