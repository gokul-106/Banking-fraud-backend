from typing import Dict, List

class SQLQueriesShowcase:
    """Showcase SQL queries and concepts for learning purposes"""
    
    @staticmethod
    def get_all_queries() -> List[Dict[str, str]]:
        """Return all SQL queries with descriptions"""
        return [
            {
                "id": "1",
                "title": "Basic JOIN - Transactions with Customer Details",
                "description": "Demonstrates INNER JOIN to combine transaction and customer data",
                "sql_query": """SELECT 
    t.transaction_id,
    t.transaction_date,
    t.amount,
    t.is_fraud,
    c.customer_name,
    c.country,
    c.risk_level
FROM transactions t
INNER JOIN customers c ON t.customer_id = c.customer_id
WHERE t.is_fraud = 1
ORDER BY t.transaction_date DESC
LIMIT 100;""",
                "concept": "JOIN, WHERE, ORDER BY",
                "pandas_equivalent": "merged = transactions_df.merge(customers_df, on='customer_id', how='inner')"
            },
            {
                "id": "2",
                "title": "Window Function - ROW_NUMBER for Ranking Transactions",
                "description": "Uses ROW_NUMBER() to rank transactions per customer by amount",
                "sql_query": """SELECT 
    customer_id,
    transaction_id,
    amount,
    transaction_date,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id 
        ORDER BY amount DESC
    ) as transaction_rank
FROM transactions
ORDER BY customer_id, transaction_rank;""",
                "concept": "Window Functions (ROW_NUMBER, PARTITION BY)",
                "pandas_equivalent": "df['rank'] = df.groupby('customer_id')['amount'].rank(method='first', ascending=False)"
            },
            {
                "id": "3",
                "title": "Window Function - LAG to Find Time Between Transactions",
                "description": "Uses LAG() to calculate time difference between consecutive transactions",
                "sql_query": """SELECT 
    customer_id,
    transaction_id,
    transaction_date,
    LAG(transaction_date) OVER (
        PARTITION BY customer_id 
        ORDER BY transaction_date
    ) as previous_transaction,
    TIMESTAMPDIFF(MINUTE, 
        LAG(transaction_date) OVER (
            PARTITION BY customer_id 
            ORDER BY transaction_date
        ),
        transaction_date
    ) as minutes_since_last_transaction
FROM transactions
WHERE minutes_since_last_transaction IS NOT NULL
ORDER BY customer_id, transaction_date;""",
                "concept": "Window Functions (LAG, PARTITION BY, ORDER BY)",
                "pandas_equivalent": "df['prev_date'] = df.groupby('customer_id')['transaction_date'].shift(1)"
            },
            {
                "id": "4",
                "title": "Aggregation with GROUP BY - Fraud Rate by Location",
                "description": "Calculates fraud statistics grouped by location",
                "sql_query": """SELECT 
    location,
    COUNT(*) as total_transactions,
    SUM(is_fraud) as fraud_count,
    ROUND(AVG(amount), 2) as avg_transaction_amount,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 2) as fraud_rate_percent
FROM transactions
GROUP BY location
HAVING COUNT(*) > 10
ORDER BY fraud_rate_percent DESC;""",
                "concept": "GROUP BY, Aggregate Functions (COUNT, SUM, AVG), HAVING",
                "pandas_equivalent": "df.groupby('location').agg({'transaction_id': 'count', 'is_fraud': 'sum', 'amount': 'mean'})"
            },
            {
                "id": "5",
                "title": "CASE WHEN - Categorize Transaction Amounts",
                "description": "Uses CASE WHEN to create amount ranges and analyze fraud patterns",
                "sql_query": """SELECT 
    CASE 
        WHEN amount < 100 THEN '0-100'
        WHEN amount < 500 THEN '100-500'
        WHEN amount < 1000 THEN '500-1000'
        WHEN amount < 5000 THEN '1000-5000'
        ELSE '5000+'
    END as amount_range,
    COUNT(*) as total_transactions,
    SUM(is_fraud) as fraud_count,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 2) as fraud_rate
FROM transactions
GROUP BY amount_range
ORDER BY 
    CASE amount_range
        WHEN '0-100' THEN 1
        WHEN '100-500' THEN 2
        WHEN '500-1000' THEN 3
        WHEN '1000-5000' THEN 4
        WHEN '5000+' THEN 5
    END;""",
                "concept": "CASE WHEN, Conditional Logic",
                "pandas_equivalent": "df['amount_range'] = pd.cut(df['amount'], bins=[0, 100, 500, 1000, 5000, np.inf], labels=[...])"
            },
            {
                "id": "6",
                "title": "CTE (Common Table Expression) - High-Risk Customer Analysis",
                "description": "Uses CTE to identify high-risk customers with multiple fraud incidents",
                "sql_query": """WITH fraud_summary AS (
    SELECT 
        customer_id,
        COUNT(*) as total_fraud_count,
        SUM(amount) as total_fraud_amount,
        MAX(transaction_date) as last_fraud_date
    FROM transactions
    WHERE is_fraud = 1
    GROUP BY customer_id
    HAVING COUNT(*) >= 2
)
SELECT 
    c.customer_id,
    c.customer_name,
    c.country,
    c.risk_level,
    c.credit_score,
    fs.total_fraud_count,
    fs.total_fraud_amount,
    fs.last_fraud_date
FROM fraud_summary fs
INNER JOIN customers c ON fs.customer_id = c.customer_id
ORDER BY fs.total_fraud_count DESC, fs.total_fraud_amount DESC;""",
                "concept": "CTE (WITH clause), Subqueries, JOIN",
                "pandas_equivalent": "fraud_summary = df[df['is_fraud']==1].groupby('customer_id').agg(...); result = fraud_summary.merge(customers_df, on='customer_id')"
            },
            {
                "id": "7",
                "title": "Window Function - RANK and DENSE_RANK",
                "description": "Compares RANK and DENSE_RANK for fraud amount ranking",
                "sql_query": """SELECT 
    transaction_id,
    customer_id,
    amount,
    is_fraud,
    RANK() OVER (ORDER BY amount DESC) as amount_rank,
    DENSE_RANK() OVER (ORDER BY amount DESC) as amount_dense_rank,
    PERCENT_RANK() OVER (ORDER BY amount DESC) as amount_percentile
FROM transactions
WHERE is_fraud = 1
LIMIT 50;""",
                "concept": "Window Functions (RANK, DENSE_RANK, PERCENT_RANK)",
                "pandas_equivalent": "df['rank'] = df['amount'].rank(method='min', ascending=False); df['dense_rank'] = df['amount'].rank(method='dense', ascending=False)"
            },
            {
                "id": "8",
                "title": "Subquery - Transactions Above Average",
                "description": "Uses subquery to find transactions above average amount",
                "sql_query": """SELECT 
    t.transaction_id,
    t.customer_id,
    t.amount,
    t.is_fraud,
    t.transaction_date,
    ROUND(t.amount / avg_amount.avg_amt, 2) as amount_vs_avg_ratio
FROM transactions t
CROSS JOIN (
    SELECT AVG(amount) as avg_amt
    FROM transactions
) avg_amount
WHERE t.amount > avg_amount.avg_amt
ORDER BY t.amount DESC
LIMIT 100;""",
                "concept": "Subqueries, CROSS JOIN",
                "pandas_equivalent": "avg_amount = df['amount'].mean(); result = df[df['amount'] > avg_amount]"
            },
            {
                "id": "9",
                "title": "Self JOIN - Find Customers with Transactions in Multiple Locations",
                "description": "Uses self join to detect suspicious activity across locations",
                "sql_query": """SELECT DISTINCT
    t1.customer_id,
    t1.location as location_1,
    t2.location as location_2,
    t1.transaction_date as time_1,
    t2.transaction_date as time_2,
    TIMESTAMPDIFF(HOUR, t1.transaction_date, t2.transaction_date) as hours_difference
FROM transactions t1
INNER JOIN transactions t2 
    ON t1.customer_id = t2.customer_id 
    AND t1.transaction_id != t2.transaction_id
    AND t1.location != t2.location
WHERE TIMESTAMPDIFF(HOUR, t1.transaction_date, t2.transaction_date) BETWEEN 0 AND 24
ORDER BY t1.customer_id, hours_difference
LIMIT 50;""",
                "concept": "Self JOIN, Complex JOIN conditions",
                "pandas_equivalent": "df.merge(df, on='customer_id', suffixes=('_1', '_2'))"
            },
            {
                "id": "10",
                "title": "Window Function - Running Total",
                "description": "Calculates running total of transaction amounts per customer",
                "sql_query": """SELECT 
    customer_id,
    transaction_id,
    transaction_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id 
        ORDER BY transaction_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total,
    AVG(amount) OVER (
        PARTITION BY customer_id 
        ORDER BY transaction_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as moving_avg_last_3
FROM transactions
ORDER BY customer_id, transaction_date;""",
                "concept": "Window Functions (Running Total, Moving Average)",
                "pandas_equivalent": "df['running_total'] = df.groupby('customer_id')['amount'].cumsum(); df['moving_avg'] = df.groupby('customer_id')['amount'].rolling(3).mean()"
            }
        ]
    
    @staticmethod
    def get_query_by_id(query_id: str) -> Dict[str, str]:
        """Get a specific query by ID"""
        queries = SQLQueriesShowcase.get_all_queries()
        for query in queries:
            if query['id'] == query_id:
                return query
        return None
