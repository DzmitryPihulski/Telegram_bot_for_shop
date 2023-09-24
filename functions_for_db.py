import pyodbc

def make_db(db_name) -> str:
    try:
        cnxn_str = ("Driver={ODBC Driver 17 for SQL Server};"
                "Server=PIHU\SQLEXPRESS;"
                "Trusted_Connection=yes;"
                   )
        cnxn = pyodbc.connect(cnxn_str,autocommit=True)
        querry = """\
        CREATE DATABASE {}""".format(db_name)
        cursor = cnxn.cursor()
        cursor.execute(querry)
    except pyodbc.Error as ex:
        return f"The error '{ex}' occurred"
    return "Success"

def make_connection_todb(db_name):
    try:
        connection_str = "Driver={};Server=PIHU\SQLEXPRESS;Database={};Trusted_Connection=yes;".format('ODBC Driver 17 for SQL Server',db_name)
        connection = pyodbc.connect(connection_str,autocommit=True)
    except pyodbc.Error as ex:
        print(f"The error '{ex}' occurred")
    return connection

##making tables
def make_table_Users_in_db(connection) -> str:
    try:
        querry = """create table Users(
    user_id BIGINT NOT NULL,
    username VARCHAR(100) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    PRIMARY KEY ( user_id )
    );"""
        cursor = connection.cursor()
        cursor.execute(querry)
    except pyodbc.Error as ex:
        return f"The error '{ex}' occurred"
    return "Success"

def make_table_Products_in_db(connection) -> str:
    try:
        querry = """create table Products(
    product_id INT IDENTITY NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    description VARCHAR(100),
    foto VARCHAR(255),
    amount INT NOT NULL,
    Awailable BIT NOT NULL, 
    PRIMARY KEY ( product_id )
    );"""
        cursor = connection.cursor()
        cursor.execute(querry)
    except pyodbc.Error as ex:
        return f"The error '{ex}' occurred"
    return "Success"

def make_table_Orders_in_db(connection) -> str:
    try:
        querry = """create table Orders(
    user_id BIGINT NOT NULL,
    username VARCHAR(100) NOT NULL,
    product_id INT NOT NULL,
    amount INT NOT NULL,
    adress VARCHAR(255) NOT NULL,
    date_of_order SMALLDATETIME NOT NULL
    );"""
        cursor = connection.cursor()
        cursor.execute(querry)
    except pyodbc.Error as ex:
        return f"The error '{ex}' occurred"
    return "Success"

def make_table_Admins_in_db(connection) -> str:
    try:
        querry = """create table Admins(
    user_id BIGINT NOT NULL,
    username VARCHAR(100) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    PRIMARY KEY ( user_id )
    );"""
        cursor = connection.cursor()
        cursor.execute(querry)
    except pyodbc.Error as ex:
        return f"The error '{ex}' occurred"
    return "Success"
##make all 4 tables
def make_tables(connection) -> list:
    users_table = make_table_Users_in_db(connection)
    products_table = make_table_Products_in_db(connection)
    orders_table = make_table_Orders_in_db(connection)
    admins_table = make_table_Admins_in_db(connection)
    return [users_table, products_table, orders_table, admins_table]

##Make records in tables
def insert_into_table_Products(*values) -> str:
    connection = make_connection_todb('ShopDB')
    a = list(values[0].text.split(','))
    for i in range(len(a)):
        try:
            a[0] = int(a[0])
        except:
            pass
    querry = """INSERT INTO {} VALUES {};""".format("Products",tuple(a))
    try:
        cursor = connection.cursor()
        cursor.execute(querry)
    except pyodbc.Error as ex:
        print(f"The error '{ex}' occurred")
    return "Success"

def insert_into_table_Orders(*values) -> str:
    connection = make_connection_todb('ShopDB')
    querry = """INSERT INTO {} VALUES {};""".format("Orders",tuple(values[0]))
    try:
        cursor = connection.cursor()
        cursor.execute(querry)
    except pyodbc.Error as ex:
        print(f"The error '{ex}' occurred")
    return "Success"

def delete_from_table_Products(id) -> str:
    connection = make_connection_todb('ShopDB')
    querry = """DELETE FROM {} WHERE product_id={};""".format("Products",int(id.text))
    try:
        cursor = connection.cursor()
        cursor.execute(querry)
    except pyodbc.Error as ex:
        print(f"The error '{ex}' occurred")
    return "Success"

##Find chat id by username
def admin_chat(admin_username):
    connection = make_connection_todb('ShopDB')
    querry = """SELECT * FROM ADMINS WHERE username='{}';""".format(admin_username)
    try:
        cursor = connection.cursor()
        rows = cursor.execute(querry).fetchall()
    except pyodbc.Error as ex:
        return f"The error '{ex}' occurred"
    return int(rows[0].user_id)

##Find products
def all_products():
    connection = make_connection_todb('ShopDB')
    querry = """SELECT * FROM PRODUCTS;"""
    try:
        cursor = connection.cursor()
        rows = cursor.execute(querry).fetchall()
    except pyodbc.Error as ex:
        return f"The error '{ex}' occurred"
    
    answer = list()
    for r in rows:
        answer.append([f"""Product name:{r.product_name}\nDescription:{r.description}\nPrice:{r.product_price}\nProduct id={r.product_id}\nAmount={r.amount}\nAwailable={r.Awailable}\n[‌‌]({r.foto})"""])
    return answer

##Find all orders
def all_orders():
    connection = make_connection_todb('ShopDB')
    querry = """SELECT * FROM Orders;"""
    try:
        cursor = connection.cursor()
        rows = cursor.execute(querry).fetchall()
    except pyodbc.Error as ex:
        return f"The error '{ex}' occurred"
    
    answer = list()
    for r in rows:
        answer.append([f"""User id:{r.user_id}\nUsername: @{r.username}\nProduct id:{r.product_id}\nAmount: {r.amount}\nAdress: {r.adress}\nDate of order: {r.date_of_order}"""])
    return answer

##Find awailable products
def all_awailable_products():
    connection = make_connection_todb('ShopDB')
    querry = """SELECT * FROM PRODUCTS WHERE Awailable=1;"""
    try:
        cursor = connection.cursor()
        rows = cursor.execute(querry).fetchall()
    except pyodbc.Error as ex:
        return f"The error '{ex}' occurred"
    
    answer = list()
    for r in rows:
        answer.append([f"""Product name {r.product_name}\n {r.description}\n Price {r.product_price}$\n[‌‌]({r.foto})"""])
    return answer

def get_names_of_awailable_products():
    connection = make_connection_todb('ShopDB')
    querry = """SELECT * FROM PRODUCTS WHERE Awailable=1;"""
    try:
        cursor = connection.cursor()
        rows = cursor.execute(querry).fetchall()
    except pyodbc.Error as ex:
        return f"The error '{ex}' occurred"
    answer = list()
    for r in rows:
        answer.append(f"""{r.product_name}""")
    return answer

#Get id of product by product name
def get_id_of_product(product_name):
    connection = make_connection_todb('ShopDB')
    querry = """SELECT * FROM PRODUCTS WHERE product_name='{}';""".format(str(product_name))
    try:
        cursor = connection.cursor()
        rows = cursor.execute(querry).fetchall()
    except pyodbc.Error as ex:
        return f"The error '{ex}' occurred"
    return int(rows[0].product_id)

#Find all users
def all_users():
    connection = make_connection_todb('ShopDB')
    querry = """SELECT * FROM Users;"""
    try:
        cursor = connection.cursor()
        rows = cursor.execute(querry).fetchall()
    except pyodbc.Error as ex:
        return f"The error '{ex}' occurred"
    
    answer = str()
    for r in rows:
        answer += f"""{r.user_id}, @{r.username}, {r.first_name}, {r.last_name}\n"""
    return answer
