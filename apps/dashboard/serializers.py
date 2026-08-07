from rest_framework import serializers

class DashboardSummaryDataSerializer(serializers.Serializer):
    monthly_revenue = serializers.FloatField()
    revenue_growth_percent = serializers.FloatField()
    active_orders_count = serializers.IntegerField()
    completed_boilers_count = serializers.IntegerField()
    low_stock_alerts_count = serializers.IntegerField()

class ChartDataPointSerializer(serializers.Serializer):
    label = serializers.CharField()
    sales = serializers.FloatField()
    production = serializers.IntegerField()

class DashboardChartsDataSerializer(serializers.Serializer):
    trends = ChartDataPointSerializer(many=True)
