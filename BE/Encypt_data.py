from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import hashlib

# Sinh khóa AES 256-bit từ mật khẩu mã hóa
def generate_aes_key_from_password(password):
    """
    Sinh khóa AES từ mật khẩu mã hóa bằng cách băm mật khẩu.
    """
    return hashlib.sha256(password.encode('utf-8')).digest()

# Mã hóa dữ liệu với AES
def encrypt_aes(data, key):
    """
    Mã hóa dữ liệu bằng AES.
    """
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')

# Giải mã dữ liệu với AES
def decrypt_aes(encrypted_data, key):
    """
    Giải mã dữ liệu AES.
    """
    raw_data = base64.b64decode(encrypted_data)
    nonce, tag, ciphertext = raw_data[:16], raw_data[16:32], raw_data[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')

# Lưu trữ mật khẩu mã hóa dưới dạng băm (hash) (trong thực tế, sẽ lưu trữ ở nơi an toàn)
stored_password_hash = hashlib.sha256("admin_password".encode('utf-8')).digest()

# Hàm kiểm tra mật khẩu của admin
def check_admin_password(input_password):
    """
    Kiểm tra mật khẩu của admin có đúng không.
    """
    input_password_hash = hashlib.sha256(input_password.encode('utf-8')).digest()
    if input_password_hash == stored_password_hash:
        return True
    return False

# Ví dụ sử dụng
input_password = input("Nhập mật khẩu mã hóa của admin: ")

# Kiểm tra mật khẩu
if check_admin_password(input_password):
    print("Mật khẩu đúng, bạn có thể tiếp tục.")
    
    # Tạo khóa AES từ mật khẩu đúng
    aes_key = generate_aes_key_from_password(input_password)

    # Mã hóa dữ liệu
    data = "Dữ liệu bí mật"
    encrypted_data = encrypt_aes(data, aes_key)
    print(f"Dữ liệu đã mã hóa: {encrypted_data}")

    # Giải mã dữ liệu
    decrypted_data = decrypt_aes(encrypted_data, aes_key)
    print(f"Dữ liệu đã giải mã: {decrypted_data}")
else:
    print("Mật khẩu sai! Không thể tiếp tục.")
