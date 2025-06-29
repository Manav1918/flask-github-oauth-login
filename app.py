import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

#-----------------------------------------------------------------------------------
# Oauth2 imports
from requests_oauthlib import OAuth2Session
import os
# Set environment variable to allow insecure transport for local testing
# This is not recommended for production use.
# In production, you should use HTTPS and secure your OAuth credentials.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # Allow HTTP for local testing
#-----------------------------------------------------------------------------------

# Importing URLSafeTimedSerializer for generating and verifying tokens
from itsdangerous import URLSafeTimedSerializer
app = Flask(__name__)  # Create a Flask app
app.secret_key = os.urandom(24)  # Replace with a secure secret key

# GitHub OAuth details
client_id = os.getenv('GITHUB_CLIENT_ID')
client_secret = os.getenv('GITHUB_CLIENT_SECRET')

# OAuth URLs
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'
user_url = 'https://api.github.com/user'
# Set your redirect URI here to match exactly with your GitHub OAuth app settings
GITHUB_REDIRECT_URI = "http://localhost:5000/callback"  # Change this to your actual redirect URI
#-----------------------------------------------------------------------------------





# ✅ Password reset token functions
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

# Returns the email if the token is valid, otherwise returns None
def verify_reset_token(token, expiration=3600):  # Valid for (3600s) i.e. 1 hour
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        return email
    except Exception as e:
        return None

def mailSetup():
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'YOUR_EMAIL_ID_HERE'  # Replace with your email
    app.config['MAIL_PASSWORD'] = 'YOUR_EMAIL_PASSWORD_HERE'  # Replace with your email password
    mail = Mail(app)
    return mail
mail =  mailSetup()

# ✅ Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",      # Change if your database is hosted elsewhere
        user="root",           # Replace with your MySQL username
        password="",           # Replace with your MySQL password
        database="wakenbakedb" # Database name
    )
def is_github_login():
    return 'oauth_token' in session and 'user' in session

@app.route('/')
def home():

    if 'email' in session:
        return render_template('home.html', username=session['username'], email=session['email'])
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():  
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        #print(email, password) #console check
        try:
            #------ database connection and query
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Fetch user details from database
            cursor.execute("SELECT * FROM usertable WHERE email = %s", (email,))
            userdata = cursor.fetchone()
            #print("Row fetched from DB: ", userdata) #console check
            conn.close()
        except Exception as e:
            print(e)
            flash("An error occurred. Please try again.\n"+str(e), "error")
            return redirect(url_for('login'))
        else:
            if userdata and check_password_hash(userdata['password'], password):
                session['username'] = userdata['username']  # Set session username
                session['email'] = userdata['email']    # Set session email
                #flash("Login successful!", "success")
                #print(userdata['username'], userdata['email']) #console check
                return redirect(url_for('home'))
            else:
                flash("Invalid Email or password. Please try again.", "error")
                return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    if is_github_login():
        session.pop('oauth_token', None)
        flash("You have successfully logged out from GitHub!", "success")
    else:
        flash("You have successfully logged out!", "success")
    # Clear session data for regular login
    session.pop('user', None)
    session.pop('email', None)
    session.pop('username', None)
    
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])  # ✅ Allow both GET & POST
def register():
    if request.method == 'POST':  # ✅ Only process when method is POST
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)  # Hash password before saving to database
        print(username, email, password, hashed_password) #console check

        # Validate inputs (example: check if username exists)
        if not username or not email or not password:
            flash("All fields are required!", "error")
            return redirect(url_for('register'))  

        # Save user to database (pseudo code)
        
        try:
            #------ database connection and query
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Fetch user details from database if already exists
            cursor.execute("SELECT * FROM usertable WHERE email = %s", (email,))
            userdata = cursor.fetchone()
            if userdata:
                conn.close()
                flash("Email already exists. Please login.", "error")
                return redirect(url_for('login'))

            # Insert user details to database
            cursor.execute("INSERT INTO usertable (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)
            flash("An error occurred. Please try again.\n"+str(e), "error")
            return redirect(url_for('login'))
        else:
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
    
    return redirect(url_for('login'))  # Redirect to login page if method is GET

# ✅ Forgot Password Route
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')  # Get email from the form input
    print("Email fetched: ",email) #console check ✅
    if not email:
        flash('Please enter your email address first.', 'error')
        return redirect(url_for('login'))

    # Check if email exists in the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usertable WHERE email = %s", (email,))
    userdata = cursor.fetchone()
    conn.close()

    if not userdata:
        flash('Email not found! Please check and try again.', 'error')
        return redirect(url_for('login'))

    try:
        # Generate Reset Token
        token = generate_reset_token(email)
        reset_link = url_for('reset_password', token=token, _external=True)

        # Send Email
        msg = Message('Password Reset Request', sender='noreply@wakenbake.com', recipients=[email])
        msg.body = f'Click the link to reset your password: {reset_link}'
        mail.send(msg)

        flash('Password reset link has been sent to your email!', 'success')
    except Exception as e:
        print(e)
        flash('An error occurred while sending email. Please try again.', 'error')

    return redirect(url_for('login'))  # Redirect to login page after sending email

# ✅ Reset Password Route
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('Invalid or expired token', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('reset_password', token=token))

        hashed_password = generate_password_hash(new_password)

        # Update password in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE usertable SET password = %s WHERE email = %s", (hashed_password, email))
        conn.commit()
        conn.close()

        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)  # ✅ Pass token to template

# ✅ Change Password Route
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    print("Session: ",session) #console check ✅
    if 'email' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form['currentPassword']
        new_password = request.form['newPassword']
        confirm_password = request.form['confirmNewPassword']
        print("Current Password= ",current_password, "New Password= ",new_password) #console check ✅
        if new_password != confirm_password:
            flash('New passwords do not match!', 'error')
            return redirect(url_for('change_password'))

        email = session['email']
        print("Email= ",email, "Current Password= ",current_password, "New Password= ",new_password) #console check ✅
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usertable WHERE email = %s", (email,))
        userdata = cursor.fetchone()
        #Check if user exists and password is correct
        if not userdata or not check_password_hash(userdata['password'], current_password):
            flash('Current password is incorrect!', 'error')
            conn.close()
            return redirect(url_for('change_password'))
        #Update password in the database
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE usertable SET password = %s WHERE email = %s", (hashed_password, email))
        conn.commit()
        conn.close()

        flash('Your password has been changed successfully!', 'success')
        return redirect(url_for('home'))

    return redirect(url_for('home'))

# ✅ Cart Route
@app.route('/cart')
def cart():
    if 'email' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    email = session['email']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cart WHERE user_email = %s", (email,))
    cart_items = cursor.fetchall()
    conn.close()

    return render_template('cart.html', cart_items=cart_items)


#------------ OAuth2 GitHub Login Route
#-----------------------------------------------------------------------------------
# GitHub OAuth2 login route
# This route initiates the OAuth2 flow by redirecting the user to GitHub's authorization page.
# After the user authorizes the application, GitHub redirects back to the callback URL.
#-----------------------------------------------------------------------------------

@app.route('/github-login')
def github_login():
    # Clear any previous OAuth state to avoid stale session issues
    session.clear()
    github = OAuth2Session(client_id, redirect_uri=GITHUB_REDIRECT_URI)
    authorization_url, state = github.authorization_url(authorization_base_url)
    session['oauth_state'] = state
    session.modified = True # Ensure session is saved
    # Redirect the user to GitHub's authorization page
    return redirect(authorization_url)

@app.route('/callback')
def github_callback():
    if 'oauth_state' not in session:
        flash('OAuth state is missing. Please try again.', 'error')
        return redirect(url_for('login'))
    github = OAuth2Session(client_id, state=session['oauth_state'], redirect_uri=GITHUB_REDIRECT_URI)
    try:
        token = github.fetch_token(token_url, client_secret=client_secret,
                                   authorization_response=request.url)
        session['oauth_token'] = token
        user = github.get(user_url).json()
        email = user.get('email')
        if not email:
            email = 'No email found'
        session['user'] = user
        session['email'] = email
        session['username'] = user.get('login', 'No username found')
        #flash(f"Welcome {session['username']}!", 'success')
    except Exception as e:
        flash(f"An error occurred during GitHub login: {str(e)}", 'error')
        return redirect(url_for('login'))
    return redirect(url_for('home'))

#-----------------------------------------------------------------------------------
# Run the Flask application
#-----------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)  # Change the port if needed