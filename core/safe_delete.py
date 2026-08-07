from django.db.models import Q
from core.exceptions import EntityInUseException


class SafeDeleteService:
    @staticmethod
    def check_entity_references(entity_key, entity_id):
        from apps.products.models import Product, RecipeItem
        from apps.purchasing.models import PurchaseItem
        from apps.sales.models import Sale
        from apps.warehouse.models import WarehouseStock

        # Normalize key to plural form
        key = str(entity_key).lower().strip().replace('_', '-')
        if key.endswith('y'):
            key = key[:-1] + 'ies'
        elif not key.endswith('s'):
            key = key + 's'

        total_references = 0
        entity_name_uz = 'Ushbu resurs'

        if key == 'product-categories':
            total_references = Product.objects.filter(category_id=entity_id).exclude(status='ARCHIVED').count()
            entity_name_uz = 'kategoriya'

        elif key == 'units':
            total_references = Product.objects.filter(unit_id=entity_id).exclude(status='ARCHIVED').count()
            entity_name_uz = "o'lchov birligi"

        elif key == 'material-types':
            total_references = Product.objects.filter(material_type_id=entity_id).exclude(status='ARCHIVED').count()
            entity_name_uz = 'material turi'

        elif key == 'suppliers':
            p_count = Product.objects.filter(supplier_id=entity_id).exclude(status='ARCHIVED').count()
            pur_count = PurchaseItem.objects.filter(product_id=entity_id).count()
            total_references = p_count + pur_count
            entity_name_uz = 'yetkazib beruvchi'

        elif key == 'customers':
            total_references = Sale.objects.filter(customer_id=entity_id).count()
            entity_name_uz = 'mijoz'

        elif key == 'warehouses':
            total_references = WarehouseStock.objects.filter(warehouse_id=entity_id).count()
            entity_name_uz = 'ombor'

        elif key == 'products':
            r_count = RecipeItem.objects.filter(material_product_id=entity_id).count()
            pur_count = PurchaseItem.objects.filter(product_id=entity_id).count()
            sale_count = Sale.objects.filter(product_id=entity_id).count()
            total_references = r_count + pur_count + sale_count
            entity_name_uz = 'mahsulot'

        if total_references > 0:
            raise EntityInUseException(
                message=f"Ushbu {entity_name_uz} {total_references} ta ob'ektga biriktirilgan. O'chirish taqiqlangan.",
                reference_count=total_references,
                can_archive=True,
            )
