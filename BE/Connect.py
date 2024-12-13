import pyodbc
import pandas as pd
import bcrypt

server = 'DESKTOP-7HBAE21'
database = 'HSNV'
username = ''
password = ''

connection_String = f'DRIVER={{SQL SERVER}};SERVER={server};DATABASE={database};UID={username};password={password}'

try:
    # Kết nối đến SQL Server
    conn = pyodbc.connect(connection_String)
    print("Kết nối SQL Server thành công!")

    # Thực hiện một truy vấn SQL
    query = "SELECT * FROM HSNV;"  # Thay 'HSNV' bằng tên bảng trong cơ sở dữ liệu của bạn
    query1 = "SELECT * FROM Account;"
    query2 = "SELECT * FROM AdminPasswords;"

    df = pd.read_sql(query, conn)
    df1 = pd.read_sql(query1, conn)
    df2 = pd.read_sql(query2, conn)

    # Xóa khoảng trắng và ký tự không mong muốn
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Hiển thị dữ liệu
    print(df)
    print(df1)
    print(df2)

except pyodbc.Error as e:
    print(f'Error: {e}')
finally:
    if conn:
        conn.close()

# try:
#     # Kết nối tới SQL Server
#     conn = pyodbc.connect(connection_String)
#     cursor = conn.cursor()

#     # Tạo bảng (nếu chưa có)
#     cursor.execute('''
#     IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Account' AND xtype='U')
#     CREATE TABLE Account (
#         username NVARCHAR(50) PRIMARY KEY,
#         hashed_password NVARCHAR(255) NOT NULL,
#         role NVARCHAR(20) NOT NULL
#     )
#     ''')

#     # Danh sách người dùng 
#     users = [
#         {"username": "NguyenAnhTuan", "password": "nguyen123", "role": "admin"},
#         {"username": "TranMinhHoang", "password": "tran456", "role": "user"},
#         {"username": "LeThiThanh", "password": "leth789", "role": "user"},
#         {"username": "PhamLanHuong", "password": "pham234", "role": "user"},
#         {"username": "VuVanDung", "password": "vudung567", "role": "user"},
#         {"username": "DangThiMai", "password": "dang890", "role": "admin"},
#         {"username": "LyQuocBao", "password": "lybao345", "role": "user"},
#         {"username": "NguyenThiHanh", "password": "nguyen678", "role": "user"},
#         {"username": "TranVanQuan", "password": "tran901", "role": "user"},
#         {"username": "PhamThiYen", "password": "pham234", "role": "user"},
#         {"username": "HoMinhTam", "password": "ho567", "role": "user"},
#         {"username": "LeThanhPhong", "password": "le890", "role": "user"},
#         {"username": "DoHoangYen", "password": "do123", "role": "user"},
#         {"username": "LeVanHung", "password": "lev456", "role": "user"},
#         {"username": "NguyenMinhChau", "password": "nguyen789", "role": "user"},
#         {"username": "PhamVanThanh", "password": "pham012", "role": "admin"},
#         {"username": "DinhThiNga", "password": "dinh345", "role": "user"},
#         {"username": "BuiThanhHai", "password": "bui678", "role": "user"},
#         {"username": "VoNgocAnh", "password": "vo901", "role": "user"},
#         {"username": "DangVanLong", "password": "dang234", "role": "user"},
#     ]

#     # Mã hóa mật khẩu và lưu vào cơ sở dữ liệu
#     for user in users:
#         username = user["username"]
#         plain_password = user["password"]
#         role = user["role"]

#         # Mã hóa mật khẩu
#         hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

#         # Chèn tài khoản vào cơ sở dữ liệu
#         try:
#             cursor.execute("INSERT INTO Account (username, hashed_password, role) VALUES (?, ?, ?)",
#                            (username, hashed_password, role))
#             print(f"Tài khoản {username} đã được tạo.")
#         except pyodbc.IntegrityError:
#             print(f"Tài khoản {username} đã tồn tại.")

#     # Lưu thay đổi và đóng kết nối
#     conn.commit()
# except pyodbc.Error as e:
#     print(f"Error: {e}")
# finally:
#     if conn:
#         conn.close()

# try:
#     # Kết nối đến SQL Server
#     conn = pyodbc.connect(connection_String)
#     print("Kết nối SQL Server thành công!")
    
#     cursor = conn.cursor()

#     # Tạo bảng AdminPasswords (nếu chưa có)
#     cursor.execute('''
#     IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AdminPasswords' AND xtype='U')
#     CREATE TABLE AdminPasswords (
#         name NVARCHAR(50) PRIMARY KEY,
#         adminpassword NVARCHAR(255) NOT NULL
#     )
#     ''')

#     # Danh sách các admin
#     admins = [
#         {"name": "NguyenAnhTuan", "password": "password1"},
#         {"name": "DangThiMai", "password": "password2"},
#         {"name": "PhamVanThanh", "password": "password3"}
#     ]

#     # Mã hóa mật khẩu và lưu vào cơ sở dữ liệu
#     for admin in admins:
#         name = admin["name"]
#         plain_password = admin["password"]

#         # Mã hóa mật khẩu
#         encrypted_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

#         # Chèn tài khoản vào cơ sở dữ liệu
#         try:
#             cursor.execute("INSERT INTO AdminPasswords (name, adminpassword) VALUES (?, ?)",
#                            (name, encrypted_password))
#             print(f"Tài khoản {name} đã được tạo.")
#         except pyodbc.IntegrityError:
#             print(f"Tài khoản {name} đã tồn tại.")

#     # Lưu thay đổi và đóng kết nối
#     conn.commit()
# except pyodbc.Error as e:
#     print(f"Error: {e}")
# finally:
#     if conn:
#         conn.close()