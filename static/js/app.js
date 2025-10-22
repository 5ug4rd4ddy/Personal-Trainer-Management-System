/**
 * Main JavaScript file for Gym Management System
 * Handles form validation, AJAX requests, and UI interactions
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Gym Management System loaded');
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize confirmation dialogs
    initializeConfirmationDialogs();
});

/**
 * Initialize form validation for all forms
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize confirmation dialogs for delete actions
 */
function initializeConfirmationDialogs() {
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const message = this.getAttribute('data-confirm') || 'Apakah Anda yakin?';
            
            if (!confirm(message)) {
                event.preventDefault();
                return false;
            }
        });
    });
}

/**
 * Show loading spinner on form submission
 */
function showLoadingSpinner(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Menyimpan...';
        submitButton.disabled = true;
        
        // Store original text for restoration
        submitButton.setAttribute('data-original-text', originalText);
    }
}

/**
 * Hide loading spinner and restore button
 */
function hideLoadingSpinner(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        const originalText = submitButton.getAttribute('data-original-text');
        if (originalText) {
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }
    }
}

/**
 * Handle AJAX form submissions
 */
function handleAjaxForm(form, successCallback, errorCallback) {
    const formData = new FormData(form);
    
    showLoadingSpinner(form);
    
    fetch(form.action, {
        method: form.method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Network response was not ok');
    })
    .then(data => {
        hideLoadingSpinner(form);
        if (successCallback) {
            successCallback(data);
        }
    })
    .catch(error => {
        hideLoadingSpinner(form);
        console.error('Error:', error);
        if (errorCallback) {
            errorCallback(error);
        }
    });
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    if (alertContainer) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

/**
 * Format numbers for display
 */
function formatNumber(num) {
    return new Intl.NumberFormat('id-ID').format(num);
}

/**
 * Format currency for display
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR'
    }).format(amount);
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate phone number format (Indonesian)
 */
function isValidPhone(phone) {
    const phoneRegex = /^(\+62|62|0)[0-9]{9,13}$/;
    return phoneRegex.test(phone.replace(/\s+/g, ''));
}

// Ambil CSRF token dari input hidden
function getCsrfToken() {
    const tokenInput = document.getElementById('csrf_token');
    return tokenInput ? tokenInput.value : '';
}

// Inline editing untuk Actual Reps
const actualRepsInputs = document.querySelectorAll('input[data-detail-id][data-reps]');
actualRepsInputs.forEach(input => {
    input.addEventListener('change', function() {
        const detailId = input.getAttribute('data-detail-id');
        const repsNum = input.getAttribute('data-reps');
        const value = input.value;
        const csrfToken = getCsrfToken();
        fetch('/sessions/update_actual_reps', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                detail_id: detailId,
                reps_num: repsNum,
                value: value
            })
        })
        .then(response => {
            // Cek apakah response JSON atau HTML error
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            } else {
                return response.text().then(text => { throw new Error('Server error: ' + text); });
            }
        })
        .then(data => {
            if (!data.success) {
                alert('Gagal update actual reps: ' + data.message);
            }
        })
        .catch(error => {
            alert('Terjadi error: ' + error);
        });
    });
});