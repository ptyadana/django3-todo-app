from django.contrib import admin
from .models import Todo

#to make read only fields to be avaliable in Admin portal
class TodoAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date',)

# Register your models here.
admin.site.register(Todo,TodoAdmin)
