// Registration System Frontend JavaScript

class RegistrationApp {
    constructor() {
        this.form = document.getElementById('registrationForm');
        this.messageArea = document.getElementById('messageArea');
        this.init();
    }
    
    init() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
            this.form.addEventListener('reset', () => this.handleReset());
            
            // Real-time validation
            const usernameInput = document.getElementById('username');
            const emailInput = document.getElementById('email');
            
            if (usernameInput) {
                usernameInput.addEventListener('blur', () => this.checkAvailability('username', usernameInput.value));
            }
            
            if (emailInput) {
                emailInput.addEventListener('blur', () => this.checkAvailability('email', emailInput.value));
            }
            
            // Password match validation
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');
            
            if (password && confirmPassword) {
                confirmPassword.addEventListener('input', () => this.validatePasswordMatch());
            }
            
            // File upload handling
            const fileInputs = document.querySelectorAll('input[type="file"]');
            fileInputs.forEach(input => {
                input.addEventListener('change', (e) => this.handleFileSelect(e.target));
            });
        }
        
        // Check if user is already logged in
        this.checkSession();
    }
    
    showMessage(message, type = 'info') {
        if (!this.messageArea) return;
        this.messageArea.textContent = message;
        this.messageArea.className = `message-area ${type}`;
        this.messageArea.style.display = 'block';
        
        setTimeout(() => {
            if (this.messageArea) {
                this.messageArea.style.display = 'none';
            }
        }, 5000);
    }
    
    async checkAvailability(field, value) {
        if (!value || value.length < 3) return;
        
        try {
            const response = await fetch('/api/check-availability', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ field, value })
            });
            
            const data = await response.json();
            const statusSpan = document.getElementById(`${field}Status`);
            
            if (statusSpan) {
                if (data.available) {
                    statusSpan.textContent = `${field} is available`;
                    statusSpan.style.color = 'green';
                } else {
                    statusSpan.textContent = `${field} is already taken`;
                    statusSpan.style.color = 'red';
                }
            }
        } catch (error) {
            console.error('Availability check failed:', error);
        }
    }
    
    validatePasswordMatch() {
        const password = document.getElementById('password').value;
        const confirm = document.getElementById('confirm_password').value;
        const confirmField = document.getElementById('confirm_password');
        
        if (password !== confirm) {
            confirmField.setCustomValidity('Passwords do not match');
            confirmField.style.borderColor = 'red';
        } else {
            confirmField.setCustomValidity('');
            confirmField.style.borderColor = '#e0e0e0';
        }
    }
    
    handleFileSelect(input) {
        const files = input.files;
        const maxSize = 5 * 1024 * 1024; // 5MB
        
        for (let file of files) {
            if (file.size > maxSize) {
                this.showMessage(`File ${file.name} exceeds 5MB limit`, 'error');
                input.value = '';
                return;
            }
        }
    }
    
    collectFormData() {
        const formData = new FormData(this.form);
        const data = {};
        
        // Handle multiple checkboxes (interests)
        const interests = [];
        document.querySelectorAll('input[name="interests"]:checked').forEach(cb => {
            interests.push(cb.value);
        });
        if (interests.length) data.interests = interests;
        
        // Handle other fields
        for (let [key, value] of formData.entries()) {
            if (key !== 'interests' && value) {
                data[key] = value;
            }
        }
        
        return data;
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        // Validate required fields
        const required = ['full_name', 'username', 'email', 'password', 'confirm_password', 'terms', 'privacy'];
        for (let field of required) {
            const element = document.getElementById(field);
            if (element && !element.value && element.type !== 'checkbox') {
                this.showMessage(`Please fill in ${field.replace('_', ' ')}`, 'error');
                element.focus();
                return;
            }
            if (element && element.type === 'checkbox' && !element.checked) {
                this.showMessage(`You must agree to ${field.replace('_', ' ')}`, 'error');
                return;
            }
        }
        
        // Validate password match
        if (document.getElementById('password').value !== document.getElementById('confirm_password').value) {
            this.showMessage('Passwords do not match', 'error');
            return;
        }
        
        const submitBtn = this.form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Registering...';
        submitBtn.disabled = true;
        submitBtn.classList.add('btn-loading');
        
        try {
            const data = this.collectFormData();
            
            // Handle file uploads separately if needed
            const files = {};
            const fileInputs = ['profile_picture', 'resume', 'additional_files'];
            for (let inputId of fileInputs) {
                const input = document.getElementById(inputId);
                if (input && input.files.length) {
                    files[inputId] = input.files;
                }
            }
            
            // First submit registration data
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Upload files if any
                if (Object.keys(files).length > 0) {
                    const uploadFormData = new FormData();
                    for (let [key, fileList] of Object.entries(files)) {
                        for (let file of fileList) {
                            uploadFormData.append(key, file);
                        }
                    }
                    
                    await fetch('/api/upload', {
                        method: 'POST',
                        body: uploadFormData
                    });
                }
                
                this.showMessage(result.message, 'success');
                setTimeout(() => {
                    window.location.href = result.redirect || '/dashboard';
                }, 1500);
            } else {
                this.showMessage(result.error || 'Registration failed', 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showMessage('Network error. Please try again.', 'error');
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
            submitBtn.classList.remove('btn-loading');
        }
    }
    
    handleReset() {
        setTimeout(() => {
            this.showMessage('Form has been reset', 'info');
        }, 100);
    }
    
    async checkSession() {
        try {
            const response = await fetch('/api/session');
            const data = await response.json();
            
            if (data.authenticated && window.location.pathname === '/register') {
                window.location.href = '/dashboard';
            }
        } catch (error) {
            console.error('Session check failed:', error);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new RegistrationApp();
    
    // Login form handling if on login page
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username_or_email = document.getElementById('username_or_email').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username_or_email, password })
                });
                
                const result = await response.json();
                if (result.success) {
                    window.location.href = result.redirect;
                } else {
                    alert(result.error);
                }
            } catch (error) {
                alert('Login failed');
            }
        });
    }
});
