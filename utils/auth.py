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
    """Load users from a JSON file"""
    if not os.path.exists(USERS_FILE):
        # Create the data directory if it doesn't exist
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        return {}
    
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Save users to a JSON file"""
    # Create the data directory if it doesn't exist
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def generate_captcha(length=6):
    """Generate a random captcha code"""
    return ''.join(random.choice(string.digits) for _ in range(length))

def generate_captcha_image(text, width=200, height=80):
    """Generate a captcha image from text"""
    # Create a blank image
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("Arial", 36)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw the text
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, font=font, fill=(0, 0, 0))
    
    # Add noise
    for _ in range(1000):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        draw.point((x, y), fill=(random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)))
    
    # Add some lines
    for _ in range(5):
        x1 = random.randint(0, width - 1)
        y1 = random.randint(0, height - 1)
        x2 = random.randint(0, width - 1)
        y2 = random.randint(0, height - 1)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)), width=2)
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr.getvalue()

def get_image_as_base64(img_bytes):
    """Convert image bytes to base64 string for HTML"""
    return base64.b64encode(img_bytes).decode()

def init_auth_state():
    """Initialize authentication state in session state"""
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
    """Decorator to require authentication for a page"""
    def wrapper(*args, **kwargs):
        init_auth_state()
        
        # Check for valid session state
        if st.session_state.authenticated:
            # Check if session has expired
            if st.session_state.session_expiry and datetime.now() < datetime.fromisoformat(st.session_state.session_expiry):
                # Session is still valid
                pass
            else:
                # Session has expired
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.session_expiry = None
        
        if not st.session_state.authenticated:
            show_login_page()
            return
        
        # User is authenticated, call the wrapped function
        func(*args, **kwargs)
    
    return wrapper

def show_login_page():
    """Display the login page"""
    st.title("Login")
    
    # Create tabs for login and sign up
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        # Display CAPTCHA
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
                st.session_state.captcha_text = generate_captcha()  # Generate new CAPTCHA
                st.session_state.login_attempts += 1
                return
            
            users = load_users()
            if username in users and users[username]["password"] == password:
                # Set session expiry (24 hours from now)
                expiry = datetime.now() + timedelta(days=1)
                
                # Save session to users data
                users[username]["last_login"] = datetime.now().isoformat()
                save_users(users)
                
                # Set authenticated in session state
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.session_expiry = expiry.isoformat()
                st.rerun()
            else:
                st.error("Invalid username or password")
                st.session_state.login_attempts += 1
                st.session_state.captcha_text = generate_captcha()  # Generate new CAPTCHA
    
    with tab2:
        new_username = st.text_input("Choose Username", key="signup_username")
        new_password = st.text_input("Create Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        # Display CAPTCHA for signup
        st.write("Verify CAPTCHA:")
        captcha_bytes = generate_captcha_image(st.session_state.captcha_text)
        st.image(captcha_bytes, width=200)
        captcha_input = st.text_input("Enter the 6 digits shown above", key="signup_captcha")
        
        if st.button("Sign Up"):
            if not captcha_input or captcha_input != st.session_state.captcha_text:
                st.error("CAPTCHA verification failed. Please try again.")
                st.session_state.captcha_text = generate_captcha()  # Generate new CAPTCHA
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
            
            # Create new user
            users[new_username] = {
                "password": new_password,
                "created_at": datetime.now().isoformat()
            }
            save_users(users)
            st.success("Account created successfully! Please login.")
            st.session_state.captcha_text = generate_captcha()  # Generate new CAPTCHA

def logout():
    """Log out the user and clear session"""
    # Record logout in user data if needed
    if st.session_state.username:
        try:
            users = load_users()
            if st.session_state.username in users:
                users[st.session_state.username]["last_logout"] = datetime.now().isoformat()
                save_users(users)
        except Exception:
            # Continue even if saving logout time fails
            pass
    
    # Reset session state
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.session_expiry = None
    st.session_state.captcha_text = generate_captcha()
    st.session_state.login_attempts = 0
    st.rerun()
