import random
import pandas as pd
from datetime import datetime, timedelta
import uuid
import numpy as np

class BankingDataGenerator:
    """Generate synthetic banking transaction data for fraud detection analysis"""
    
    def __init__(self, num_customers=1000, num_transactions=10000):
        self.num_customers = num_customers
        self.num_transactions = num_transactions
        self.fraud_rate = 0.05  # 5% fraud rate
        
    def generate_customers(self):
        """Generate customer data"""
        customers = []
        countries = ['USA', 'UK', 'Canada', 'Germany', 'France', 'India', 'Australia']
        risk_levels = ['Low', 'Medium', 'High']
        
        for i in range(self.num_customers):
            customer = {
                'customer_id': f'CUST{str(i+1).zfill(6)}',
                'customer_name': f'Customer {i+1}',
                'email': f'customer{i+1}@email.com',
                'country': random.choice(countries),
                'registration_date': (datetime.now() - timedelta(days=random.randint(30, 1095))).isoformat(),
                'risk_level': random.choices(risk_levels, weights=[0.7, 0.25, 0.05])[0],
                'account_balance': round(random.uniform(1000, 100000), 2),
                'credit_score': random.randint(300, 850)
            }
            customers.append(customer)
        
        return pd.DataFrame(customers)
    
    def generate_transactions(self, customers_df):
        """Generate transaction data with fraud indicators"""
        transactions = []
        transaction_types = ['Purchase', 'Transfer', 'Withdrawal', 'Deposit']
        merchants = ['Amazon', 'Walmart', 'Best Buy', 'Target', 'Apple Store', 'Gas Station', 'Restaurant', 'Online Store']
        
        # Determine which transactions will be fraudulent
        num_fraud = int(self.num_transactions * self.fraud_rate)
        fraud_indices = set(random.sample(range(self.num_transactions), num_fraud))
        
        for i in range(self.num_transactions):
            is_fraud = i in fraud_indices
            customer = customers_df.sample(1).iloc[0]
            
            # Fraud transactions have different patterns
            if is_fraud:
                amount = round(random.uniform(5000, 50000), 2)  # Higher amounts
                time_hour = random.choice([0, 1, 2, 3, 4, 23])  # Unusual hours
                transaction_type = random.choice(['Purchase', 'Transfer'])
                distance_from_home = random.uniform(500, 5000)  # Far from home
            else:
                amount = round(random.uniform(10, 5000), 2)  # Normal amounts
                time_hour = random.randint(6, 22)  # Normal hours
                transaction_type = random.choice(transaction_types)
                distance_from_home = random.uniform(0, 100)  # Near home
            
            transaction_date = datetime.now() - timedelta(days=random.randint(0, 90))
            transaction_date = transaction_date.replace(hour=time_hour, minute=random.randint(0, 59))
            
            transaction = {
                'transaction_id': str(uuid.uuid4()),
                'customer_id': customer['customer_id'],
                'transaction_date': transaction_date.isoformat(),
                'amount': amount,
                'transaction_type': transaction_type,
                'merchant': random.choice(merchants),
                'merchant_category': random.choice(['Retail', 'Online', 'Food', 'Travel', 'Entertainment']),
                'location': random.choice(['New York', 'Los Angeles', 'Chicago', 'London', 'Paris', 'Tokyo']),
                'distance_from_home_km': round(distance_from_home, 2),
                'is_fraud': 1 if is_fraud else 0,
                'fraud_reason': self._get_fraud_reason(is_fraud, amount, time_hour, distance_from_home) if is_fraud else None
            }
            transactions.append(transaction)
        
        return pd.DataFrame(transactions)
    
    def _get_fraud_reason(self, is_fraud, amount, time_hour, distance):
        """Generate fraud reason based on patterns"""
        reasons = []
        if amount > 5000:
            reasons.append('High transaction amount')
        if time_hour < 5 or time_hour > 22:
            reasons.append('Unusual transaction time')
        if distance > 500:
            reasons.append('Transaction far from registered location')
        
        return ', '.join(reasons) if reasons else 'Suspicious pattern detected'
    
    def generate_all_data(self):
        """Generate complete dataset"""
        customers_df = self.generate_customers()
        transactions_df = self.generate_transactions(customers_df)
        
        return customers_df, transactions_df

def get_sample_data():
    """Helper function to get sample data"""
    generator = BankingDataGenerator(num_customers=500, num_transactions=5000)
    customers_df, transactions_df = generator.generate_all_data()
    return customers_df, transactions_df
