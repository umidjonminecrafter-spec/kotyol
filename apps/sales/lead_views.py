from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated
from core.audit_helper import record_audit_log
from apps.sales.lead_services import LeadService
from apps.sales.lead_serializers import LeadCreateSerializer, LeadResponseSerializer

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def leads_list_create_view(request):
    if request.method == 'GET':
        items = LeadService.get_multi()
        response_items = LeadResponseSerializer(items, many=True).data
        return Response({
            "success": True,
            "data": response_items
        })

    # POST (create)
    serializer = LeadCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    body_data = serializer.validated_data

    lead = LeadService.create_lead(body_data, created_by_id=request.user.id)
    record_audit_log(
        action="CREATE",
        entity_name="LEAD",
        entity_id=lead.id,
        actor_id=request.user.id,
        new_values=body_data,
        request=request
    )
    return Response({"success": True, "data": LeadResponseSerializer(lead).data}, status=201)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def lead_detail_view(request, id):
    from apps.sales.models import Lead
    try:
        lead = Lead.objects.get(id=id)
    except Lead.DoesNotExist:
        return Response({"success": False, "message": "Lid topilmadi"}, status=404)

    if request.method == 'GET':
        return Response({"success": True, "data": LeadResponseSerializer(lead).data})

    if request.method in ['PUT', 'PATCH']:
        serializer = LeadCreateSerializer(data=request.data, partial=(request.method == 'PATCH'))
        serializer.is_valid(raise_exception=True)
        body_data = serializer.validated_data

        updated_lead = LeadService.update_lead(id, body_data, updated_by_id=request.user.id)
        record_audit_log(
            action="UPDATE", entity_name="LEAD",
            entity_id=id, actor_id=request.user.id, new_values=body_data, request=request
        )
        return Response({"success": True, "data": LeadResponseSerializer(updated_lead).data})

    # DELETE
    lead.delete()
    record_audit_log(
        action="DELETE", entity_name="LEAD",
        entity_id=id, actor_id=request.user.id, request=request
    )
    return Response({"success": True, "data": {"id": id, "deleted": True}})
