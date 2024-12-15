# login.py
import streamlit as st
import bcrypt
import pyodbc

# Kết nối đến cơ sở dữ liệu SQL Server
server = 'DESKTOP-7HBAE21'
database = 'HSNV'
username = ''  
password = ''  

connection_string = f'DRIVER={{SQL SERVER}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def authenticate_user(username_input, password_input):
    try:
        # Kết nối đến cơ sở dữ liệu
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Kiểm tra tên người dùng có trong cơ sở dữ liệu không
        cursor.execute("SELECT hashed_password, role FROM Account WHERE username = ?", (username_input,))
        row = cursor.fetchone()

        if row:
            stored_hashed_password = row[0]  # Mật khẩu đã mã hóa trong cơ sở dữ liệu
            user_role = row[1]  # Vai trò người dùng

            # So sánh mật khẩu người dùng nhập với mật khẩu đã mã hóa trong cơ sở dữ liệu
            if bcrypt.checkpw(password_input.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                return True, user_role
            else:
                return False, "Mật khẩu không đúng!"
        else:
            return False, "Tên người dùng không tồn tại!"

    except pyodbc.Error as e:
        return False, f"Lỗi kết nối cơ sở dữ liệu: {e}"

    finally:
        if conn:
            conn.close()


