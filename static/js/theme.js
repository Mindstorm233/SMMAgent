/**
 * Theme Management - Microfluidics Design System
 * Handles light/dark theme switching
 */

const ThemeManager = {
  STORAGE_KEY: 'microfluidics-theme',
  
  /**
   * Initialize theme from localStorage or system preference
   */
  init() {
    const savedTheme = localStorage.getItem(this.STORAGE_KEY);
    if (savedTheme) {
      this.setTheme(savedTheme);
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.setTheme(prefersDark ? 'dark' : 'light');
    }
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem(this.STORAGE_KEY)) {
        this.setTheme(e.matches ? 'dark' : 'light');
      }
    });
  },
  
  /**
   * Set the current theme
   * @param {string} theme - 'light' or 'dark'
   */
  setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(this.STORAGE_KEY, theme);
    this.updateToggleButton();
  },
  
  /**
   * Get the current theme
   * @returns {string} 'light' or 'dark'
   */
  getTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
  },
  
  /**
   * Toggle between light and dark themes
   */
  toggle() {
    const currentTheme = this.getTheme();
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme);
  },
  
  /**
   * Update the toggle button icon
   */
  updateToggleButton() {
    const btn = document.querySelector('.theme-toggle');
    if (btn) {
      const theme = this.getTheme();
      btn.setAttribute('aria-label', `Switch to ${theme === 'light' ? 'dark' : 'light'} mode`);
    }
  }
};

// Initialize theme on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  
  // Bind toggle button
  const toggleBtn = document.querySelector('.theme-toggle');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => ThemeManager.toggle());
  }
});

// Export for use in other modules
window.ThemeManager = ThemeManager;
