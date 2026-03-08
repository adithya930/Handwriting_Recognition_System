/**
 * Authentication JavaScript
 * Handles login and registration functionality
 */

// API Base URL
const API_BASE_URL = '/api';

/**
 * Show alert message
 */
function showAlert(message, type = 'error') {
    const alertDiv = document.getElementById('alertMessage');
    if (!alertDiv) return;

    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        alertDiv.style.display = 'none';
    }, 5000);
}

/**
 * Hide alert message
 */
function hideAlert() {
    const alertDiv = document.getElementById('alertMessage');
    if (alertDiv) {
        alertDiv.style.display = 'none';
    }
}

/**
 * Toggle button loading state
 */
function setButtonLoading(button, isLoading) {
    const btnText = button.querySelector('.btn-text');
    const btnLoader = button.querySelector('.btn-loader');

    if (isLoading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'flex';
        button.disabled = true;
    } else {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        button.disabled = false;
    }
}

/**
 * Initialize Login Page
 */
function initLogin() {
    const loginForm = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');

    if (!loginForm) return;

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAlert();

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        // Validation
        if (!username || !password) {
            showAlert('Please fill in all fields');
            return;
        }

        // Start loading
        setButtonLoading(loginBtn, true);

        try {
            const response = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Store token in localStorage
                if (data.token) {
                    localStorage.setItem('authToken', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                }

                // Show success message
                showAlert('Login successful! Redirecting...', 'success');

                // Redirect to home page
                setTimeout(() => {
                    window.location.href = '/home';
                }, 1000);
            } else {
                showAlert(data.error || 'Login failed');
                setButtonLoading(loginBtn, false);
            }
        } catch (error) {
            console.error('Login error:', error);
            showAlert('Network error. Please try again.');
            setButtonLoading(loginBtn, false);
        }
    });

    // Handle "Remember me" checkbox
    const rememberMe = document.getElementById('rememberMe');
    const usernameInput = document.getElementById('username');

    // Load saved username if exists
    const savedUsername = localStorage.getItem('savedUsername');
    if (savedUsername) {
        usernameInput.value = savedUsername;
        rememberMe.checked = true;
    }

    // Save username on form submit if remember me is checked
    loginForm.addEventListener('submit', () => {
        if (rememberMe.checked) {
            localStorage.setItem('savedUsername', usernameInput.value);
        } else {
            localStorage.removeItem('savedUsername');
        }
    });
}

/**
 * Initialize Registration Page
 */
function initRegister() {
    const registerForm = document.getElementById('registerForm');
    const registerBtn = document.getElementById('registerBtn');

    if (!registerForm) return;

    // Password confirmation validation
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');

    confirmPasswordInput.addEventListener('input', () => {
        if (confirmPasswordInput.value !== passwordInput.value) {
            confirmPasswordInput.setCustomValidity('Passwords do not match');
        } else {
            confirmPasswordInput.setCustomValidity('');
        }
    });

    // Form submission
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAlert();

        const fullName = document.getElementById('fullName').value.trim();
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const role = document.getElementById('role').value;
        const acceptTerms = document.getElementById('acceptTerms').checked;

        // Validation
        if (!fullName || !username || !email || !password || !confirmPassword) {
            showAlert('Please fill in all fields');
            return;
        }

        if (password !== confirmPassword) {
            showAlert('Passwords do not match');
            return;
        }

        if (password.length < 6) {
            showAlert('Password must be at least 6 characters long');
            return;
        }

        if (!acceptTerms) {
            showAlert('Please accept the terms and conditions');
            return;
        }

        // Start loading
        setButtonLoading(registerBtn, true);

        try {
            const response = await fetch(`${API_BASE_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    full_name: fullName,
                    username: username,
                    email: email,
                    password: password,
                    role: role
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Show success message
                showAlert('Registration successful! Redirecting to login...', 'success');

                // Clear form
                registerForm.reset();

                // Redirect to login page
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                showAlert(data.error || 'Registration failed');
                setButtonLoading(registerBtn, false);
            }
        } catch (error) {
            console.error('Registration error:', error);
            showAlert('Network error. Please try again.');
            setButtonLoading(registerBtn, false);
        }
    });
}

/**
 * Logout function
 */
async function logout() {
    try {
        const response = await fetch(`${API_BASE_URL}/logout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Clear local storage
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');

        // Redirect to login page
        window.location.href = '/login';
    } catch (error) {
        console.error('Logout error:', error);
        // Still redirect even if API call fails
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
    }
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    const token = localStorage.getItem('authToken');
    return token !== null;
}

/**
 * Get current user from localStorage
 */
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        try {
            return JSON.parse(userStr);
        } catch (e) {
            return null;
        }
    }
    return null;
}

/**
 * Make authenticated API request
 */
async function authenticatedFetch(url, options = {}) {
    const token = localStorage.getItem('authToken');

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    // If unauthorized, redirect to login
    if (response.status === 401) {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return null;
    }

    return response;
}

/**
 * Password strength checker
 */
function checkPasswordStrength(password) {
    let strength = 0;

    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z\d]/.test(password)) strength++;

    return strength;
}

/**
 * Display password strength indicator
 */
function displayPasswordStrength(password, indicatorElement) {
    const strength = checkPasswordStrength(password);

    indicatorElement.innerHTML = '';

    const strengthBar = document.createElement('div');
    strengthBar.className = 'password-strength';

    const bar = document.createElement('div');
    bar.className = 'password-strength-bar';

    if (strength <= 2) {
        bar.classList.add('password-strength-weak');
    } else if (strength <= 3) {
        bar.classList.add('password-strength-medium');
    } else {
        bar.classList.add('password-strength-strong');
    }

    strengthBar.appendChild(bar);
    indicatorElement.appendChild(strengthBar);
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showAlert,
        hideAlert,
        setButtonLoading,
        initLogin,
        initRegister,
        logout,
        isAuthenticated,
        getCurrentUser,
        authenticatedFetch,
        checkPasswordStrength,
        displayPasswordStrength
    };
}
