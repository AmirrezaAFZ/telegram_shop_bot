
import mysql.connector

def create_database_shop () :
    conn = mysql.connector.connect(user='root', password='password', host='localhost')
    cursor = conn.cursor()
    cursor.execute("create database  if not exists shop ")
    cursor.close()
    conn.close


def create_table() :
    conn = mysql.connector.connect(user='root', password='password', host='localhost', database = 'shop')
    cursor = conn.cursor()
    command_1 = """create table if not exists user (cid bigint primary key not null,first_name varchar(12),last_name varchar(20),username varchar (20),phone_number varchar(20),email varchar(30), privilage ENUM ('user','admin'));"""
    cursor.execute(command_1)
    command_3  = """create table if not exists product(id int primary key not null auto_increment,brand varchar(50) not null,name varchar(100),price  bigint,inventory int not null default 0,image_file_id varchar(150), category Enum('cpu','gpu'), description varchar(200));""" 
    cursor.execute(command_3)
    command_4 =   """create table if not exists sale(id int not null auto_increment,user_cid bigint not null,date datetime not null default current_timestamp,primary key (id),foreign key (user_cid) references user(cid));  """
    cursor.execute(command_4)
    command_5 =  """   create table if not exists sale_row(sale_id int not null,product_id int not null,quantity int not null,foreign key (sale_id) references sale(id),foreign key (product_id) references product(id));  """
    cursor.execute(command_5)
    cursor.close()
    conn.close
create_database_shop()
create_table()

