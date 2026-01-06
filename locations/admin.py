from django.contrib import admin
from .models import Region, District, Site, ZoneASC


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'code', 'created_at']
    list_filter = ['region']
    search_fields = ['name', 'code', 'region__name']
    ordering = ['region', 'name']


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'code', 'phone', 'created_at']
    list_filter = ['district__region', 'district']
    search_fields = ['name', 'code', 'phone', 'district__name']
    ordering = ['district', 'name']


@admin.register(ZoneASC)
class ZoneASCAdmin(admin.ModelAdmin):
    list_display = ['name', 'site', 'code', 'created_at']
    list_filter = ['site']
    search_fields = ['name', 'code', 'site__name']
    ordering = ['site', 'name']
