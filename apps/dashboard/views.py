from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated
from apps.dashboard.services import DashboardService
from apps.dashboard.serializers import DashboardSummaryDataSerializer, ChartDataPointSerializer

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_summary_view(request):
    summary_data = DashboardService.get_summary()
    return Response({
        "success": True,
        "data": DashboardSummaryDataSerializer(summary_data).data
    })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_charts_view(request):
    charts_data = DashboardService.get_charts()
    return Response({
        "success": True,
        "data": {"trends": ChartDataPointSerializer(charts_data, many=True).data}
    })
