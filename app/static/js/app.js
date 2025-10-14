// Toast notification system
class ToastManager {
    constructor() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    }

    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        this.container.appendChild(toast);
        
        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, duration);
        
        // Click to dismiss
        toast.addEventListener('click', () => {
            toast.remove();
        });
        
        return toast;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Initialize toast manager
const toast = new ToastManager();
window.toast = toast;

// HTMX configuration
document.addEventListener('DOMContentLoaded', function() {
    htmx.config.useTemplateFragments = true;
    
    // Show loading states for HTMX requests
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        const target = evt.target;
        
        if (target.hasAttribute('data-loading')) {
            const originalText = target.innerHTML;
            target.setAttribute('data-original-text', originalText);
            target.innerHTML = '<span class="loading"></span> Loading...';
            target.disabled = true;
        }
    });
    
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        const target = evt.target;
        
        if (target.hasAttribute('data-loading')) {
            const originalText = target.getAttribute('data-original-text');
            if (originalText) {
                target.innerHTML = originalText;
                target.removeAttribute('data-original-text');
            }
            target.disabled = false;
        }
    });
    
    // Handle successful responses
    document.body.addEventListener('htmx:afterOnLoad', function(evt) {
        const xhr = evt.detail.xhr;
        
        if (xhr.status >= 200 && xhr.status < 300) {
            const requestMethod = evt.detail.requestConfig.verb;
            
            if (requestMethod === 'post') {
                toast.success('Operation completed successfully!');
            } else if (requestMethod === 'put' || requestMethod === 'patch') {
                toast.success('Update completed successfully!');
            } else if (requestMethod === 'delete') {
                toast.success('Item deleted successfully!');
            }
        }
    });
    
    // Handle errors
    document.body.addEventListener('htmx:responseError', function(evt) {
        const xhr = evt.detail.xhr;
        let errorMessage = 'An error occurred';
        
        try {
            const response = JSON.parse(xhr.responseText);
            errorMessage = response.detail || errorMessage;
        } catch (e) {
            // Use default error message
        }
        
        toast.error(errorMessage);
    });
});

// Utility functions
window.utils = {
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    },

    truncateText(text, maxLength = 100) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
};

// Auth management functions
async function updateAuthUI() {
    const authSection = document.getElementById('auth-section');
    if (!authSection) return;
    
    const token = localStorage.getItem('access_token');
    
    if (token) {
        try {
            const response = await fetch('/auth/me', {
                headers: {
                    'Authorization': 'Bearer ' + token
                }
            });
            
            if (response.ok) {
                const user = await response.json();
                authSection.innerHTML = `
                    <div class="user-nav">
                        <div class="user-info">
                            <span class="user-name">Hello, ${user.name}</span>
                            <div class="user-badges">
                                ${user.is_verified ? '<span class="badge badge-success">Verified Author</span>' : ''}
                                ${user.is_admin ? '<span class="badge badge-warning">Admin</span>' : ''}
                            </div>
                        </div>
                        <div class="user-actions">
                            ${user.is_verified ? '<a href="/news/create" class="btn btn-outline btn-sm">✏️ Create News</a>' : ''}
                            <button onclick="logout()" class="btn btn-outline btn-sm">🚪 Logout</button>
                        </div>
                    </div>
                `;
            } else {
                showLoginButtons();
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            showLoginButtons();
        }
    } else {
        showLoginButtons();
    }
}

function showLoginButtons() {
    const authSection = document.getElementById('auth-section');
    authSection.innerHTML = `
        <div class="auth-buttons">
            <a href="/auth/login" class="nav-link">🔐 Login</a>
            <a href="/auth/register" class="nav-link">👤 Register</a>
            <a href="/auth/oauth/github/demo" class="btn btn-github btn-sm">
                <span>🐙 GitHub Demo</span>
            </a>
        </div>
    `;
}

function logout() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (refreshToken) {
        // Call logout endpoint to invalidate refresh token
        fetch('/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh_token: refreshToken })
        }).catch(error => {
            console.error('Logout API call failed:', error);
        });
    }
    
    // Clear local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Show success message
    if (window.toast) {
        window.toast.success('Logged out successfully!');
    }
    
    // Redirect to home page
    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}

// Handle OAuth callback - check if we have tokens in URL or response
function handleOAuthCallback() {
    const urlParams = new URLSearchParams(window.location.hash.substring(1));
    const accessToken = urlParams.get('access_token');
    const refreshToken = urlParams.get('refresh_token');
    
    if (accessToken && refreshToken) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        
        toast.success('GitHub login successful!');
        
        // Redirect to home page
        setTimeout(() => {
            window.location.href = '/';
        }, 1000);
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    handleOAuthCallback();
    updateAuthUI();
    
    // Add auth header to all HTMX requests
    document.body.addEventListener('htmx:configRequest', function(evt) {
        const token = localStorage.getItem('access_token');
        if (token) {
            evt.detail.headers['Authorization'] = 'Bearer ' + token;
        }
    });
    
    // Handle auth errors in HTMX responses
    document.body.addEventListener('htmx:responseError', function(evt) {
        if (evt.detail.xhr.status === 401) {
            // Unauthorized - clear tokens and reload auth UI
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            updateAuthUI();
            
            if (window.toast) {
                window.toast.error('Session expired. Please login again.');
            }
        }
    });
});

// Global function to check if user is authenticated
window.isAuthenticated = function() {
    return !!localStorage.getItem('access_token');
}

// Global function to get current user (async)
window.getCurrentUser = async function() {
    const token = localStorage.getItem('access_token');
    if (!token) return null;
    
    try {
        const response = await fetch('/auth/me', {
            headers: {
                'Authorization': 'Bearer ' + token
            }
        });
        
        if (response.ok) {
            return await response.json();
        }
        return null;
    } catch (error) {
        console.error('Failed to get current user:', error);
        return null;
    }
}

// Make functions available globally
window.updateAuthUI = updateAuthUI;
window.logout = logout;