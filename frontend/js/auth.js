// auth.js — Frontend authentication helper
// Include this in any page that needs login/signup/logout
// Usage: <script src="../js/auth.js"></script>

const API = 'http://127.0.0.1:5000';

// ─── Token helpers ────────────────────────────────────────────
// Token is stored in localStorage so it persists across page refreshes

const Auth = {

  getToken() {
    return localStorage.getItem('riq-token');
  },

  getUser() {
    const raw = localStorage.getItem('riq-user');
    try { return raw ? JSON.parse(raw) : null; } catch { return null; }
  },

  isLoggedIn() {
    return !!this.getToken();
  },

  _save(token, user) {
    localStorage.setItem('riq-token', token);
    localStorage.setItem('riq-user', JSON.stringify(user));
  },

  _clear() {
    localStorage.removeItem('riq-token');
    localStorage.removeItem('riq-user');
  },

  authHeaders() {
    const token = this.getToken();
    return token
      ? { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
      : { 'Content-Type': 'application/json' };
  },

  // ─── Signup ─────────────────────────────────────────────────
  async signup(name, email, phone, password, confirmPassword) {
    const res = await fetch(`${API}/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, phone, password, confirm_password: confirmPassword })
    });
    const data = await res.json();
    return data;   // { success, message, data }
  },

  // ─── Login ──────────────────────────────────────────────────
  async login(identifier, password) {
    const res = await fetch(`${API}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ identifier, password })
    });
    const data = await res.json();
    if (data.success && data.data?.token) {
      this._save(data.data.token, { name: data.data.name, email: data.data.email });
    }
    return data;
  },

  // ─── Logout ─────────────────────────────────────────────────
  async logout() {
    const token = this.getToken();
    if (token) {
      try {
        await fetch(`${API}/logout`, {
          method: 'POST',
          headers: this.authHeaders()
        });
      } catch { /* ignore network errors on logout */ }
    }
    this._clear();
    window.location.href = 'login.html';
  },

  // ─── Get profile ─────────────────────────────────────────────
  async getProfile() {
    if (!this.isLoggedIn()) return null;
    const res = await fetch(`${API}/profile`, { headers: this.authHeaders() });
    const data = await res.json();
    return data.success ? data.data : null;
  },

  // ─── Update profile ──────────────────────────────────────────
  async updateProfile(updates) {
    const res = await fetch(`${API}/profile`, {
      method: 'PUT',
      headers: this.authHeaders(),
      body: JSON.stringify(updates)
    });
    return await res.json();
  },

  // ─── Forgot password ─────────────────────────────────────────
  async resetPassword(email, newPassword, confirmPassword) {
    const res = await fetch(`${API}/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, new_password: newPassword, confirm_password: confirmPassword })
    });
    return await res.json();
  },

  // ─── Guard: redirect to login if not logged in ───────────────
  // Call this at the top of any protected page
  requireLogin(redirectTo = 'login.html') {
    if (!this.isLoggedIn()) {
      window.location.href = redirectTo;
      return false;
    }
    return true;
  },

  // ─── Password strength checker ───────────────────────────────
  // Returns { score: 0-5, checks: { upper, lower, number, special, length } }
  checkPasswordStrength(password) {
    const checks = {
      length:  password.length >= 8,
      upper:   /[A-Z]/.test(password),
      lower:   /[a-z]/.test(password),
      number:  /[0-9]/.test(password),
      special: /[!@#$%^&*()_+\-=\[\]{}|;':",./<>?]/.test(password)
    };
    const score = Object.values(checks).filter(Boolean).length;
    return { score, checks };
  }

};

// ─── Auto-update navbar user display on any page ─────────────
// If a page has elements with id="navUserName" or id="navAvatar"
// this will fill them in automatically
document.addEventListener('DOMContentLoaded', () => {
  const user = Auth.getUser();
  const nameEl   = document.getElementById('navUserName');
  const avatarEl = document.getElementById('navAvatar');
  const loginBtn = document.getElementById('navLoginBtn');
  const logoutBtn= document.getElementById('navLogoutBtn');

  if (user) {
    const initials = user.name
      ? user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
      : '?';
    if (nameEl)    nameEl.textContent   = user.name;
    if (avatarEl)  avatarEl.textContent = initials;
    if (loginBtn)  loginBtn.style.display  = 'none';
    if (logoutBtn) logoutBtn.style.display = 'inline-flex';
  } else {
    if (loginBtn)  loginBtn.style.display  = 'inline-flex';
    if (logoutBtn) logoutBtn.style.display = 'none';
  }

  // Wire logout button if it exists
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => Auth.logout());
  }
});
