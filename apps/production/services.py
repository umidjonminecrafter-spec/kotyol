from core.exceptions import CustomAppException
from apps.production.models import ProductionBatch

class ProductionService:
    @staticmethod
    def create_batch(data: dict, created_by_id: str) -> ProductionBatch:
        import uuid
        import datetime

        b_num = (data.get("batch_number") or data.get("production_number") or "").strip()
        if not b_num or b_num in ["undefined", "null"]:
            b_num = f"BATCH-{datetime.date.today().year}-{str(uuid.uuid4())[:6].upper()}"
        if ProductionBatch.objects.filter(batch_number=b_num).exists():
            b_num = f"BATCH-{datetime.date.today().year}-{str(uuid.uuid4())[:6].upper()}"

        boiler_id = (data.get("boiler_id") or "").strip()
        if not boiler_id or boiler_id in ["undefined", "null"]:
            from apps.products.models import Boiler
            boiler = Boiler.objects.first()
            if boiler:
                boiler_id = str(boiler.id)
            else:
                boiler_id = None

        target_qty = data.get("target_quantity") or data.get("quantity") or 1

        assigned_emp = ""
        if "assigned_employees" in data and isinstance(data["assigned_employees"], list) and len(data["assigned_employees"]) > 0:
            assigned_emp = data["assigned_employees"][0]

        batch = ProductionBatch.objects.create(
            batch_number=b_num,
            boiler_id=boiler_id,
            target_quantity=target_qty,
            completed_quantity=0,
            defect_quantity=0,
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            status="PLANNED",
            assigned_employee=assigned_emp,
            created_by_id=created_by_id
        )
        return batch

    @staticmethod
    def update_batch(batch_id: str, data: dict, updated_by_id: str) -> ProductionBatch:
        try:
            batch = ProductionBatch.objects.get(id=batch_id)
        except ProductionBatch.DoesNotExist:
            raise CustomAppException(message="Ishlab chiqarish partiyasi topilmadi", status_code=404)

        # Map keys before updating
        b_num = data.get("batch_number") or data.get("production_number")
        if b_num is not None:
            batch.batch_number = b_num.strip()

        target_qty = data.get("target_quantity") or data.get("quantity")
        if target_qty is not None:
            batch.target_quantity = target_qty

        for field in ["boiler_id", "completed_quantity", "defect_quantity", "start_date", "end_date", "status"]:
            if field in data and data[field] is not None:
                setattr(batch, field, data[field])

        if "assigned_employees" in data and isinstance(data["assigned_employees"], list):
            batch.assigned_employee = data["assigned_employees"][0] if len(data["assigned_employees"]) > 0 else ""

        batch.updated_by_id = updated_by_id
        batch.save()
        return batch

    @staticmethod
    def delete_batch(batch_id: str) -> bool:
        try:
            batch = ProductionBatch.objects.get(id=batch_id)
        except ProductionBatch.DoesNotExist:
            raise CustomAppException(message="Ishlab chiqarish partiyasi topilmadi", status_code=404)
        batch.delete()
        return True

    @staticmethod
    def get_multi(
        page: int = 1,
        limit: int = 20,
        status: str = None
    ):
        qs = ProductionBatch.objects.all()

        if status:
            qs = qs.filter(status=status)

        total = qs.count()

        skip = (page - 1) * limit
        items = list(qs.order_by('-created_at')[skip:skip + limit])

        return items, total
