# main.py

from Login import login  

def main():
    # Nhập tên người dùng và mật khẩu từ người dùng
    username_input = input("Nhập tên người dùng: ")
    password_input = input("Nhập mật khẩu: ")

    # Gọi hàm đăng nhập
    login(username_input, password_input)

if __name__ == "__main__":
    main()
