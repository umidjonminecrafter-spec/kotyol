from django.db import models
from core.base_model import BaseModel

class FinancialTransaction(BaseModel):
    transaction_number = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20)  # 'INCOME', 'EXPENSE'
    expense_type = models.ForeignKey('master_data.ExpenseType', on_delete=models.SET_NULL, null=True, blank=True, db_column='expense_type_id', related_name='financial_transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    reference_id = models.CharField(max_length=100, null=True, blank=True)
    transaction_date = models.DateField()
    notes = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'financial_transactions'
