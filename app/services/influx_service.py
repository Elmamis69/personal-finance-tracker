from influxdb_client import Point
from datetime import datetime
from app.core.config import settings
from app.db.influxdb import get_write_api, get_query_api
from app.models.transaction import TransactionType

class InfluxService:
    """Service for writing and querying financial metrics  in InfluxDB"""

    @staticmethod
    def write_transaction_metric(
        transaction_id: str,
        amount: float,
        transaction_type: TransactionType,
        category: str,
        date: datetime
    ):
        """
        Write a transaction metric to InfluxDB

        Args:
            transaction_id: MongoDB transaction ID
            amount: Transaction amount
            transaction_type: income or expense
            category: Transaction category
            date: Transaction date
        """

        write_api = get_write_api()

        point = (
            Point("transactions")
            .tag("type", transaction_type.value)
            .tag("category", category)
            .field("amount", float(amount))
            .tag("transaction_id", transaction_id)
            .time(date)
        )
        write_api.write(
            bucket = settings.influxdb_bucket,
            org = settings.influxdb_org,
            record = point
        )

    @staticmethod
    def delete_transaction_metric(transaction_id: str):
        """
        Delete transaction metric from InfluxDB (not commonly used, metrics are typically kept))
        Note: InfluxDB does not support deletes easily, this is a placeholder
        """

        # InfluxDB is designed for time-series data and does not support easy deletes 
        # Typically, we'd just stop writing new data or use retention policies
        pass

    @staticmethod
    def get_spending_trend(start_date: datetime, end_date: datetime, interval: str = "1d"):
        """
        Get spending trend over time

        Args:
            start_date: Start date for the query
            end_date: End date for the query
            interval: Time interval for aggregation (1h, 1d, 1w, 1mo)

        Returns:
            List of data points with timestamp and amount
        """
        query_api = get_query_api()

        query = f'''
        from(bucket: "{settings.influxdb_bucket}")
            |> range(start: {start_date.isoformat()}Z, stop: {end_date.isoformat()}Z)
            |> filter(fn: (r) => r["_measurement"] == "transactions")
            |> filter(fn: (r) => r["type"] == "expense")
            |> filter(fn: (r) => r["_field"] == "amount")
            |> aggregateWindow(every: {interval}, fn: sum, createEmpty: false)
            |> yield(name: "spending_trend")
        '''

        result = query_api.query(org = settings.influxdb_org, query = query)

        data_points = []
        for table in result:
            for record in table.records:
                data_points.append({
                    "timestamp": record.get_time().isoformat(),
                    "amount": record.get_value()
                })

        return data_points
    
    @staticmethod
    def get_category_breakdown(start_date: datetime, end_date: datetime):
        """
        Get spending breakdown by category

        Args:
            start_date: Start date for the query
            end_date: End date for the query

        Returns:
            List of categories with total amounts
        """
        query_api = get_query_api()

        query = f'''
        from(bucket: "{settings.influxdb_bucket}")
            |> range(start: {start_date.isoformat()}Z, stop: {end_date.isoformat()}Z)
            |> filter(fn: (r) => r["_measurement"] == "transactions")
            |> filter(fn: (r) => r["type"] == "expense")
            |> filter(fn: (r) => r["_field"] == "amount")
            |> group(columns: ["category"])
            |> sum()
            |> yield(name: "category_breakdown")
        '''

        result = query_api.query(org = settings.influxdb_org, query = query)

        data = []
        for table in result:
            for record in table.records:
                data.append({
                    "category": record.values.get("category"),
                    "total_amount": record.get_value()
                })

        return data
    
    @staticmethod
    def get_income_vs_expenses(start_date: datetime, end_date: datetime):
        """
        Get total income vs expenses

        Args:
            start_date: Start date for the query
            end_date: End date for the query

        Returns:
            Dictionary with total_income, total_expenses, and net_savings
        """
        query_api = get_query_api()
        
        # Query for total income
        income_query = f'''
        from(bucket: "{settings.influxdb_bucket}")
            |> range(start: {start_date.isoformat()}Z, stop: {end_date.isoformat()}Z)
            |> filter(fn: (r) => r["_measurement"] == "transactions")
            |> filter(fn: (r) => r["type"] == "income")
            |> filter(fn: (r) => r["_field"] == "amount")
            |> sum()
        '''

        # Query for total expenses
        expenses_query = f'''
        from(bucket: "{settings.influxdb_bucket}")
            |> range(start: {start_date.isoformat()}Z, stop: {end_date.isoformat()}Z)
            |> filter(fn: (r) => r["_measurement"] == "transactions")
            |> filter(fn: (r) => r["type"] == "expense")
            |> filter(fn: (r) => r["_field"] == "amount")
            |> sum()
        '''

        income_result = query_api.query(org = settings.influxdb_org, query = income_query)
        expenses_result = query_api.query(org = settings.influxdb_org, query = expenses_query)

        total_income = 0
        for table in income_result:
            for record in table.records:
                total_income = record.get_value()
        
        total_expenses = 0
        for table in expenses_result:
            for record in table.records:
                total_expenses = record.get_value()

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_savings": total_income - total_expenses,
            "savings_rate": ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
        }
    
influx_service = InfluxService()