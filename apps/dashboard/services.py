from apps.finance.services import FinanceService

class DashboardService:
    @staticmethod
    def get_summary():
        return FinanceService.get_dashboard_summary()

    @staticmethod
    def get_charts():
        return FinanceService.get_dashboard_charts()
