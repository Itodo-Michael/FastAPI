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
                toast.style.animation = 'slideInRight 0.3s ease reverse';
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
        
        // Click to dismiss
        toast.addEventListener('click', () => {
            toast.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
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

// HTMX configuration and extensions
document.addEventListener('DOMContentLoaded', function() {
    // Configure HTMX
    htmx.config.useTemplateFragments = true;
    
    // Show loading states
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
    
    // Handle form responses
    document.body.addEventListener('htmx:afterOnLoad', function(evt) {
        const xhr = evt.detail.xhr;
        
        // Show success message for successful operations
        if (xhr.status >= 200 && xhr.status < 300) {
            const requestMethod = evt.detail.requestConfig.verb;
            
            if (requestMethod === 'post') {
                toast.success('Item created successfully!');
            } else if (requestMethod === 'put') {
                toast.success('Item updated successfully!');
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

// API Client for additional JavaScript functionality
class ApiClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async getUsers() {
        return this.request('/users');
    }

    async createUser(userData) {
        return this.request('/users', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }

    async getNews() {
        return this.request('/news');
    }

    async createNews(newsData) {
        return this.request('/news', {
            method: 'POST',
            body: JSON.stringify(newsData),
        });
    }

    async getComments() {
        return this.request('/comments');
    }

    async createComment(commentData) {
        return this.request('/comments', {
            method: 'POST',
            body: JSON.stringify(commentData),
        });
    }
}

// Initialize API client
const api = new ApiClient();

// Utility functions
const utils = {
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
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
};

// Custom formatters for HTMX responses
window.formatUsers = function(users) {
    if (!users || users.length === 0) {
        return `
            <div class="empty-state">
                <div class="empty-state-icon">👥</div>
                <h3>No Users Found</h3>
                <p>Create your first user to get started.</p>
            </div>
        `;
    }

    return users.map(user => `
        <div class="list-item">
            <div class="item-header">
                <div>
                    <h4 class="item-title">${user.name}</h4>
                    <div class="item-meta">
                        ${user.email}
                        ${user.is_verified ? '<span class="badge badge-success">Verified</span>' : ''}
                    </div>
                </div>
                <div class="item-actions">
                    <button class="btn btn-outline btn-sm"
                            hx-get="/users/${user.id}"
                            hx-target="closest .list-item"
                            hx-swap="outerHTML">
                        Edit
                    </button>
                    <button class="btn btn-danger btn-sm"
                            hx-delete="/users/${user.id}"
                            hx-confirm="Are you sure you want to delete this user?"
                            hx-target="closest .list-item"
                            hx-swap="delete">
                        Delete
                    </button>
                </div>
            </div>
            <div class="item-meta">
                Created: ${utils.formatDate(user.created_at)}
                ${user.updated_at ? ` • Updated: ${utils.formatDate(user.updated_at)}` : ''}
            </div>
        </div>
    `).join('');
};

window.formatNews = function(news) {
    if (!news || news.length === 0) {
        return `
            <div class="empty-state">
                <div class="empty-state-icon">📝</div>
                <h3>No News Found</h3>
                <p>Create your first news article to get started.</p>
            </div>
        `;
    }

    return news.map(item => `
        <div class="list-item">
            <div class="item-header">
                <div>
                    <h4 class="item-title">${item.title}</h4>
                    <div class="item-meta">
                        By ${item.author?.name || 'Unknown Author'}
                        ${item.cover ? '<span class="badge">Has Cover</span>' : ''}
                    </div>
                </div>
                <div class="item-actions">
                    <button class="btn btn-outline btn-sm"
                            hx-get="/news/${item.id}"
                            hx-target="closest .list-item"
                            hx-swap="outerHTML">
                        Edit
                    </button>
                    <button class="btn btn-danger btn-sm"
                            hx-delete="/news/${item.id}"
                            hx-confirm="Are you sure you want to delete this news article?"
                            hx-target="closest .list-item"
                            hx-swap="delete">
                        Delete
                    </button>
                </div>
            </div>
            <div class="item-content">
                <p>${utils.truncateText(typeof item.content === 'object' ? JSON.stringify(item.content) : item.content)}</p>
            </div>
            <div class="item-meta">
                Published: ${utils.formatDate(item.created_at)}
            </div>
        </div>
    `).join('');
};

window.formatComments = function(comments) {
    if (!comments || comments.length === 0) {
        return `
            <div class="empty-state">
                <div class="empty-state-icon">💬</div>
                <h3>No Comments Found</h3>
                <p>No comments have been posted yet.</p>
            </div>
        `;
    }


// Modal management
window.modalManager = {
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    },
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    },
    
    closeAllModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
        document.body.style.overflow = 'auto';
    }
};

// Close modal when clicking outside content
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        window.modalManager.closeModal(event.target.id);
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        window.modalManager.closeAllModals();
    }
});


// Global modal functions
window.openModal = window.modalManager.openModal;
window.closeModal = window.modalManager.closeModal;


    return comments.map(comment => `
        <div class="list-item">
            <div class="item-header">
                <div>
                    <h4 class="item-title">Comment by ${comment.author?.name || 'Unknown User'}</h4>
                    <div class="item-meta">
                        On News ID: ${comment.news_id}
                    </div>
                </div>
                <div class="item-actions">
                    <button class="btn btn-outline btn-sm"
                            hx-get="/comments/${comment.id}"
                            hx-target="closest .list-item"
                            hx-swap="outerHTML">
                        Edit
                    </button>
                    <button class="btn btn-danger btn-sm"
                            hx-delete="/comments/${comment.id}"
                            hx-confirm="Are you sure you want to delete this comment?"
                            hx-target="closest .list-item"
                            hx-swap="delete">
                        Delete
                    </button>
                </div>
            </div>
            <div class="item-content">
                <p>${comment.text}</p>
            </div>
            <div class="item-meta">
                Posted: ${utils.formatDate(comment.created_at)}
            </div>
        </div>
    `).join('');
};
