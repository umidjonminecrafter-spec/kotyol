from core.exceptions import CustomAppException
from apps.sales.models import Lead

class LeadService:
    @staticmethod
    def create_lead(data: dict, created_by_id: str) -> Lead:
        lead = Lead.objects.create(
            full_name=data.get('full_name'),
            phone=data.get('phone'),
            email=data.get('email', ''),
            company_name=data.get('company_name', ''),
            status=data.get('status', 'NEW'),
            source=data.get('source', ''),
            notes=data.get('notes', ''),
            next_contact_date=data.get('next_contact_date') or None,
            assigned_employee_id=data.get('assigned_employee_id', ''),
            assigned_employee_name=data.get('assigned_employee_name', ''),
            created_by_id=created_by_id
        )
        return lead

    @staticmethod
    def update_lead(lead_id: str, data: dict, updated_by_id: str) -> Lead:
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            raise CustomAppException(message="Lid topilmadi", status_code=404)

        for field in ['full_name', 'phone', 'email', 'company_name', 'status', 'source', 'notes', 'next_contact_date', 'assigned_employee_id', 'assigned_employee_name']:
            if field in data:
                val = data[field]
                if field == 'next_contact_date' and not val:
                    val = None
                setattr(lead, field, val)

        lead.updated_by_id = updated_by_id
        lead.save()
        return lead

    @staticmethod
    def get_multi():
        qs = Lead.objects.all()
        return list(qs.order_by('-created_at'))
