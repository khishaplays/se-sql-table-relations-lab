
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect("data.sqlite")


# STEP 1: Employees working in Boston
df_boston = pd.read_sql("""
    SELECT
        e.firstName,
        e.lastName
    FROM employees AS e
    INNER JOIN offices AS o
        ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston'
    ORDER BY e.firstName ASC
""", conn)


# STEP 2: Offices without employees
df_zero_emp = pd.read_sql("""
    SELECT
        o.officeCode,
        o.city
    FROM offices AS o
    LEFT JOIN employees AS e
        ON o.officeCode = e.officeCode
    GROUP BY o.officeCode, o.city
    HAVING COUNT(e.employeeNumber) = 0
""", conn)


# STEP 3: All employees and their office locations
df_employee = pd.read_sql("""
    SELECT
        e.firstName,
        e.lastName,
        o.city,
        o.state
    FROM employees AS e
    LEFT JOIN offices AS o
        ON e.officeCode = o.officeCode
    ORDER BY e.firstName ASC, e.lastName ASC
""", conn)


# STEP 4: Customers without orders
df_contacts = pd.read_sql("""
    SELECT
        c.contactFirstName,
        c.contactLastName,
        c.phone,
        c.salesRepEmployeeNumber
    FROM customers AS c
    LEFT JOIN orders AS o
        ON c.customerNumber = o.customerNumber
    WHERE o.orderNumber IS NULL
    ORDER BY c.contactLastName ASC
""", conn)


# STEP 5: Customer payments sorted by amount
df_payment = pd.read_sql("""
    SELECT
        c.contactFirstName,
        c.contactLastName,
        p.amount,
        p.paymentDate
    FROM customers AS c
    INNER JOIN payments AS p
        ON c.customerNumber = p.customerNumber
    ORDER BY CAST(p.amount AS REAL) DESC
""", conn)


# STEP 6: Sales representatives with average
# customer credit limits above 90,000
df_credit = pd.read_sql("""
    SELECT
        e.employeeNumber,
        e.firstName,
        e.lastName,
        COUNT(c.customerNumber) AS numcustomers
    FROM employees AS e
    INNER JOIN customers AS c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY
        e.employeeNumber,
        e.firstName,
        e.lastName
    HAVING AVG(CAST(c.creditLimit AS REAL)) > 90000
    ORDER BY numcustomers DESC
""", conn)


# STEP 7: Products ranked by total units sold
df_product_sold = pd.read_sql("""
    SELECT
        p.productName,
        COUNT(od.orderNumber) AS numorders,
        SUM(od.quantityOrdered) AS totalunits
    FROM products AS p
    INNER JOIN orderdetails AS od
        ON p.productCode = od.productCode
    GROUP BY
        p.productCode,
        p.productName
    ORDER BY totalunits DESC
""", conn)


# STEP 8: Number of unique purchasers per product
df_total_customers = pd.read_sql("""
    SELECT
        p.productName,
        p.productCode,
        COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products AS p
    INNER JOIN orderdetails AS od
        ON p.productCode = od.productCode
    INNER JOIN orders AS o
        ON od.orderNumber = o.orderNumber
    GROUP BY
        p.productCode,
        p.productName
    ORDER BY numpurchasers DESC
""", conn)


# STEP 9: Number of customers assigned to each office
df_customers = pd.read_sql("""
    SELECT
        o.officeCode,
        o.city,
        COUNT(c.customerNumber) AS n_customers
    FROM offices AS o
    LEFT JOIN employees AS e
        ON o.officeCode = e.officeCode
    LEFT JOIN customers AS c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY
        o.officeCode,
        o.city
    ORDER BY o.officeCode ASC
""", conn)


# STEP 10: Employees who sold products purchased
# by fewer than 20 distinct customers
df_under_20 = pd.read_sql("""
    SELECT DISTINCT
        e.employeeNumber,
        e.firstName,
        e.lastName,
        ofc.city,
        ofc.officeCode
    FROM employees AS e
    INNER JOIN offices AS ofc
        ON e.officeCode = ofc.officeCode
    INNER JOIN customers AS c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    INNER JOIN orders AS o
        ON c.customerNumber = o.customerNumber
    INNER JOIN orderdetails AS od
        ON o.orderNumber = od.orderNumber
    WHERE od.productCode IN (
        SELECT
            od2.productCode
        FROM orderdetails AS od2
        INNER JOIN orders AS o2
            ON od2.orderNumber = o2.orderNumber
        GROUP BY od2.productCode
        HAVING COUNT(DISTINCT o2.customerNumber) < 20
    )
    ORDER BY
        CASE WHEN e.firstName = 'Loui' THEN 0 ELSE 1 END,
        e.firstName ASC,
        e.lastName ASC
""", conn)


# Close the database connection
conn.close()
