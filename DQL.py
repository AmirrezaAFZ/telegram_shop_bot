import mysql.connector

def get_product():
    conn=mysql.connector.connect(user='root',password='password',host='localhost',database='shop')
    cursor=conn.cursor(dictionary=True)
    command="SELECT * FROM product"
    cursor.execute(command)
    result=cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_products_by_category(category):
    conn=mysql.connector.connect(user='root',password='password',host='localhost',database='shop')
    cursor = conn.cursor(dictionary=True)
    command = "SELECT * FROM product WHERE category = %s"
    cursor.execute(command, (category,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def update_product_inventory(product_id, quantity):
    conn=mysql.connector.connect(user='root',password='password',host='localhost',database='shop')
    cursor = conn.cursor()
    command = "UPDATE product SET inventory = inventory - %s WHERE id = %s"
    cursor.execute(command, (quantity, product_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_products_by_brand(brand):
    conn = mysql.connector.connect(user='root', password='password', host='localhost', database='shop')
    cursor = conn.cursor(dictionary=True)
    command = "SELECT * FROM product WHERE  brand = %s"
    cursor.execute(command , (brand,))
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products




def create_or_update_sale_row(sale_id, product_id, quantity):
    conn=mysql.connector.connect(user='root',password='password',host='localhost',database='shop')
    cursor = conn.cursor()
    SQL_SELECT = "SELECT quantity FROM sale_row WHERE sale_id = %s AND product_id = %s"
    cursor.execute(SQL_SELECT, (sale_id, product_id))
    result = cursor.fetchone()
    if result:
        new_quantity = result[0] + quantity
        SQL_UPDATE = "UPDATE sale_row SET quantity = %s WHERE sale_id = %s AND product_id = %s"
        cursor.execute(SQL_UPDATE, (new_quantity, sale_id, product_id))
    else:
        SQL_INSERT = "INSERT INTO sale_row (sale_id, product_id, quantity) VALUES (%s, %s, %s)"
        cursor.execute(SQL_INSERT, (sale_id, product_id, quantity))
    conn.commit()
    cursor.close()
    conn.close()



