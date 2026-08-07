from django.core.management.base import BaseCommand
from django.conf import settings
from core.security import get_password_hash
from apps.accounts.models import User, Organization, Branch
from apps.master_data.models import ProductCategory, Unit, Warehouse

class Command(BaseCommand):
    help = 'Initialize database with default seed data'

    def handle(self, *args, **options):
        # 1. Default Organization and Branch
        org, _ = Organization.objects.get_or_create(
            name="Kotyol Group",
            defaults={"description": "Asosiy Isitish Kotyollari Tashkiloti"}
        )

        branch, _ = Branch.objects.get_or_create(
            organization=org,
            code="MAIN-BRANCH",
            defaults={
                "name": "Asosiy filial",
                "address": "Toshkent shahri",
                "phone": "+998901234567"
            }
        )

        # 2. Superadmin user
        admin_user = User.objects.filter(username=settings.SUPERADMIN_USERNAME).first()
        if not admin_user:
            admin_user = User.objects.create(
                username=settings.SUPERADMIN_USERNAME,
                full_name="Alex Vance",
                hashed_password=get_password_hash(settings.SUPERADMIN_PASSWORD),
                role="ADMIN",
                phone=settings.SUPERADMIN_USERNAME,
                department="Management",
                organization_name="Kotyol Group",
                branch_name="Asosiy filial",
                organization=org,
                branch=branch,
                status="ACTIVE"
            )
            self.stdout.write(self.style.SUCCESS(f"Superadmin user created: {settings.SUPERADMIN_USERNAME} / {settings.SUPERADMIN_PASSWORD}"))

        # 3. Master Data
        cat, _ = ProductCategory.objects.get_or_create(
            code="CAT-BOILER",
            defaults={
                "name": "Isitish Kotyollari",
                "description": "Kotyol mahsulotlari",
                "organization_id": org.id,
                "branch_id": branch.id
            }
        )

        unit, _ = Unit.objects.get_or_create(
            code="UNIT-PCS",
            defaults={
                "name": "dona",
                "symbol": "dona",
                "organization_id": org.id,
                "branch_id": branch.id
            }
        )

        wh, _ = Warehouse.objects.get_or_create(
            code="WH-MAIN",
            defaults={
                "name": "Asosiy Ombor",
                "location": "Toshkent",
                "organization_id": org.id,
                "branch_id": branch.id
            }
        )

        self.stdout.write(self.style.SUCCESS("Modular DB initialization & seed completed!"))
