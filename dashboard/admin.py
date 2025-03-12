from django.contrib import admin
from .models import Article

# Register your models here.
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("author", "article_title", "publish")
    list_filter = ("publish","featured",)
admin.site.register(Article, ArticleAdmin)