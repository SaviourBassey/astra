from django.contrib import admin
from .models import Article, Journal, Volume, Issue

# Register your models here.
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("author", "article_title", "publish")
    list_filter = ("publish","featured",)
admin.site.register(Article, ArticleAdmin)


admin.site.register(Journal)

admin.site.register(Volume)

admin.site.register(Issue)