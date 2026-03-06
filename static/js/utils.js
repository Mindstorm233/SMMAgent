/**
 * Utility Functions - Microfluidics Design System
 */

const Utils = {
    /**
     * Format a date to a readable string
     * @param {string|Date} date - Date to format
     * @returns {string} Formatted date string
     */
    formatDate(date) {
        const d = new Date(date);
        return d.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    /**
     * Format duration in milliseconds to a readable string
     * @param {number} ms - Duration in milliseconds
     * @returns {string} Formatted duration
     */
    formatDuration(ms) {
        if (ms < 1000) return `${ms}ms`;
        const seconds = (ms / 1000).toFixed(1);
        return `${seconds}s`;
    },

    /**
     * Generate a unique ID
     * @param {string} prefix - Optional prefix
     * @returns {string} Unique ID
     */
    generateId(prefix = 'id') {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    },

    /**
     * Debounce a function
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
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

    /**
     * Copy text to clipboard
     * @param {string} text - Text to copy
     * @returns {Promise<boolean>} Success status
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.error('Failed to copy:', err);
            return false;
        }
    },

    /**
     * Syntax highlight JSON
     * @param {object|string} json - JSON to highlight
     * @returns {string} HTML with syntax highlighting
     */
    highlightJSON(json) {
        const str = typeof json === 'string' ? json : JSON.stringify(json, null, 2);
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, (match) => {
                let cls = 'json-number';
                if (/^"/.test(match)) {
                    if (/:$/.test(match)) {
                        cls = 'json-key';
                        match = match.replace(/:$/, '');
                        return `<span class="${cls}">${match}</span>:`;
                    } else {
                        cls = 'json-string';
                    }
                } else if (/true|false/.test(match)) {
                    cls = 'json-boolean';
                } else if (/null/.test(match)) {
                    cls = 'json-null';
                }
                return `<span class="${cls}">${match}</span>`;
            });
    },

    /**
     * Show a toast notification
     * @param {string} message - Message to show
     * @param {string} type - Type: success, error, warning, info
     */
    showToast(message, type = 'info') {
        // Create toast container if not exists
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            container.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        gap: 10px;
      `;
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
      padding: 12px 20px;
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-lg);
      font-size: var(--text-sm);
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 8px;
      animation: slideIn 0.3s ease;
    `;

        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        toast.innerHTML = `<span>${icons[type] || icons.info}</span><span>${message}</span>`;
        container.appendChild(toast);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    /**
     * Create element from HTML string
     * @param {string} html - HTML string
     * @returns {Element} DOM element
     */
    createElement(html) {
        const template = document.createElement('template');
        template.innerHTML = html.trim();
        return template.content.firstChild;
    },

    /**
     * Escape HTML special characters
     * @param {string} str - String to escape
     * @returns {string} Escaped string
     */
    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
};

// Add toast animation styles
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
`;
document.head.appendChild(style);

// Export
window.Utils = Utils;
