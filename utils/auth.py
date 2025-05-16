import streamlit as st
import random
import string
from datetime import datetime, timedelta
import os
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Initialize a dictionary to store users (in production use a database)
USERS_FILE = "data/users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def generate_captcha(length=6):
    return ''.join(random.choice(string.digits) for _ in range(length))

def generate_captcha_image(text, width=200, height=80):
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Arial", 36)
    except IOError:
        font = ImageFont.load_default()
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, font=font, fill=(0, 0, 0))
    for _ in range(1000):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        draw.point((x, y), fill=(random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)))
    for _ in range(5):
        x1, y1, x2, y2 = random.randint(0, width - 1), random.randint(0, height - 1), random.randint(0, width - 1), random.randint(0, height - 1)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)), width=2)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()

def get_image_as_base64(img_bytes):
    return base64.b64encode(img_bytes).decode()

def init_auth_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'captcha_text' not in st.session_state:
        st.session_state.captcha_text = generate_captcha()
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    if 'session_expiry' not in st.session_state:
        st.session_state.session_expiry = None

def auth_required(func):
    def wrapper(*args, **kwargs):
        init_auth_state()
        if st.session_state.authenticated:
            if st.session_state.session_expiry and datetime.now() < datetime.fromisoformat(st.session_state.session_expiry):
                pass
            else:
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.session_expiry = None
        if not st.session_state.authenticated:
            show_login_page()
            return
        func(*args, **kwargs)
    return wrapper

def show_login_page():
    st.markdown("""
    <style>
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 80vh;
    }
    .login-box {
        background-color: #f9f9f9;
        padding: 30px 40px;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 400px;
    }
    .login-box h2 {
        text-align: center;
        color: #4c78db;
        margin-bottom: 20px;
    }
    .stButton > button {
        background-color: #4c78db;
        color: white;
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #355fc0;
        transform: scale(1.02);
    }
    </style>
    <div class="login-wrapper">
        <div class="login-box">
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.markdown("<h2>Login</h2>", unsafe_allow_html=True)
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        st.write("Verify CAPTCHA:")
        captcha_bytes = generate_captcha_image(st.session_state.captcha_text)
        st.image(captcha_bytes, width=200)
        captcha_input = st.text_input("Enter the 6 digits shown above", key="login_captcha")
        if st.button("Login"):
            if st.session_state.login_attempts >= 3:
                st.error("Too many failed login attempts. Please try again later.")
                return
            if not captcha_input or captcha_input != st.session_state.captcha_text:
                st.error("CAPTCHA verification failed. Please try again.")
                st.session_state.captcha_text = generate_captcha()
                st.session_state.login_attempts += 1
                return
            users = load_users()
            if username in users and users[username]["password"] == password:
                expiry = datetime.now() + timedelta(days=1)
                users[username]["last_login"] = datetime.now().isoformat()
                save_users(users)
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.session_expiry = expiry.isoformat()
                st.rerun()
            else:
                st.error("Invalid username or password")
                st.session_state.login_attempts += 1
                st.session_state.captcha_text = generate_captcha()

    with tab2:
        st.markdown("<h2>Sign Up</h2>", unsafe_allow_html=True)
        new_username = st.text_input("Choose Username", key="signup_username")
        new_password = st.text_input("Create Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
        st.write("Verify CAPTCHA:")
        captcha_bytes = generate_captcha_image(st.session_state.captcha_text)
        st.image(captcha_bytes, width=200)
        captcha_input = st.text_input("Enter the 6 digits shown above", key="signup_captcha")
        if st.button("Sign Up"):
            if not captcha_input or captcha_input != st.session_state.captcha_text:
                st.error("CAPTCHA verification failed. Please try again.")
                st.session_state.captcha_text = generate_captcha()
                return
            if not new_username or not new_password:
                st.error("Username and password are required")
                return
            if new_password != confirm_password:
                st.error("Passwords do not match")
                return
            users = load_users()
            if new_username in users:
                st.error("Username already exists")
                return
            users[new_username] = {
                "password": new_password,
                "created_at": datetime.now().isoformat()
            }
            save_users(users)
            st.success("Account created successfully! Please login.")
            st.session_state.captcha_text = generate_captcha()

    st.markdown("</div></div>", unsafe_allow_html=True)

def logout():
    if st.session_state.username:
        try:
            users = load_users()
            if st.session_state.username in users:
                users[st.session_state.username]["last_logout"] = datetime.now().isoformat()
                save_users(users)
        except Exception:
            pass
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.session_expiry = None
    st.session_state.captcha_text = generate_captcha()
    st.session_state.login_attempts = 0
    st.rerun()
