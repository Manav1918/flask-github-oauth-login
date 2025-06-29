# 🔐 Flask GitHub OAuth Login

This project demonstrates how to integrate **GitHub OAuth 2.0 login** into a Flask web application.  
Users can now securely log in using their GitHub credentials alongside the traditional email/password method.

---

## 🚀 Features

- 🔐 GitHub OAuth 2.0 Login
- 📨 Email & Password Authentication
- 🔁 Forgot & Reset Password via Email
- 📧 Secure Session Management
- 🧠 Smart Routing Based on Login Type (GitHub or DB)
- 🌐 Beautiful Login Page with GitHub Button

---

## 📸 Demo

![GitHub Login UI Screenshot](https://user-images.githubusercontent.com/yourusername/screenshot.png)

---

## ⚙️ Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Manav1918/flask-github-oauth-login.git
cd flask-github-oauth-login
```

### 2. Create & Register OAuth App on GitHub
- Go to: https://github.com/settings/developers
- Register a new OAuth App with:
  - **Homepage**: `http://localhost:5000`
  - **Callback URL**: `http://localhost:5000/callback`
- Copy your **Client ID** and **Client Secret**

### 3. Set Environment Variables
```bash
set GITHUB_CLIENT_ID=your_client_id_here
set GITHUB_CLIENT_SECRET=your_client_secret_here
set OAUTHLIB_INSECURE_TRANSPORT=1
```

*(For Linux/macOS use `export` instead of `set`)*

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

Or manually install:
```bash
pip install flask requests-oauthlib flask-mail mysql-connector-python
```

---

## 📝 Project Structure

```
├── app.py                 # Main Flask App
├── templates/
│   ├── login.html         # Login page with GitHub button
│   └── ...
├── static/                # CSS, Images
└── README.md
```

---

## 🔑 How GitHub OAuth Works

1. User clicks "Login with GitHub"
2. Redirects to GitHub authorization screen
3. On approval, GitHub redirects back to `/callback`
4. The app fetches user profile data
5. Session is created with GitHub username and email

---

## 👨‍💻 Author

**Pawan Kumar**  
GitHub: [Manav1918](https://github.com/Manav1918)  
YouTube: [@CID_Official](https://youtube.com/@CID_Official)  
Slogan: *Keep Coding! Keep Learning!*

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 💬 Questions or Suggestions?

Open an issue or leave a comment on [YouTube](https://youtube.com/@CID_Official). I'd love to hear from you!
