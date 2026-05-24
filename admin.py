from django.contrib import admin
from .models import AnalysisOutcome, WatchlistItem, WatchlistAlert, SimulationRecord


@admin.register(AnalysisOutcome)
class AnalysisOutcomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'timestamp', 'expected_return', 'sharpe_ratio')
    list_filter = ('user', 'timestamp')


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'added_at')
    list_filter = ('user',)


admin.site.register(WatchlistAlert)
admin.site.register(SimulationRecord)











from django.contrib import admin
from .models import AnalysisResult

admin.site.register(AnalysisResult)