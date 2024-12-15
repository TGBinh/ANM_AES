import os
import pandas as pd
import pyodbc
import base64
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

server = 'DESKTOP-7HBAE21'
database = 'HSNV'
username = ''
password = ''

connection_String = f'DRIVER={{SQL SERVER}};SERVER={server};DATABASE={database};UID={username};password={password}'


# Tạo khóa AES ngẫu nhiên
def generate_random_aes_key():
    return os.urandom(32)  # 256-bit AES key

# Tạo khóa mã hóa từ mật khẩu admin
def derive_key_from_password(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

# Mã hóa khóa AES
def encrypt_aes_key(aes_key: bytes, password: str):
    salt = os.urandom(16)  # Salt ngẫu nhiên
    derived_key = derive_key_from_password(password, salt)
    
    iv = os.urandom(16)  # Initialization vector (IV)
    cipher = Cipher(algorithms.AES(derived_key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_aes_key = encryptor.update(aes_key) + encryptor.finalize()
    
    # Lưu trữ salt và iv cùng với khóa đã mã hóa
    return base64.b64encode(salt + iv + encrypted_aes_key).decode()

def decrypt_aes_key(encrypted_data: str, password: str):
    decoded_data = base64.b64decode(encrypted_data)
    salt = decoded_data[:16]
    iv = decoded_data[16:32]
    encrypted_aes_key = decoded_data[32:]
    
    derived_key = derive_key_from_password(password, salt)
    cipher = Cipher(algorithms.AES(derived_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    try:
        aes_key = decryptor.update(encrypted_aes_key) + decryptor.finalize()
        return aes_key
    except Exception:
        raise ValueError("Mật khẩu không chính xác hoặc dữ liệu mã hóa bị lỗi!")


    
def encrypt_aes(data, key):
    if not isinstance(data, str):
        data = str(data)  # Ensure data is a string
    
    # Ensure the key is in bytes format, if it's a string
    if isinstance(key, str):
        key = key.encode('utf-8')  # Convert string key to bytes
    
    # Add padding to the data to make its length a multiple of 16
    data_padded = pad(data.encode('utf-8'), AES.block_size)

    # Generate a random IV for each encryption
    iv = os.urandom(16)  # 16 bytes IV
    cipher = AES.new(key, AES.MODE_CBC, iv)  # Use CBC mode for encryption
    
    # Encrypt the data
    encrypted_data = cipher.encrypt(data_padded)
    
    # Return the IV + encrypted data, base64 encoded
    return base64.b64encode(iv + encrypted_data).decode('utf-8')

def encrypt_hsnv_data(key):
    try:
        conn = pyodbc.connect(connection_String)  
        cursor = conn.cursor()
       
        # Truy vấn dữ liệu từ bảng HSNV
        query = "SELECT * FROM HSNV;"
        df = pd.read_sql(query, conn)

        # Kiểm tra và mã hóa cột 'Số điện thoại' và 'Địa chỉ'
        if 'Số điện thoại' in df.columns:
            df['Số điện thoại'] = df['Số điện thoại'].apply(lambda x: encrypt_aes(str(x), key) if pd.notnull(x) else x)
        if 'Địa chỉ' in df.columns:
            df['Địa chỉ'] = df['Địa chỉ'].apply(lambda x: encrypt_aes(str(x), key) if pd.notnull(x) else x)

        # Cập nhật lại dữ liệu đã mã hóa vào bảng HSNV
        for index, row in df.iterrows():
            update_query = """
            UPDATE HSNV
            SET [Số điện thoại] = ?, [Địa chỉ] = ?
            WHERE [Id] = ?
            """
            cursor.execute(update_query, row['Số điện thoại'], row['Địa chỉ'], row['Id'])

        conn.commit()  
        conn.close()  
        print("Dữ liệu đã được mã hóa và cập nhật vào bảng HSNV thành công!")
        print(df)
        return df
    except pyodbc.Error as e:
        print(f"Lỗi khi xử lý dữ liệu từ bảng HSNV: {e}")
        return None
    
    
def decrypt_aes(encrypted_text, key):
    try:
        # Giải mã chuỗi đã mã hóa từ base64
        encrypted_data = base64.b64decode(encrypted_text)

        # Kiểm tra nếu key không phải là bytes, chuyển đổi sang bytes
        if not isinstance(key, bytes):
            key = key.encode('utf-8')

        # Lấy IV từ dữ liệu mã hóa (16 byte đầu tiên)
        iv = encrypted_data[:16]
        encrypted_data = encrypted_data[16:]

        # Tạo cipher object từ key và IV (chế độ CBC)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Giải mã dữ liệu
        decrypted_data = cipher.decrypt(encrypted_data)

        # Loại bỏ padding (PKCS7)
        padding_length = decrypted_data[-1]
        decrypted_data = decrypted_data[:-padding_length]

        # Chuyển đổi từ bytes sang chuỗi
        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"Lỗi khi giải mã AES: {e}")
        return None
    
def decrypt_hsnv_data(key):
    try:
        conn = pyodbc.connect(connection_String)  
        cursor = conn.cursor()

        # Truy vấn dữ liệu từ bảng HSNV
        query = "SELECT * FROM HSNV;"
        df = pd.read_sql(query, conn)

        # Kiểm tra và giải mã cột 'Số điện thoại' và 'Địa chỉ'
        if 'Số điện thoại' in df.columns:
            df['Số điện thoại'] = df['Số điện thoại'].apply(lambda x: decrypt_aes(str(x), key) if pd.notnull(x) else x)
        if 'Địa chỉ' in df.columns:
            df['Địa chỉ'] = df['Địa chỉ'].apply(lambda x: decrypt_aes(str(x), key) if pd.notnull(x) else x)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        # Đóng kết nối
        conn.close()

        # Trả về DataFrame chứa dữ liệu đã giải mã
        print("Dữ liệu đã được giải mã thành công!")
        print(df)
        return df
    except pyodbc.Error as e:
        print(f"Lỗi khi truy vấn dữ liệu từ bảng HSNV: {e}")
        return None
    except Exception as ex:
        print(f"Lỗi trong quá trình giải mã: {ex}")
        return None