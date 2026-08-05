import sqlite3

conn = sqlite3.connect("bluestock_mf.db")

print("\n--- Top 5 Funds by AUM ---")
for r in conn.execute("""
    SELECT f.scheme_name, a.aum_cr
    FROM fact_aum a JOIN dim_fund f ON a.scheme_code=f.scheme_code
    WHERE a.month=(SELECT MAX(month) FROM fact_aum)
    ORDER BY a.aum_cr DESC LIMIT 5
""").fetchall():
    print(r)

print("\n--- SIP Year over Year ---")
for r in conn.execute("""
    SELECT strftime('%Y', txn_date) yr, COUNT(*) cnt, ROUND(SUM(amount),2) total
    FROM fact_transactions WHERE txn_type='SIP'
    GROUP BY yr ORDER BY yr
""").fetchall():
    print(r)

print("\n--- KYC Breakdown ---")
for r in conn.execute("""
    SELECT kyc_status, COUNT(*) txns, ROUND(SUM(amount),2) total
    FROM fact_transactions GROUP BY kyc_status
""").fetchall():
    print(r)

print("\n--- Funds with Expense Ratio < 1% ---")
for r in conn.execute("""
    SELECT f.scheme_name, ROUND(AVG(p.expense_ratio),3) ter
    FROM fact_performance p JOIN dim_fund f ON p.scheme_code=f.scheme_code
    GROUP BY p.scheme_code HAVING ter < 1.0 ORDER BY ter LIMIT 5
""").fetchall():
    print(r)

print("\n--- Redemption Rate per Fund ---")
for r in conn.execute("""
    SELECT f.scheme_name,
           ROUND(100.0*SUM(CASE WHEN t.txn_type='Redemption' THEN 1 ELSE 0 END)/COUNT(*),1) rate
    FROM fact_transactions t JOIN dim_fund f ON t.scheme_code=f.scheme_code
    GROUP BY t.scheme_code ORDER BY rate DESC LIMIT 5
""").fetchall():
    print(r)

print("\n--- Best 1-Year Performers ---")
for r in conn.execute("""
    SELECT f.scheme_name, p.ret_1y, p.benchmark_ret,
           ROUND(p.ret_1y - p.benchmark_ret, 2) alpha_vs_bench
    FROM fact_performance p JOIN dim_fund f ON p.scheme_code=f.scheme_code
    WHERE p.period=(SELECT MAX(period) FROM fact_performance)
    ORDER BY p.ret_1y DESC LIMIT 5
""").fetchall():
    print(r)

conn.close()
print("\ndone")
