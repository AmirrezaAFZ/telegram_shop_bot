import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        user='root',
        password='password',
        host='localhost',
        database='alpha_store'
    )

def insert_user_info(cid, first_name, last_name,phone_number, username=None, email=None, privilage='user'):
    conn=mysql.connector.connect(user='root',password='password',host='localhost',database='shop')
    cursor=conn.cursor()
    command ="""insert ignore into user (cid, first_name, last_name, username, phone_number, email, privilage)
    VALUES (%s,%s,%s,%s,%s,%s,%s);"""
    cursor.execute(command,(cid, first_name, last_name, username, phone_number, email, privilage))
    conn.commit()
    cursor.close()
    conn.close()
    print('value inserted to user table')


def insert_product_info(name, brand ,description, image_file_id, price, inventory, category):
    conn=mysql.connector.connect(user='root',password='password',host='localhost',database='shop')
    cursor=conn.cursor()
    command="""insert into product (name, brand ,description, image_file_id, price, inventory, category)
    VALUES (%s,%s,%s,%s,%s,%s,%s);"""
    cursor.execute(command,(name, brand ,description, image_file_id, price, inventory, category))
    conn.commit()
    cursor.close()
    conn.close()
    print('value inserted to product table')


def create_sale(user_cid):
    conn=mysql.connector.connect(user='root',password='password',host='localhost',database='shop')
    cursor = conn.cursor()
    command = "insert into sale (user_cid) VALUES (%s)"
    cursor.execute(command, (user_cid,))
    sale_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return sale_id

def create_sale_row(sale_id, product_id, quantity):
    conn=mysql.connector.connect(user='root',password='password',host='localhost',database='shop')
    cursor = conn.cursor()
    command = "insert into sale_row (sale_id, product_id, quantity) VALUES (%s, %s, %s)"
    cursor.execute(command, (sale_id, product_id, quantity))
    conn.commit()
    cursor.close()
    conn.close()

