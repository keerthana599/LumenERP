// Main JavaScript functions

// Country code and phone number validation data
const COUNTRY_PHONE_DATA = {
    'IN': { code: '+91', maxDigits: 10, flag: '🇮🇳', name: 'India' },
    'US': { code: '+1', maxDigits: 10, flag: '🇺🇸', name: 'United States' },
    'GB': { code: '+44', maxDigits: 10, flag: '🇬🇧', name: 'United Kingdom' },
    'AU': { code: '+61', maxDigits: 9, flag: '🇦🇺', name: 'Australia' },
    'CA': { code: '+1', maxDigits: 10, flag: '🇨🇦', name: 'Canada' },
    'SG': { code: '+65', maxDigits: 8, flag: '🇸🇬', name: 'Singapore' },
    'MY': { code: '+60', maxDigits: 9, flag: '🇲🇾', name: 'Malaysia' },
    'PK': { code: '+92', maxDigits: 10, flag: '🇵🇰', name: 'Pakistan' },
    'BD': { code: '+880', maxDigits: 10, flag: '🇧🇩', name: 'Bangladesh' },
    'NZ': { code: '+64', maxDigits: 9, flag: '🇳🇿', name: 'New Zealand' },
    'AE': { code: '+971', maxDigits: 9, flag: '🇦🇪', name: 'United Arab Emirates' },
    'JP': { code: '+81', maxDigits: 10, flag: '🇯🇵', name: 'Japan' },
    'DE': { code: '+49', maxDigits: 11, flag: '🇩🇪', name: 'Germany' },
    'FR': { code: '+33', maxDigits: 9, flag: '🇫🇷', name: 'France' },
    'IT': { code: '+39', maxDigits: 10, flag: '🇮🇹', name: 'Italy' }
};

// Get country list sorted by name
function getCountryList() {
    return Object.entries(COUNTRY_PHONE_DATA)
        .map(([code, data]) => ({
            code: code,
            ...data
        }))
        .sort((a, b) => a.name.localeCompare(b.name));
}

// Handle country code change
function handleCountryChange(event) {
    const countryCode = event.target.value;
    const countryData = COUNTRY_PHONE_DATA[countryCode];
    
    if (!countryData) return;
    
    // Find the phone input field
    const phoneInput = event.target.closest('.country-phone-group')?.querySelector('input[type="tel"]');
    if (!phoneInput) return;
    
    // Update max length
    phoneInput.maxLength = countryData.maxDigits;
    
    // Update the data attribute for validation
    phoneInput.dataset.countryCode = countryCode;
    phoneInput.dataset.maxDigits = countryData.maxDigits;
    
    // Only clear phone input if user manually changed country (not during initialization)
    // Check if this is a programmatic change by checking if the event was dispatched internally
    if (event.isTrusted) {
        // User manually changed the country dropdown - clear the phone
        phoneInput.value = '';
    }
    
    // Update placeholder
    phoneInput.placeholder = `${countryData.maxDigits} digit number`;
    
    // Add validation hint
    const hint = event.target.closest('.country-phone-group')?.querySelector('.phone-hint');
    if (hint) {
        hint.textContent = `${countryData.name} (${countryData.code}): Max ${countryData.maxDigits} digits`;
    }
}

// Validate phone number
function validatePhoneNumber(phoneInput) {
    const countryCode = phoneInput.dataset.countryCode;
    const maxDigits = parseInt(phoneInput.dataset.maxDigits || '10');
    const phoneValue = phoneInput.value.replace(/\D/g, ''); // Remove non-digits
    
    if (!phoneValue) return true; // Empty is OK if not required
    
    // Check if phone number exceeds max digits
    if (phoneValue.length > maxDigits) {
        phoneInput.classList.add('border-red-500');
        const errorSpan = phoneInput.closest('.country-phone-group')?.querySelector('.phone-error');
        if (errorSpan) {
            errorSpan.textContent = `Maximum ${maxDigits} digits allowed`;
            errorSpan.style.display = 'block';
        }
        return false;
    } else {
        phoneInput.classList.remove('border-red-500');
        const errorSpan = phoneInput.closest('.country-phone-group')?.querySelector('.phone-error');
        if (errorSpan) {
            errorSpan.style.display = 'none';
        }
    }
    
    return true;
}

// Initialize country phone inputs
function initializeCountryPhoneInputs() {
    document.querySelectorAll('.country-select').forEach(select => {
        select.addEventListener('change', handleCountryChange);
        
        // Validate on phone input change
        const phoneInput = select.closest('.country-phone-group')?.querySelector('input[type="tel"]');
        if (phoneInput) {
            phoneInput.addEventListener('input', function() {
                validatePhoneNumber(this);
            });
            
            phoneInput.addEventListener('blur', function() {
                validatePhoneNumber(this);
            });
        }
    });
    
    // Add form submission validation for all forms with country-phone-group
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const phoneInputs = this.querySelectorAll('input[type="tel"]');
            let isValid = true;
            
            phoneInputs.forEach(phoneInput => {
                if (phoneInput.closest('.country-phone-group')) {
                    // Only validate if phone field has a value
                    if (phoneInput.value.trim()) {
                        if (!validatePhoneNumber(phoneInput)) {
                            isValid = false;
                        }
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fix the phone number validation errors before submitting.');
            }
        });
    });
}

// Toggle Sidebar (for admin/faculty portals)
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const checkbox = document.getElementById('sidebarCheckbox');
    const barsIcon = document.getElementById('sidebarBarsIcon');
    const closeIcon = document.getElementById('sidebarCloseIcon');
    
    if (sidebar) {
        sidebar.classList.toggle('hidden');
        
        // Toggle icon visibility
        if (sidebar.classList.contains('hidden')) {
            // Hidden: Show hamburger icon
            if (barsIcon) barsIcon.style.display = 'inline-block';
            if (closeIcon) closeIcon.style.display = 'none';
        } else {
            // Visible: Show close icon
            if (barsIcon) barsIcon.style.display = 'none';
            if (closeIcon) closeIcon.style.display = 'inline-block';
        }
        
        // Save preference to localStorage
        localStorage.setItem('sidebarHidden', sidebar.classList.contains('hidden'));
    }
}

// Toggle Navbar (for student portal)
function toggleNavbar() {
    const navbar = document.getElementById('navbar');
    const checkbox = document.getElementById('navbarCheckbox');
    const floatingToggle = document.getElementById('floatingToggle');
    const barsIcon = document.getElementById('navbarBarsIcon');
    const closeIcon = document.getElementById('navbarCloseIcon');
    
    if (navbar) {
        navbar.classList.toggle('navbar-hidden');
        
        // Toggle icon visibility
        if (navbar.classList.contains('navbar-hidden')) {
            // Hidden: Show hamburger icon
            if (barsIcon) barsIcon.style.display = 'inline-block';
            if (closeIcon) closeIcon.style.display = 'none';
        } else {
            // Visible: Show close icon
            if (barsIcon) barsIcon.style.display = 'none';
            if (closeIcon) closeIcon.style.display = 'inline-block';
        }
        
        if (floatingToggle) {
            floatingToggle.classList.toggle('hidden');
        }
    }
}

// Initialize toggle states from localStorage
document.addEventListener('DOMContentLoaded', function() {
    // Initialize country phone inputs
    initializeCountryPhoneInputs();
    
    // Restore sidebar state only when page uses checkbox toggle (e.g. student portal)
    const sidebar = document.getElementById('sidebar');
    const sidebarCheckbox = document.getElementById('sidebarCheckbox');
    const sidebarBarsIcon = document.getElementById('sidebarBarsIcon');
    const sidebarCloseIcon = document.getElementById('sidebarCloseIcon');
    
    if (sidebar && sidebarCheckbox) {
        if (localStorage.getItem('sidebarHidden') === 'true') {
            sidebar.classList.add('hidden');
            if (sidebarBarsIcon) sidebarBarsIcon.style.display = 'inline-block';
            if (sidebarCloseIcon) sidebarCloseIcon.style.display = 'none';
        } else {
            if (sidebarBarsIcon) sidebarBarsIcon.style.display = 'none';
            if (sidebarCloseIcon) sidebarCloseIcon.style.display = 'inline-block';
        }
    }

    // Restore navbar state
    const navbar = document.getElementById('navbar');
    const navbarCheckbox = document.getElementById('navbarCheckbox');
    const navbarBarsIcon = document.getElementById('navbarBarsIcon');
    const navbarCloseIcon = document.getElementById('navbarCloseIcon');
    const initialFloatingToggle = document.getElementById('floatingToggle');
    
    if (navbar) {
        // Always start with navbar hidden; user must click to show it
        navbar.classList.add('navbar-hidden');
        if (initialFloatingToggle) {
            // Show the floating toggle so user can open navbar when needed
            initialFloatingToggle.classList.remove('hidden');
        }
        if (navbarCheckbox) {
            navbarCheckbox.checked = false;
        }
        if (navbarBarsIcon) navbarBarsIcon.style.display = 'inline-block';
        if (navbarCloseIcon) navbarCloseIcon.style.display = 'none';
    }

    // Add event listeners for toggle checkboxes
    if (sidebarCheckbox) {
        sidebarCheckbox.addEventListener('change', toggleSidebar);
    }

    const navbarCheckboxBtn = document.getElementById('navbarCheckbox');
    if (navbarCheckboxBtn) {
        navbarCheckboxBtn.addEventListener('change', toggleNavbar);
    }

    const floatingToggle = document.getElementById('floatingToggle');
    if (floatingToggle) {
        floatingToggle.addEventListener('click', function() {
            const checkbox = document.getElementById('navbarCheckbox');
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
                checkbox.dispatchEvent(new Event('change'));
            }
        });
    }

    // Toggle mobile menu
    const menu = document.querySelector('.mobile-menu');
    if (menu) {
        menu.classList.toggle('hidden');
    }

    // Close flash messages after 5 seconds
    const alerts = document.querySelectorAll('[role="alert"]');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease-out';
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
});

// Confirm before delete
function confirmDelete(message = 'Are you sure?') {
    return confirm(message);
}

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0
    }).format(value);
}

// Show loading spinner
function showLoading() {
    const spinner = document.createElement('div');
    spinner.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    spinner.innerHTML = `
        <div class="bg-white rounded-lg p-8">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p class="text-center mt-4 text-gray-700">Loading...</p>
        </div>
    `;
    document.body.appendChild(spinner);
    return spinner;
}

// Hide loading spinner
function hideLoading(spinner) {
    if (spinner) {
        spinner.remove();
    }
}

// Validate email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Format date to DD-MM-YYYY
function formatDate(dateString) {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}-${month}-${year}`;
}

// Get URL parameter
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}
