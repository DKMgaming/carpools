import streamlit as st
import requests
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# Cấu hình xác thực OAuth với Google
def get_google_auth_flow():
    client_config = {
        "web": {
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "redirect_uris": ["https://carpools-vietri.streamlit.app"],  # Đảm bảo trùng khớp với URL của ứng dụng
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=["https://www.googleapis.com/auth/userinfo.email"],
        redirect_uri="https://carpools-vietri.streamlit.app",  # Đảm bảo trùng khớp với URL của ứng dụng
    )
    return flow

# Hàm xử lý đăng nhập Google và lấy URL xác thực
def google_login():
    flow = get_google_auth_flow()
    authorization_url, state = flow.authorization_url(prompt="consent")
    st.session_state['auth_state'] = state
    st.write("**Đang chuyển hướng đến Google để đăng nhập...**")
    st.write(f"[Đăng nhập với Google]({authorization_url})")

# Hàm lấy thông tin người dùng từ Google API sau khi đăng nhập
def fetch_user_info():
    if 'auth_code' in st.experimental_get_query_params():
        flow = get_google_auth_flow()
        flow.fetch_token(code=st.experimental_get_query_params()['auth_code'])
        credentials = flow.credentials
        user_info = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            headers={'Authorization': f'Bearer {credentials.token}'}
        ).json()
        st.write(f"Chào, {user_info['email']}!")  # Hiển thị email của người dùng
    else:
        google_login()

# Hàm chính của ứng dụng
def main():
    st.title("🚗 Ứng dụng chia sẻ xe Carpool")

    # Kiểm tra xem người dùng đã đăng nhập chưa
    if 'auth_code' not in st.experimental_get_query_params():
        if st.button("Đăng nhập bằng Google"):
            google_login()  # Gọi hàm đăng nhập Google
    else:
        fetch_user_info()  # Lấy thông tin người dùng nếu đã đăng nhập

if __name__ == "__main__":
    main()
