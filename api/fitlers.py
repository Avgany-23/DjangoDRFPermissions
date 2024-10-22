from django_filters import rest_framework as filters
from .models import Advertisement
from datetime import timedelta


class AdvertisementFilter(filters.FilterSet):
    """Фильтры для объявлений."""

    created_at = filters.DateTimeFilter(field_name="created_at")

    class Meta:
        model = Advertisement
        fields = ['status', 'created_at']

    def filter_queryset(self, queryset):
        created_at_value = self.request.query_params.get('created_at')
        if created_at_value is not None:
            result = []
            for d in queryset:
                if (d.created_at + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S') == created_at_value:
                    result.append(d)
            return result
        return super().filter_queryset(queryset)
