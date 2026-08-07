from django.test import TestCase
from rest_framework.test import APIClient
from django.conf import settings
from core.security import get_password_hash
from apps.accounts.models import User
from apps.master_data.models import ProductCategory, Unit, Warehouse

class KatyolAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            username="admin@kotyol.uz",
            full_name="Alex Vance",
            hashed_password=get_password_hash("Password123!"),
            role="ADMIN",
            department="Management",
            status="ACTIVE"
        )
        self.cat = ProductCategory.objects.create(code="CAT-BOILER", name="Isitish Kotyollari")
        self.unit = Unit.objects.create(code="UNIT-PCS", name="dona")
        self.wh = Warehouse.objects.create(code="WH-MAIN", name="Asosiy Ombor")

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertEqual(data["app"], "Kotyol ERP Backend")

    def test_cors_preflight(self):
        response = self.client.options(
            "/api/v1/auth/branches",
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="x-branch-id,authorization"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Access-Control-Allow-Origin"], "http://localhost:3000")
        self.assertIn("x-branch-id", response["Access-Control-Allow-Headers"].lower())


    def test_login_success_and_invalid(self):
        # Invalid login
        res_bad = self.client.post("/api/v1/auth/login", {"username": "admin@kotyol.uz", "password": "WrongPassword"}, format='json')
        self.assertEqual(res_bad.status_code, 401)
        self.assertFalse(res_bad.json()["success"])

        # Valid login
        res = self.client.post("/api/v1/auth/login", {"username": "admin@kotyol.uz", "password": "Password123!"}, format='json')
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body["success"])
        self.assertIn("access_token", body["data"])
        self.assertEqual(body["data"]["user"]["username"], "admin@kotyol.uz")

    def test_products_and_safe_delete(self):
        # Login as admin
        login_res = self.client.post("/api/v1/auth/login", {"username": "admin@kotyol.uz", "password": "Password123!"}, format='json')
        token = login_res.json()["data"]["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Fetch Categories to get valid category_id and unit_id
        cat_res = self.client.get("/api/v1/master-data/product-categories")
        cat_id = cat_res.json()["data"][0]["id"]

        unit_res = self.client.get("/api/v1/master-data/units")
        unit_id = unit_res.json()["data"][0]["id"]

        # Create product
        prod_data = {
            "code": "PRD-101",
            "name": "Kotyol K-50kW",
            "category_id": cat_id,
            "unit_id": unit_id,
            "type": "FINISHED_GOOD",
            "min_stock_level": 5.0,
            "unit_price": 2500.00
        }
        prod_res = self.client.post("/api/v1/products", prod_data, format='json')
        self.assertEqual(prod_res.status_code, 201)
        prod_body = prod_res.json()
        self.assertTrue(prod_body["success"])
        self.assertEqual(prod_body["data"]["code"], "PRD-101")

        # Attempt to delete the Category which is now referenced by PRD-101
        del_cat_res = self.client.delete(f"/api/v1/master-data/product-categories/{cat_id}")
        self.assertEqual(del_cat_res.status_code, 400)
        del_cat_body = del_cat_res.json()
        self.assertFalse(del_cat_body["success"])
        self.assertEqual(del_cat_body["error_code"], "ENTITY_IN_USE")
        self.assertEqual(del_cat_body["details"]["reference_count"], 1)

    def test_dashboard_summary(self):
        login_res = self.client.post("/api/v1/auth/login", {"username": "admin@kotyol.uz", "password": "Password123!"}, format='json')
        token = login_res.json()["data"]["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        dash_res = self.client.get("/api/v1/dashboard/summary")
        self.assertEqual(dash_res.status_code, 200)
        dash_body = dash_res.json()
        self.assertTrue(dash_body["success"])
        self.assertIn("monthly_revenue", dash_body["data"])
        self.assertIn("active_orders_count", dash_body["data"])
