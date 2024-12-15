import pyodbc
import pandas as pd

server = 'DESKTOP-7HBAE21'
database = 'HSNV'
username = ''
password = ''

connection_String = f'DRIVER={{SQL SERVER}};SERVER={server};DATABASE={database};UID={username};password={password}'

# Hàm lấy dữ liệu từ bảng HSNV
def get_hsnv_data():
    try:
        conn = pyodbc.connect(connection_String)  # Kết nối đến SQL Server
        # print("Kết nối SQL Server thành công!")

        query = "SELECT * FROM HSNV;"  # Truy vấn dữ liệu từ bảng HSNV
        df = pd.read_sql(query, conn)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Xóa khoảng trắng và ký tự không mong muốn
        conn.close()  # Đóng kết nối
        print(df)
        return df
    except pyodbc.Error as e:
        print(f"Error khi lấy dữ liệu từ bảng HSNV: {e}")
        return None

# Hàm lấy dữ liệu từ bảng Account
def get_account_data():
    try:
        conn = pyodbc.connect(connection_String)  # Kết nối đến SQL Server
        # print("Kết nối SQL Server thành công!")

        query = "SELECT * FROM Account;"  # Truy vấn dữ liệu từ bảng Account
        df = pd.read_sql(query, conn)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Xóa khoảng trắng và ký tự không mong muốn
        conn.close()  # Đóng kết nối
        # print(df)
        return df
    except pyodbc.Error as e:
        print(f"Error khi lấy dữ liệu từ bảng Account: {e}")
        return None

# Hàm lấy dữ liệu từ bảng AdminPasswords
def get_admin_passwords_data():
    try:
        conn = pyodbc.connect(connection_String)  # Kết nối đến SQL Server
        # print("Kết nối SQL Server thành công!")

        query = "SELECT * FROM AdminPasswords;"  # Truy vấn dữ liệu từ bảng AdminPasswords
        df = pd.read_sql(query, conn)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Xóa khoảng trắng và ký tự không mong muốn
        conn.close()  # Đóng kết nối
        # print(df)
        return df
    except pyodbc.Error as e:
        print(f"Error khi lấy dữ liệu từ bảng AdminPasswords: {e}")
        return None


