import streamlit as st
import requests
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests as google_requests


st.set_page_config(page_title="Carpool App", page_icon="🚗")

# Tải thông tin OAuth từ file JSON
def get_google_auth_flow():
    client_config = {
        "web": {
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "redirect_uris": ["https://your-app-name.streamlit.app"]
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/userinfo.email'],
        redirect_uri="https://your-app-name.streamlit.app"
    )
    return flow

# Hàm để đăng nhập Google OAuth2
def google_login():
    flow = get_google_auth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.write(f"[Đăng nhập bằng Google]({auth_url})", unsafe_allow_html=True)

# Hàm để lấy thông tin đăng nhập sau khi có mã xác thực
def fetch_user_info():
    flow = get_google_auth_flow()
    code = st.experimental_get_query_params().get('code')
    if code:
        flow.fetch_token(code=code[0])
        credentials = flow.credentials
        session = google_requests.AuthorizedSession(credentials)
        user_info = session.get('https://www.googleapis.com/userinfo/v2/me').json()
        st.session_state['email'] = user_info.get('email')
        return user_info.get('email')
    return None

# Tính toán tuyến đường bằng Google Maps API
def get_directions(origin, destination):
    api_key = 'AIzaSyASj96AGvX38kmkb18m5d4s1uR4wQ6j9_o'
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={api_key}'
    response = requests.get(url)
    return response.json()

# Giao diện Streamlit
st.title("🚗 Ứng dụng chia sẻ xe Carpool")

# Đăng nhập hoặc hiển thị email nếu đã đăng nhập
if 'email' not in st.session_state:
    google_login()
    email = fetch_user_info()
else:
    email = st.session_state['email']
    st.write(f"Xin chào, {email}")

# Chọn điểm đi và điểm đến
if email:
    st.subheader("Chọn điểm đi và điểm đến")
    origin = st.text_input("Điểm đi (ví dụ: Ho Chi Minh City)")
    destination = st.text_input("Điểm đến (ví dụ: Hanoi)")

    if st.button("Tạo tuyến đường"):
        if origin and destination:
            directions = get_directions(origin, destination)
            if directions['status'] == 'OK':
                route = directions['routes'][0]['overview_polyline']['points']
                
                # Hiển thị tuyến đường trên Google Maps
                st.map({
                    "data": [
                        {"lat": step['start_location']['lat'], "lon": step['start_location']['lng']} 
                        for step in directions['routes'][0]['legs'][0]['steps']
                    ],
                    "zoom": 10,
                    "center": {"lat": directions['routes'][0]['legs'][0]['start_location']['lat'], 
                               "lon": directions['routes'][0]['legs'][0]['start_location']['lng']}
                })
            else:
                st.write("Không thể tạo tuyến đường. Vui lòng thử lại.")
