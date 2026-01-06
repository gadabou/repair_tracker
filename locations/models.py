from django.db import models


class Region(models.Model):
    """Région administrative"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Région"
        verbose_name_plural = "Régions"
        ordering = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    """District sanitaire"""
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100, verbose_name="Nom")
    code = models.CharField(max_length=20, verbose_name="Code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"
        ordering = ['region', 'name']
        unique_together = ['region', 'code']

    def __str__(self):
        return f"{self.name} ({self.region.name})"


class Commune(models.Model):
    """Commune"""
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='communes')
    name = models.CharField(max_length=100, verbose_name="Nom")
    code = models.CharField(max_length=20, verbose_name="Code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commune"
        verbose_name_plural = "Communes"
        ordering = ['district', 'name']
        unique_together = ['district', 'code']

    def __str__(self):
        return f"{self.name} ({self.district.name})"


class Site(models.Model):
    """Site (Centre de santé)"""
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=150, verbose_name="Nom")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    address = models.TextField(blank=True, verbose_name="Adresse")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site"
        verbose_name_plural = "Sites"
        ordering = ['commune', 'name']

    def __str__(self):
        return f"{self.name} ({self.commune.name})"

    @property
    def district(self):
        return self.commune.district

    @property
    def region(self):
        return self.commune.district.region


class ZoneASC(models.Model):
    """Zone d'intervention d'un ASC"""
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name='zones_asc'
    )
    name = models.CharField(max_length=100, verbose_name="Nom de la zone")
    code = models.CharField(max_length=20, verbose_name="Code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Zone ASC"
        verbose_name_plural = "Zones ASC"
        ordering = ['site', 'name']
        unique_together = ['site', 'code']

    def __str__(self):
        return f"{self.name} ({self.site.name})"
