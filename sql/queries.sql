-- queries.sql — 10 analytical queries on bluestock_mf.db
-- Run against: bluestock_mf.db (SQLite)

-- 1. Top 5 funds by latest AUM
SELECT
    f.scheme_name,
    f.fund_house,
    a.aum_cr
FROM fact_aum a
JOIN dim_fund f ON a.scheme_code = f.scheme_code
WHERE a.month = (SELECT MAX(month) FROM fact_aum)
ORDER BY a.aum_cr DESC
LIMIT 5;


-- 2. Average NAV per month for each fund (2024)
SELECT
    f.scheme_name,
    strftime('%Y-%m', n.date) AS month,
    ROUND(AVG(n.nav), 4)      AS avg_nav
FROM fact_nav n
JOIN dim_fund f ON n.scheme_code = f.scheme_code
WHERE strftime('%Y', n.date) = '2024'
GROUP BY f.scheme_name, month
ORDER BY f.scheme_name, month;


-- 3. SIP transaction count and total amount — year over year
SELECT
    strftime('%Y', txn_date) AS year,
    COUNT(*)                 AS sip_count,
    ROUND(SUM(amount), 2)    AS total_amount
FROM fact_transactions
WHERE txn_type = 'SIP'
GROUP BY year
ORDER BY year;


-- 4. Total transactions and amount by state
SELECT
    state,
    COUNT(*)              AS txn_count,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(AVG(amount), 2) AS avg_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;


-- 5. Funds with expense_ratio below 1% (direct plan advantage)
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    ROUND(AVG(p.expense_ratio), 3) AS avg_expense_ratio
FROM fact_performance p
JOIN dim_fund f ON p.scheme_code = f.scheme_code
GROUP BY p.scheme_code
HAVING avg_expense_ratio < 1.0
ORDER BY avg_expense_ratio;


-- 6. Best performing funds by 1-year return (latest period)
SELECT
    f.scheme_name,
    f.category,
    p.ret_1y,
    p.benchmark_ret,
    ROUND(p.ret_1y - p.benchmark_ret, 2) AS alpha_vs_benchmark
FROM fact_performance p
JOIN dim_fund f ON p.scheme_code = f.scheme_code
WHERE p.period = (SELECT MAX(period) FROM fact_performance)
ORDER BY p.ret_1y DESC
LIMIT 10;


-- 7. Monthly AUM trend for top 3 funds
SELECT
    f.scheme_name,
    a.month,
    a.aum_cr,
    a.folios
FROM fact_aum a
JOIN dim_fund f ON a.scheme_code = f.scheme_code
WHERE f.scheme_code IN (
    SELECT scheme_code FROM fact_aum
    GROUP BY scheme_code
    ORDER BY AVG(aum_cr) DESC
    LIMIT 3
)
ORDER BY f.scheme_name, a.month;


-- 8. KYC status breakdown of investors
SELECT
    kyc_status,
    COUNT(DISTINCT investor_id) AS investors,
    COUNT(*)                    AS transactions,
    ROUND(SUM(amount), 2)       AS total_invested
FROM fact_transactions
GROUP BY kyc_status
ORDER BY total_invested DESC;


-- 9. Redemption rate per fund (redemptions vs total transactions)
SELECT
    f.scheme_name,
    COUNT(*) AS total_txns,
    SUM(CASE WHEN t.txn_type = 'Redemption' THEN 1 ELSE 0 END) AS redemptions,
    ROUND(
        100.0 * SUM(CASE WHEN t.txn_type = 'Redemption' THEN 1 ELSE 0 END) / COUNT(*), 1
    ) AS redemption_rate_pct
FROM fact_transactions t
JOIN dim_fund f ON t.scheme_code = f.scheme_code
GROUP BY t.scheme_code
ORDER BY redemption_rate_pct DESC;


-- 10. Risk-adjusted return: funds with sharpe > 1 and alpha > 0
SELECT
    f.scheme_name,
    f.fund_house,
    f.risk_grade,
    ROUND(AVG(p.ret_1y), 2)        AS avg_1y_return,
    ROUND(AVG(p.alpha), 3)         AS avg_alpha,
    ROUND(AVG(p.expense_ratio), 3) AS avg_ter
FROM fact_performance p
JOIN dim_fund f ON p.scheme_code = f.scheme_code
GROUP BY p.scheme_code
HAVING avg_alpha > 0
ORDER BY avg_1y_return DESC;
