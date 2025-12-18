from django.contrib import admin
from .models import Region, District, Commune, FormationSanitaire, ZoneASC


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


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'code', 'created_at']
    list_filter = ['district__region', 'district']
    search_fields = ['name', 'code', 'district__name']
    ordering = ['district', 'name']


@admin.register(FormationSanitaire)
class FormationSanitaireAdmin(admin.ModelAdmin):
    list_display = ['name', 'commune', 'code', 'phone', 'created_at']
    list_filter = ['commune__district__region', 'commune__district', 'commune']
    search_fields = ['name', 'code', 'phone', 'commune__name']
    ordering = ['commune', 'name']


@admin.register(ZoneASC)
class ZoneASCAdmin(admin.ModelAdmin):
    list_display = ['name', 'formation_sanitaire', 'code', 'population', 'created_at']
    list_filter = ['formation_sanitaire']
    search_fields = ['name', 'code', 'formation_sanitaire__name']
    ordering = ['formation_sanitaire', 'name']
