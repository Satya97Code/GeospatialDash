import streamlit as st
import random
import string
from datetime import datetime, timedelta
import os
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64

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
    .main-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background-color: #ffffff;
        font-family: 'Segoe UI', sans-serif;
    }
    .login-card {
        display: flex;
        max-width: 600px;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-radius: 12px;
        overflow: hidden;
        background-color: white;
        padding: 40px;
    }
    .login-form {
        width: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .login-form h2 {
        margin-bottom: 20px;
        color: #333;
        font-weight: 600;
        text-align: center;
    }
    .login-form input {
        margin-bottom: 15px;
        padding: 12px;
        border: 1px solid #ddd;
        border-radius: 8px;
        width: 100%;
    }
    .login-form button {
        padding: 12px;
        border: none;
        border-radius: 25px;
        background-color: #63c132;
        color: white;
        font-weight: bold;
        cursor: pointer;
        margin-top: 10px;
    }
    .login-form button:hover {
        background-color: #4ea424;
    }
    .login-form small {
        color: #888;
        margin-top: 10px;
        font-size: 12px;
        text-align: center;
    }
    </style>
    <div class="main-container">
        <div class="login-card">
            <div class="login-form">
    """, unsafe_allow_html=True)

    st.markdown("<h2>Member Login</h2>", unsafe_allow_html=True)
    username = st.text_input("Email", key="login_username", label_visibility="collapsed", placeholder="Email")
    password = st.text_input("Password", type="password", key="login_password", label_visibility="collapsed", placeholder="Password")
    st.write("Verify CAPTCHA:")
    captcha_bytes = generate_captcha_image(st.session_state.captcha_text)
    st.image(captcha_bytes, width=200)
    captcha_input = st.text_input("Enter the 6 digits shown above", key="login_captcha")

    if st.button("LOGIN"):
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

    st.markdown("<small>Forgot Username / Password?</small>", unsafe_allow_html=True)
    st.markdown("<small style='margin-top: 10px;'>Create your Account →</small>", unsafe_allow_html=True)

    st.markdown("</div></div></div>", unsafe_allow_html=True)

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
