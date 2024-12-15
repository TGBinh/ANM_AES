# main.py
import streamlit as st
import ast
from Login import authenticate_user 
from GetData import get_hsnv_data, get_account_data, get_admin_passwords_data
from Encypt_data import decrypt_aes_key, encrypt_hsnv_data, decrypt_hsnv_data
from Manage import verify_admin_password, add_employee, delete_employee_by_id, update_employee_info


# Hàm đăng nhập
def login():
    st.title("Đăng nhập")

    # Giao diện nhập thông tin đăng nhập
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")

    if st.button("Đăng nhập"):
        if username and password:
            # Xác thực người dùng
            success, message = authenticate_user(username, password)
            if success:
                # Lưu thông tin đăng nhập vào session_state
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = message
                st.success(f"Đăng nhập thành công! Vai trò: {message}")
                # Sau khi đăng nhập thành công, chuyển ngay sang giao diện chính
                st.rerun()  # Làm mới trang và chuyển sang giao diện chính
            else:
                st.session_state.logged_in = False
                st.error(message)
        else:
            st.error("Vui lòng nhập đầy đủ thông tin đăng nhập.")

# Hàm giao diện chính sau khi đăng nhập
def main_page():
    st.title("QUẢN LÝ THÔNG TIN NHÂN VIÊN")

    # Hiển thị thông tin người dùng
    st.write(f"Chào {st.session_state.username}") 
    st.write(f"Vai trò của bạn là: {st.session_state.role}")
    st.write("")
    # Nếu là Admin, yêu cầu nhập mật khẩu để lấy khóa AES
    if st.session_state.role == "admin":
        password_for_key = st.text_input("Nhập mật khẩu để lấy khóa AES", type="password")

        # Hiển thị nút "Get Key" khi người dùng nhập mật khẩu
        if st.button("Get Key"):
            if verify_admin_password(password_for_key):  # Kiểm tra mật khẩu admin
                # Lấy khóa AES từ hàm hoặc từ nguồn nào đó
                df = get_admin_passwords_data()
                hashed_keyAES = df['hashed_keyAES'].iloc[0]
                aes_key = decrypt_aes_key(hashed_keyAES, password_for_key)
                st.session_state.key = aes_key
                st.success(aes_key)
            else:
                st.warning("Mật khẩu không đúng để lấy khóa AES.")
        st.subheader("Danh sách nhân viên")
        df_hsnv = get_hsnv_data()  # Lấy dữ liệu nhân viên từ hàm get_hsnv_data
        if df_hsnv is not None:
            st.dataframe(df_hsnv)  # Hiển thị dữ liệu dưới dạng bảng
        else:
            st.warning("Không thể tải dữ liệu nhân viên.")

        password_for_key = st.text_input("Nhập mật khẩu để giải mã dữ liệu", type="password")

        # Nút "Giải mã"
        if st.button("Giải mã"):
            if password_for_key:
                # Kiểm tra mật khẩu admin
                if verify_admin_password(password_for_key):  # Kiểm tra mật khẩu admin
                    # Lấy khóa AES từ hàm hoặc từ nguồn nào đó
                    df = get_admin_passwords_data()
                    hashed_keyAES = df['hashed_keyAES'].iloc[0]
                    aes_key = decrypt_aes_key(hashed_keyAES, password_for_key)
                    st.session_state.key = aes_key

                    decrypted_data = decrypt_hsnv_data(aes_key)  # Giải mã dữ liệu với khóa AES
                    if decrypted_data is not None and not decrypted_data.empty:  
                        st.dataframe(decrypted_data)  # Hiển thị dữ liệu đã giải mã
                        st.success("Dữ liệu đã được giải mã thành công.")
                    else:
                        st.error("Không thể giải mã dữ liệu. Vui lòng kiểm tra khóa AES.")
                else:
                    st.warning("Mật khẩu không đúng. Vui lòng thử lại.")
            else:
                st.warning("Vui lòng nhập mật khẩu admin.")
                
 # Thêm nhân viên
        st.subheader("Thêm nhân viên mới")
        hoTen = st.text_input("Họ và tên")
        chucVu = st.text_input("Chức vụ")
        phongBan = st.text_input("Phòng ban")
        soDienThoai = st.text_input("Số điện thoại (+84)")
        email = st.text_input("Email")
        diaChi = st.text_input("Địa chỉ")
        adminPassword = st.text_input("Mật khẩu admin", type="password", key="adminPassword")

        if st.button("Thêm nhân viên"):
            if hoTen and chucVu and phongBan and soDienThoai and email and diaChi:
                add_employee(hoTen, chucVu, phongBan, soDienThoai, email, diaChi, adminPassword)
            else:
                st.error("Vui lòng nhập đầy đủ thông tin nhân viên.")

        # Cập nhật thông tin nhân viên
        st.subheader("Cập nhật thông tin nhân viên")
        employee_id = st.text_input("Nhập ID nhân viên cần cập nhật")
        new_hoTen = st.text_input("Họ và tên mới")
        new_chucVu = st.text_input("Chức vụ mới")
        new_phongBan = st.text_input("Phòng ban mới")
        new_soDienThoai = st.text_input("Số điện thoại mới (+84)")
        new_email = st.text_input("Email mới")
        new_diaChi = st.text_input("Địa chỉ mới")
        adminPassword1 = st.text_input("Mật khẩu admin", type="password", key="adminPassword1")

        if st.button("Cập nhật thông tin"):
            if employee_id:
                update_employee_info(employee_id, new_hoTen, new_chucVu, new_phongBan, new_soDienThoai, new_email, new_diaChi, adminPassword1)
            else:
                st.error("Vui lòng nhập ID nhân viên cần cập nhật.")

        # Xóa nhân viên
        st.subheader("Xóa nhân viên")
        employee_id_to_delete = st.text_input("Nhập ID nhân viên cần xóa")
        adminPassword2 = st.text_input("Mật khẩu admin", type="password", key="adminPassword2")

        if st.button("Xóa nhân viên"):
            if employee_id_to_delete:
                delete_employee_by_id(employee_id_to_delete, adminPassword2)
            else:
                st.error("Vui lòng nhập ID nhân viên cần xóa.")

    # Nếu là User, chỉ cho phép xem dữ liệu
    elif st.session_state.role == "user":
        st.subheader("Danh sách nhân viên")
        df_hsnv = get_hsnv_data()  # Lấy dữ liệu nhân viên từ hàm get_hsnv_data
        if df_hsnv is not None:
            st.dataframe(df_hsnv)  # Hiển thị dữ liệu dưới dạng bảng
        else:
            st.warning("Không thể tải dữ liệu nhân viên.")

# Hàm chính để điều hướng giao diện
def main():
    # Kiểm tra trạng thái đăng nhập
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login()  # Nếu chưa đăng nhập, hiển thị giao diện đăng nhập
    else:
        main_page()  # Nếu đã đăng nhập, hiển thị giao diện chính

if __name__ == "__main__":
    main()


