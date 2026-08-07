from django.db import models
from core.base_model import BaseModel

class Product(BaseModel):
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    category = models.ForeignKey('master_data.ProductCategory', on_delete=models.CASCADE, db_column='category_id', related_name='products')
    material_type = models.ForeignKey('master_data.MaterialType', on_delete=models.SET_NULL, null=True, blank=True, db_column='material_type_id', related_name='products')
    unit = models.ForeignKey('master_data.Unit', on_delete=models.CASCADE, db_column='unit_id', related_name='products')
    supplier = models.ForeignKey('master_data.Supplier', on_delete=models.SET_NULL, null=True, blank=True, db_column='supplier_id', related_name='products')
    
    type = models.CharField(max_length=50)  # 'FINISHED_GOOD', 'RAW_MATERIAL', 'SPARE_PART'
    min_stock_level = models.DecimalField(max_digits=15, decimal_places=3, default=0.000)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default="USD")

    class Meta:
        db_table = 'products'

class Recipe(BaseModel):
    recipe_number = models.CharField(max_length=50, unique=True)
    recipe_name = models.CharField(max_length=255, default="Nomsiz Retseptura")
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True, db_column='product_id', related_name='recipes')
    version = models.CharField(max_length=20, default="v1.0")
    estimated_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'recipes'

class RecipeItem(BaseModel):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, db_column='recipe_id', related_name='items')
    material_product = models.ForeignKey('Product', on_delete=models.CASCADE, db_column='material_product_id', related_name='used_in_recipes')
    quantity = models.DecimalField(max_digits=15, decimal_places=3)
    waste_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'recipe_items'

class Boiler(BaseModel):
    model_code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    capacity_kw = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    fuel_type = models.CharField(max_length=50, default="GAS")  # 'GAS', 'COAL', 'ELECTRIC', 'DUAL'
    efficiency_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    base_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recipe = models.ForeignKey('Recipe', on_delete=models.SET_NULL, null=True, blank=True, db_column='recipe_id', related_name='boilers')
    warranty_type = models.ForeignKey('master_data.WarrantyType', on_delete=models.SET_NULL, null=True, blank=True, db_column='warranty_type_id', related_name='boilers')
    selected_stage_ids = models.JSONField(default=list, blank=True, null=True)

    class Meta:
        db_table = 'boilers'
