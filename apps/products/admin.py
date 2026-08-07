from django.contrib import admin
from apps.products.models import Product, Recipe, RecipeItem, Boiler

admin.site.register(Product)
admin.site.register(Recipe)
admin.site.register(RecipeItem)
admin.site.register(Boiler)
