import bcrypt
from Login import login  
from GetData import get_hsnv_data, get_account_data, get_admin_passwords_data
from Encypt_data import decrypt_aes_key, encrypt_aes, encrypt_hsnv_data, decrypt_hsnv_data
import pyodbc
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os


# Kết nối tới cơ sở dữ liệu
server = 'DESKTOP-7HBAE21'
database = 'HSNV'
username = ''
password = ''
connection_String = f'DRIVER={{SQL SERVER}};SERVER={server};DATABASE={database};UID={username};password={password}'

def verify_admin_password(input_password):
    """
    Kiểm tra mật khẩu admin với mật khẩu đã mã hóa trong bảng AdminPasswords
    """
    try:
        # Kết nối cơ sở dữ liệu
        conn = pyodbc.connect(connection_String)
        cursor = conn.cursor()

        # Lấy mật khẩu đã mã hóa từ bảng AdminPasswords
        query = "SELECT adminpassword FROM AdminPasswords"  # Giả sử chỉ có một dòng duy nhất
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            hashed_password = result[0]
            # Kiểm tra mật khẩu nhập vào có khớp với mật khẩu đã mã hóa không
            if bcrypt.checkpw(input_password.encode('utf-8'), hashed_password.encode('utf-8')):
                return True
            else:
                print("Mật khẩu không đúng.")
                return False
        else:
            print("Không tìm thấy mật khẩu admin trong cơ sở dữ liệu.")
            return False

    except pyodbc.Error as e:
        print(f"Lỗi kết nối cơ sở dữ liệu: {e}")
        return False

    except Exception as e:
        print(f"Lỗi: {e}")
        return False

    finally:
        if conn:
            conn.close()

def add_employee(hoTen, chucVu, phongBan, soDienThoai, email, diaChi, adminPassword):
    """
    Thêm nhân viên mới vào cơ sở dữ liệu
    """
    conn = None
    keyAES = None  # Khởi tạo keyAES mặc định

    try:
        if verify_admin_password(adminPassword): 
            df = get_admin_passwords_data()

            # Kiểm tra xem df có chứa dữ liệu không
            if not df.empty and 'hashed_keyAES' in df.columns:
                hashed_keyAES = df['hashed_keyAES'].iloc[0]
                keyAES = decrypt_aes_key(hashed_keyAES, adminPassword)
            else:
                raise ValueError("Không tìm thấy dữ liệu khóa AES trong cơ sở dữ liệu.")
        else:
            print("Mật khẩu không đúng!")
            return  

        # Kiểm tra xem keyAES có hợp lệ không
        if keyAES is None:
            raise ValueError("Khóa AES không hợp lệ!")

        # Mã hóa số điện thoại và địa chỉ
        encrypted_soDienThoai = encrypt_aes(soDienThoai, keyAES)
        encrypted_diaChi = encrypt_aes(diaChi, keyAES)

        # Kết nối cơ sở dữ liệu
        conn = pyodbc.connect(connection_String)
        cursor = conn.cursor()

        # Thêm thông tin nhân viên vào cơ sở dữ liệu
        query = """
        INSERT INTO [HSNV] ([Họ tên], [Chức vụ], [Phòng ban], [Số điện thoại], [Email], [Địa chỉ])
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (hoTen, chucVu, phongBan, encrypted_soDienThoai, email, encrypted_diaChi))
        conn.commit()

        print("Thêm nhân viên thành công!")

    except pyodbc.Error as e:
        print(f"Lỗi kết nối cơ sở dữ liệu: {e}")

    except ValueError as e:
        print(f"Lỗi: {e}")

    except Exception as e:
        print(f"Lỗi không xác định: {e}")

    finally:
        if conn:
            conn.close()

def delete_employee_by_id(employee_id, admin_password):
    """
    Xóa nhân viên khỏi cơ sở dữ liệu dựa trên Id và kiểm tra mật khẩu admin
    """
    if not verify_admin_password(admin_password):
        print("Xóa nhân viên thất bại do mật khẩu admin không đúng.")
        return

    try:
        # Kết nối cơ sở dữ liệu
        conn = pyodbc.connect(connection_String)
        cursor = conn.cursor()

        # Kiểm tra xem nhân viên có tồn tại không với Id
        query_check = "SELECT COUNT(*) FROM [HSNV] WHERE [Id] = ?"
        cursor.execute(query_check, (employee_id,))
        result = cursor.fetchone()

        if result[0] == 0:
            print(f"Không tìm thấy nhân viên với Id {employee_id}.")
            return

        # Xóa nhân viên khỏi cơ sở dữ liệu
        query_delete = "DELETE FROM [HSNV] WHERE [Id] = ?"
        cursor.execute(query_delete, (employee_id,))
        conn.commit()

        print(f"Xóa nhân viên với Id {employee_id} thành công!")

    except pyodbc.Error as e:
        print(f"Lỗi kết nối cơ sở dữ liệu: {e}")

    except Exception as e:
        print(f"Lỗi: {e}")

    finally:
        if conn:
            conn.close()

def update_employee_info(employee_id, hoTen, chucVu, phongBan, soDienThoai, email, diaChi, adminPassword):
    """
    Sửa thông tin nhân viên dựa trên Id và kiểm tra mật khẩu admin.
    """
    # Kiểm tra mật khẩu admin
    if not verify_admin_password(adminPassword):
        print("Cập nhật thông tin thất bại do mật khẩu admin không đúng.")
        return

    conn = None
    try:
        # Lấy dữ liệu khóa AES từ cơ sở dữ liệu
        df = get_admin_passwords_data()
        
        # Kiểm tra dữ liệu khóa AES
        if df.empty or 'hashed_keyAES' not in df.columns:
            print("Không tìm thấy dữ liệu khóa AES trong cơ sở dữ liệu.")
            return

        # Giải mã khóa AES
        hashed_keyAES = df['hashed_keyAES'].iloc[0]
        keyAES = decrypt_aes_key(hashed_keyAES, adminPassword)

        # Kiểm tra khóa AES có hợp lệ không
        if not keyAES:
            print("Khóa AES không hợp lệ!")
            return

        # Kết nối cơ sở dữ liệu
        conn = pyodbc.connect(connection_String)
        cursor = conn.cursor()

        # Kiểm tra xem nhân viên có tồn tại không với Id
        query_check = "SELECT COUNT(*) FROM [HSNV] WHERE [Id] = ?"
        cursor.execute(query_check, (employee_id,))
        result = cursor.fetchone()

        if result[0] == 0:
            print(f"Không tìm thấy nhân viên với Id {employee_id}.")
            return

        # Tạo danh sách các trường cần cập nhật
        updates = []
        params = []

        if hoTen:
            updates.append("[Họ tên] = ?")
            params.append(hoTen)
        if chucVu:
            updates.append("[Chức vụ] = ?")
            params.append(chucVu)
        if phongBan:
            updates.append("[Phòng ban] = ?")
            params.append(phongBan)
        
        # Mã hóa số điện thoại và địa chỉ nếu có
        if soDienThoai:
            encrypted_soDienThoai = encrypt_aes(soDienThoai, keyAES)
            updates.append("[Số điện thoại] = ?")
            params.append(encrypted_soDienThoai)
        
        if email:
            updates.append("[Email] = ?")
            params.append(email)
        
        if diaChi:
            encrypted_diaChi = encrypt_aes(diaChi, keyAES)
            updates.append("[Địa chỉ] = ?")
            params.append(encrypted_diaChi)

        # Kiểm tra xem có trường nào cần cập nhật không
        if not updates:
            print("Không có thông tin nào để cập nhật.")
            return

        # Tạo câu truy vấn cập nhật
        query_update = f"UPDATE [HSNV] SET {', '.join(updates)} WHERE [Id] = ?"
        params.append(employee_id)

        # Thực hiện cập nhật
        cursor.execute(query_update, params)
        conn.commit()

        print(f"Cập nhật thông tin nhân viên với Id {employee_id} thành công!")

    except pyodbc.Error as e:
        print(f"Lỗi kết nối cơ sở dữ liệu: {e}")

    except Exception as e:
        print(f"Lỗi không xác định: {e}")

    finally:
        if conn:
            conn.close()

