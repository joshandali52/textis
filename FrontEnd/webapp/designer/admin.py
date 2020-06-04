from django.contrib import admin

# Register your models here.
from designer.models import Profile, taskProperty


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'IsUser', 'CreatedAt', 'LastModified')
    search_fields = ['IsUser__username']

admin.site.register(Profile, ProfileAdmin)


class taskPropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'Name', 'Form', 'IsChecked', 'Owner', 'CreatedAt')
    search_fields = ['Name']

admin.site.register(taskProperty, taskPropertyAdmin)