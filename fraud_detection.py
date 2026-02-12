import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

class FraudDetectionAnalyzer:
    """Fraud detection analysis using Pandas and SQL-like operations"""
    
    def __init__(self, transactions_df: pd.DataFrame, customers_df: pd.DataFrame):
        self.transactions_df = transactions_df.copy()
        self.customers_df = customers_df.copy()
        
        # Convert date strings to datetime if needed
        if isinstance(self.transactions_df['transaction_date'].iloc[0], str):
            self.transactions_df['transaction_date'] = pd.to_datetime(self.transactions_df['transaction_date'])
        if isinstance(self.customers_df['registration_date'].iloc[0], str):
            self.customers_df['registration_date'] = pd.to_datetime(self.customers_df['registration_date'])
    
    def get_fraud_statistics(self) -> Dict[str, Any]:
        """Get overall fraud statistics"""
        total_transactions = len(self.transactions_df)
        fraud_transactions = self.transactions_df['is_fraud'].sum()
        fraud_rate = (fraud_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        total_amount = self.transactions_df['amount'].sum()
        fraud_amount = self.transactions_df[self.transactions_df['is_fraud'] == 1]['amount'].sum()
        
        return {
            'total_transactions': int(total_transactions),
            'fraud_transactions': int(fraud_transactions),
            'legitimate_transactions': int(total_transactions - fraud_transactions),
            'fraud_rate': round(fraud_rate, 2),
            'total_amount': round(float(total_amount), 2),
            'fraud_amount': round(float(fraud_amount), 2),
            'legitimate_amount': round(float(total_amount - fraud_amount), 2)
        }
    
    def get_fraud_trends_by_day(self) -> List[Dict[str, Any]]:
        """Analyze fraud trends over time - demonstrates GROUP BY and aggregation"""
        # SQL equivalent: SELECT DATE(transaction_date), COUNT(*), SUM(is_fraud) FROM transactions GROUP BY DATE(transaction_date)
        self.transactions_df['date'] = self.transactions_df['transaction_date'].dt.date
        
        daily_stats = self.transactions_df.groupby('date').agg({
            'transaction_id': 'count',
            'is_fraud': 'sum',
            'amount': 'sum'
        }).reset_index()
        
        daily_stats.columns = ['date', 'total_transactions', 'fraud_count', 'total_amount']
        daily_stats['fraud_rate'] = (daily_stats['fraud_count'] / daily_stats['total_transactions'] * 100).round(2)
        daily_stats['date'] = daily_stats['date'].astype(str)
        
        return daily_stats.to_dict('records')
    
    def get_high_risk_customers(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """Identify high-risk customers - demonstrates JOIN and window functions"""
        # SQL equivalent with JOIN:
        # SELECT c.customer_id, c.customer_name, COUNT(t.transaction_id) as fraud_count,
        #        SUM(t.amount) as fraud_amount, c.risk_level
        # FROM customers c JOIN transactions t ON c.customer_id = t.customer_id
        # WHERE t.is_fraud = 1
        # GROUP BY c.customer_id ORDER BY fraud_count DESC LIMIT top_n
        
        fraud_transactions = self.transactions_df[self.transactions_df['is_fraud'] == 1]
        
        # Join transactions with customers
        merged = fraud_transactions.merge(self.customers_df, on='customer_id', how='left')
        
        # Group by customer
        customer_fraud = merged.groupby(['customer_id', 'customer_name', 'risk_level']).agg({
            'transaction_id': 'count',
            'amount': 'sum'
        }).reset_index()
        
        customer_fraud.columns = ['customer_id', 'customer_name', 'risk_level', 'fraud_count', 'fraud_amount']
        customer_fraud['fraud_amount'] = customer_fraud['fraud_amount'].round(2)
        
        # Sort and get top N
        customer_fraud = customer_fraud.sort_values('fraud_count', ascending=False).head(top_n)
        
        return customer_fraud.to_dict('records')
    
    def get_fraud_by_location(self) -> List[Dict[str, Any]]:
        """Analyze fraud patterns by location"""
        location_stats = self.transactions_df.groupby('location').agg({
            'transaction_id': 'count',
            'is_fraud': 'sum',
            'amount': 'sum'
        }).reset_index()
        
        location_stats.columns = ['location', 'total_transactions', 'fraud_count', 'total_amount']
        location_stats['fraud_rate'] = (location_stats['fraud_count'] / location_stats['total_transactions'] * 100).round(2)
        location_stats = location_stats.sort_values('fraud_count', ascending=False)
        
        return location_stats.to_dict('records')
    
    def get_transaction_velocity_analysis(self) -> List[Dict[str, Any]]:
        """Analyze transaction velocity using window functions - demonstrates LAG/LEAD"""
        # SQL equivalent using window functions:
        # SELECT customer_id, transaction_date,
        #        LAG(transaction_date) OVER (PARTITION BY customer_id ORDER BY transaction_date) as prev_transaction,
        #        DATEDIFF(transaction_date, prev_transaction) as time_diff
        
        df = self.transactions_df.sort_values(['customer_id', 'transaction_date'])
        
        # Calculate time difference between consecutive transactions (window function LAG)
        df['prev_transaction_date'] = df.groupby('customer_id')['transaction_date'].shift(1)
        df['time_diff_minutes'] = (df['transaction_date'] - df['prev_transaction_date']).dt.total_seconds() / 60
        
        # Calculate running count of transactions per customer (window function ROW_NUMBER)
        df['transaction_rank'] = df.groupby('customer_id').cumcount() + 1
        
        # Get suspicious velocity patterns (multiple transactions in short time)
        suspicious = df[df['time_diff_minutes'] < 5].copy()  # Transactions within 5 minutes
        
        if len(suspicious) > 0:
            suspicious['time_diff_minutes'] = suspicious['time_diff_minutes'].round(2)
            result = suspicious[[
                'customer_id', 'transaction_id', 'transaction_date', 
                'amount', 'is_fraud', 'time_diff_minutes'
            ]].head(50)
            
            result['transaction_date'] = result['transaction_date'].astype(str)
            return result.to_dict('records')
        
        return []
    
    def get_merchant_fraud_analysis(self) -> List[Dict[str, Any]]:
        """Analyze fraud patterns by merchant"""
        merchant_stats = self.transactions_df.groupby(['merchant', 'merchant_category']).agg({
            'transaction_id': 'count',
            'is_fraud': 'sum',
            'amount': 'sum'
        }).reset_index()
        
        merchant_stats.columns = ['merchant', 'category', 'total_transactions', 'fraud_count', 'total_amount']
        merchant_stats['fraud_rate'] = (merchant_stats['fraud_count'] / merchant_stats['total_transactions'] * 100).round(2)
        merchant_stats = merchant_stats.sort_values('fraud_rate', ascending=False)
        
        return merchant_stats.to_dict('records')
    
    def get_amount_range_analysis(self) -> List[Dict[str, Any]]:
        """Analyze fraud by transaction amount ranges - demonstrates CASE WHEN"""
        # SQL equivalent:
        # SELECT CASE 
        #   WHEN amount < 100 THEN '0-100'
        #   WHEN amount < 500 THEN '100-500'
        #   ... END as amount_range,
        # COUNT(*), SUM(is_fraud) FROM transactions GROUP BY amount_range
        
        def categorize_amount(amount):
            if amount < 100:
                return '0-100'
            elif amount < 500:
                return '100-500'
            elif amount < 1000:
                return '500-1000'
            elif amount < 5000:
                return '1000-5000'
            else:
                return '5000+'
        
        self.transactions_df['amount_range'] = self.transactions_df['amount'].apply(categorize_amount)
        
        range_stats = self.transactions_df.groupby('amount_range').agg({
            'transaction_id': 'count',
            'is_fraud': 'sum'
        }).reset_index()
        
        range_stats.columns = ['amount_range', 'total_transactions', 'fraud_count']
        range_stats['fraud_rate'] = (range_stats['fraud_count'] / range_stats['total_transactions'] * 100).round(2)
        
        # Sort by range
        range_order = ['0-100', '100-500', '500-1000', '1000-5000', '5000+']
        range_stats['sort_order'] = range_stats['amount_range'].map({r: i for i, r in enumerate(range_order)})
        range_stats = range_stats.sort_values('sort_order').drop('sort_order', axis=1)
        
        return range_stats.to_dict('records')
    
    def get_data_quality_metrics(self) -> Dict[str, Any]:
        """Calculate data quality metrics - important for Data Governance"""
        transactions_quality = {
            'total_records': len(self.transactions_df),
            'null_values': int(self.transactions_df.isnull().sum().sum()),
            'duplicate_transactions': int(self.transactions_df.duplicated(subset=['transaction_id']).sum()),
            'completeness_rate': round((1 - self.transactions_df.isnull().sum().sum() / (len(self.transactions_df) * len(self.transactions_df.columns))) * 100, 2)
        }
        
        customers_quality = {
            'total_records': len(self.customers_df),
            'null_values': int(self.customers_df.isnull().sum().sum()),
            'duplicate_customers': int(self.customers_df.duplicated(subset=['customer_id']).sum()),
            'completeness_rate': round((1 - self.customers_df.isnull().sum().sum() / (len(self.customers_df) * len(self.customers_df.columns))) * 100, 2)
        }
        
        return {
            'transactions': transactions_quality,
            'customers': customers_quality,
            'overall_quality_score': round((transactions_quality['completeness_rate'] + customers_quality['completeness_rate']) / 2, 2)
        }
    
    def get_recent_transactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent transactions with customer details - demonstrates JOIN"""
        # Join transactions with customers
        merged = self.transactions_df.merge(self.customers_df[['customer_id', 'customer_name', 'country']], on='customer_id', how='left')
        
        # Sort by date and get recent
        recent = merged.sort_values('transaction_date', ascending=False).head(limit)
        recent['transaction_date'] = recent['transaction_date'].astype(str)
        
        return recent.to_dict('records')
