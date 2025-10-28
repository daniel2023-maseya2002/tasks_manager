/**
 * Misala - User Management Modern JavaScript
 * Enhanced interactions and animations for user management interfaces
 * Version: 1.0
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize Bootstrap tooltips
  initializeTooltips();
  
  // Initialize user action modal functionality
  setupUserActionModals();
  
  // Setup data table functionality
  setupDataTables();
  
  // Initialize counter animations
  animateCounters();
  
  // Setup row hover effects
  setupRowHoverEffects();
  
  // Setup form validations and animations
  setupFormAnimations();
  
  // Setup filter dropdowns
  setupFilterDropdowns();
  
  // Setup status badges pulse effect
  setupStatusBadges();
  
  // Setup profile picture upload
  setupProfilePictureUpload();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl, {
      boundary: document.body,
      delay: { show: 500, hide: 100 }
    });
  });
}

/**
 * Setup modals for user actions (block, warn, activate, etc)
 */
function setupUserActionModals() {
  const actionButtons = document.querySelectorAll('[data-action]');
  const userActionModal = document.getElementById('userActionModal');
  
  if (!userActionModal || actionButtons.length === 0) return;
  
  const modalInstance = new bootstrap.Modal(userActionModal);
  const actionTypeField = document.getElementById('actionTypeField');
  const actionWarning = document.getElementById('actionWarning');
  const actionWarningText = document.getElementById('actionWarningText');
  const confirmActionButton = document.getElementById('confirmActionButton');
  const passwordResetFields = document.getElementById('passwordResetFields');
  
  actionButtons.forEach(button => {
    button.addEventListener('click', (e) => {
      e.preventDefault();
      
      const actionType = button.getAttribute('data-action');
      const userId = button.getAttribute('data-user-id');
      const username = button.getAttribute('data-username') || 'this user';
      
      actionTypeField.value = actionType;
      
      if (passwordResetFields) {
        passwordResetFields.classList.add('d-none');
      }
      
      // Set modal title and button text based on action
      document.getElementById('userActionModalLabel').textContent = 
        formatActionText(actionType) + ' User';
      
      confirmActionButton.textContent = formatActionText(actionType);
      
      // Set warning message and button style based on action
      setupModalForAction(actionType, username, confirmActionButton, actionWarning, actionWarningText, passwordResetFields);
      
      // Show with entrance animation
      userActionModal.classList.add('fade');
      modalInstance.show();
      
      // Add entrance animation after modal is shown
      setTimeout(() => {
        const modalDialog = userActionModal.querySelector('.modal-dialog');
        if (modalDialog) {
          modalDialog.style.transform = 'translateY(0)';
          modalDialog.style.opacity = '1';
        }
      }, 150);
    });
  });
  
  // Password validation for reset password
  setupPasswordValidation();
}

/**
 * Format action text for display
 */
function formatActionText(actionType) {
  // Convert 'reset-password' to 'Reset Password'
  return actionType
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Setup modal for specific action type
 */
function setupModalForAction(actionType, username, confirmButton, warningEl, warningTextEl, passwordFieldsEl) {
  if (actionType === 'block') {
    confirmButton.className = 'btn btn-danger';
    warningEl.className = 'alert alert-danger';
    warningEl.classList.remove('d-none');
    warningTextEl.textContent = `This will prevent ${username} from logging in and using the system.`;
  } else if (actionType === 'warn') {
    confirmButton.className = 'btn btn-warning';
    warningEl.className = 'alert alert-warning';
    warningEl.classList.remove('d-none');
    warningTextEl.textContent = `This will flag ${username}'s account with a warning.`;
  } else if (actionType === 'delete') {
    confirmButton.className = 'btn btn-danger';
    warningEl.className = 'alert alert-danger';
    warningEl.classList.remove('d-none');
    warningTextEl.textContent = `This will permanently delete ${username}'s account. This action cannot be undone.`;
  } else if (actionType === 'reset-password' && passwordFieldsEl) {
    confirmButton.className = 'btn btn-primary';
    passwordFieldsEl.classList.remove('d-none');
    warningEl.classList.add('d-none');
  } else {
    confirmButton.className = 'btn btn-primary';
    warningEl.classList.add('d-none');
  }
}

/**
 * Setup password validation for reset password fields
 */
function setupPasswordValidation() {
  const newPasswordField = document.getElementById('newPassword');
  const confirmPasswordField = document.getElementById('confirmPassword');
  const passwordMismatch = document.getElementById('passwordMismatch');
  const confirmActionButton = document.getElementById('confirmActionButton');
  
  if (!newPasswordField || !confirmPasswordField || !passwordMismatch) return;
  
  const validatePasswords = () => {
    if (confirmPasswordField.value && newPasswordField.value !== confirmPasswordField.value) {
      passwordMismatch.classList.remove('d-none');
      confirmActionButton.disabled = true;
    } else {
      passwordMismatch.classList.add('d-none');
      confirmActionButton.disabled = false;
    }
  };
  
  confirmPasswordField.addEventListener('input', validatePasswords);
  newPasswordField.addEventListener('input', validatePasswords);
}

/**
 * Setup data tables functionality
 */
function setupDataTables() {
  // If you're using a DataTable library
  const userTable = document.querySelector('.modern-table');
  
  if (!userTable) return;
  
  // Add sorting indicators to table headers
  const tableHeaders = userTable.querySelectorAll('thead th');
  tableHeaders.forEach(header => {
    if (!header.classList.contains('no-sort')) {
      header.style.cursor = 'pointer';
      header.addEventListener('click', () => sortTable(header));
      header.innerHTML += '<span class="sort-icon ms-1"><i class="bi bi-chevron-expand fs-xs"></i></span>';
    }
  });
}

/**
 * Basic table sorting functionality 
 */
function sortTable(header) {
  const table = header.closest('table');
  const columnIndex = Array.from(header.parentNode.children).indexOf(header);
  const rows = Array.from(table.querySelectorAll('tbody tr'));
  const isAscending = header.getAttribute('data-sort') !== 'asc';
  
  // Reset sort indicators
  table.querySelectorAll('thead th').forEach(th => {
    th.removeAttribute('data-sort');
    const icon = th.querySelector('.sort-icon i');
    if (icon) icon.className = 'bi bi-chevron-expand fs-xs';
  });
  
  // Set current sort direction
  header.setAttribute('data-sort', isAscending ? 'asc' : 'desc');
  const sortIcon = header.querySelector('.sort-icon i');
  if (sortIcon) {
    sortIcon.className = isAscending ? 'bi bi-chevron-up fs-xs' : 'bi bi-chevron-down fs-xs';
  }
  
  // Sort the rows
  rows.sort((rowA, rowB) => {
    const cellA = rowA.cells[columnIndex].textContent.trim();
    const cellB = rowB.cells[columnIndex].textContent.trim();
    
    // Special case for dates and numbers
    if (!isNaN(Date.parse(cellA)) && !isNaN(Date.parse(cellB))) {
      return isAscending ? 
        new Date(cellA) - new Date(cellB) : 
        new Date(cellB) - new Date(cellA);
    } else if (!isNaN(cellA) && !isNaN(cellB)) {
      return isAscending ? 
        parseFloat(cellA) - parseFloat(cellB) : 
        parseFloat(cellB) - parseFloat(cellA);
    } else {
      return isAscending ? 
        cellA.localeCompare(cellB) : 
        cellB.localeCompare(cellA);
    }
  });
  
  // Reorder the table
  const tbody = table.querySelector('tbody');
  rows.forEach(row => tbody.appendChild(row));
  
  // Add sort animation
  rows.forEach((row, index) => {
    row.style.animation = 'none';
    row.offsetHeight; // Trigger reflow
    row.style.animation = `fadeIn 0.3s ease forwards ${index * 0.05}s`;
  });
}

/**
 * Animate counter elements
 */
function animateCounters() {
  const counters = document.querySelectorAll('.user-count, .new-user-count, .active-user-count');
  
  counters.forEach(counter => {
    const targetValue = parseInt(counter.textContent, 10);
    if (isNaN(targetValue)) return;
    
    // Reset counter
    counter.textContent = '0';
    
    // Setup animation values
    const duration = 1500; // ms
    const frameDuration = 1000 / 60; // 60fps
    const totalFrames = Math.round(duration / frameDuration);
    const easeOutQuad = t => t * (2 - t);
    
    // Animate
    let frame = 0;
    const animate = () => {
      frame++;
      const progress = easeOutQuad(frame / totalFrames);
      const currentCount = Math.round(targetValue * progress);
      
      // Update counter
      counter.textContent = currentCount;
      
      // Continue animation if not complete
      if (frame < totalFrames) {
        requestAnimationFrame(animate);
      } else {
        counter.textContent = targetValue;
      }
    };
    
    // Start animation after a small delay
    setTimeout(() => requestAnimationFrame(animate), 300);
  });
}

/**
 * Setup hover effects for table rows
 */
function setupRowHoverEffects() {
  document.querySelectorAll('.modern-table tbody tr').forEach(row => {
    row.addEventListener('mouseenter', () => {
      row.style.transition = 'all 0.2s ease';
      row.style.backgroundColor = 'rgba(249, 250, 251, 0.7)';
      row.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.02)';
      row.style.transform = 'translateY(-1px)';
    });
    
    row.addEventListener('mouseleave', () => {
      row.style.backgroundColor = '';
      row.style.boxShadow = 'none';
      row.style.transform = '';
    });
    
    // Add click handler if the row has a data-href attribute
    if (row.hasAttribute('data-href')) {
      row.style.cursor = 'pointer';
      row.addEventListener('click', () => {
        window.location.href = row.getAttribute('data-href');
      });
    }
  });
}

/**
 * Setup form animations
 */
function setupFormAnimations() {
  // Form validation
  const forms = document.querySelectorAll('.needs-validation');
  
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
        
        // Add shake animation to invalid fields
        form.querySelectorAll(':invalid').forEach(field => {
          field.style.animation = 'none';
          field.offsetHeight; // Trigger reflow
          field.style.animation = 'shake 0.5s cubic-bezier(.36,.07,.19,.97) both';
        });
      }
      
      form.classList.add('was-validated');
    }, false);
  });
  
  // Floating labels animation
  const formControls = document.querySelectorAll('.form-floating .form-control, .form-floating .form-select');
  
  formControls.forEach(control => {
    if (control.value) {
      control.classList.add('filled');
      control.parentNode.classList.add('filled');
    }
    
    control.addEventListener('focus', () => {
      control.classList.add('focused');
      control.parentNode.classList.add('focused');
    });
    
    control.addEventListener('blur', () => {
      control.classList.remove('focused');
      control.parentNode.classList.remove('focused');
      
      if (control.value) {
        control.classList.add('filled');
        control.parentNode.classList.add('filled');
      } else {
        control.classList.remove('filled');
        control.parentNode.classList.remove('filled');
      }
    });
  });
}

/**
 * Setup filter dropdowns
 */
function setupFilterDropdowns() {
  // Status filter dropdown
  const statusFilters = document.querySelectorAll('[data-filter="status"]');
  
  statusFilters.forEach(filter => {
    filter.addEventListener('click', (e) => {
      e.preventDefault();
      
      const status = filter.getAttribute('data-value');
      const currentUrl = new URL(window.location.href);
      
      if (status) {
        currentUrl.searchParams.set('status', status);
      } else {
        currentUrl.searchParams.delete('status');
      }
      
      window.location.href = currentUrl.toString();
    });
  });
  
  // Role filter dropdown
  const roleFilters = document.querySelectorAll('[data-filter="role"]');
  
  roleFilters.forEach(filter => {
    filter.addEventListener('click', (e) => {
      e.preventDefault();
      
      const role = filter.getAttribute('data-value');
      const currentUrl = new URL(window.location.href);
      
      if (role) {
        currentUrl.searchParams.set('role', role);
      } else {
        currentUrl.searchParams.delete('role');
      }
      
      window.location.href = currentUrl.toString();
    });
  });
}

/**
 * Setup status badges with pulse effect
 */
function setupStatusBadges() {
  // Add pulse animation to active status dots
  document.querySelectorAll('.status-active .status-dot').forEach(dot => {
    dot.style.animation = 'pulse 2s infinite';
  });
  
  // Add warning animation to warning status dots
  document.querySelectorAll('.status-warned .status-dot').forEach(dot => {
    dot.style.animation = 'pulse 1s infinite';
  });
}

/**
 * Setup profile picture upload functionality
 */
function setupProfilePictureUpload() {
  const uploadBtn = document.querySelector('.profile-upload-btn');
  const fileInput = document.getElementById('profile_picture');
  
  if (!uploadBtn || !fileInput) return;
  
  uploadBtn.addEventListener('click', function() {
    fileInput.click();
  });
  
  fileInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
      // Show loading state
      const profileImage = document.querySelector('.profile-image') || 
                          document.querySelector('.profile-image-placeholder');
      
      if (profileImage) {
        profileImage.style.opacity = '0.5';
      }
      
      // Add upload spinner to button
      uploadBtn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i>';
      
      // Submit form
      this.form.submit();
    }
  });
}

/**
 * Apply custom form classes to Django form rendering
 */
function applyFormStyling() {
  // Add Bootstrap classes to Django form elements
  const formControls = document.querySelectorAll('input, select, textarea');
  
  formControls.forEach(control => {
    if (!control.classList.contains('form-control') && 
        !control.classList.contains('form-select') && 
        !control.classList.contains('form-check-input') && 
        control.type !== 'hidden' && 
        control.type !== 'submit' && 
        control.type !== 'button') {
      
      if (control.tagName === 'SELECT') {
        control.classList.add('form-select');
      } else if (control.type === 'checkbox' || control.type === 'radio') {
        control.classList.add('form-check-input');
      } else if (control.type !== 'file') {
        control.classList.add('form-control');
      }
    }
  });
  
  // Style form labels
  document.querySelectorAll('label').forEach(label => {
    if (!label.classList.contains('form-check-label') && 
        !label.classList.contains('form-label')) {
      label.classList.add('form-label');
    }
  });
}

// Apply custom form styling
document.addEventListener('DOMContentLoaded', applyFormStyling);

// Add CSS for animations
document.head.insertAdjacentHTML('beforeend', `
<style>
@keyframes shake {
  10%, 90% { transform: translateX(-1px); }
  20%, 80% { transform: translateX(2px); }
  30%, 50%, 70% { transform: translateX(-4px); }
  40%, 60% { transform: translateX(4px); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spin {
  animation: spin 1s linear infinite;
}

.modal-dialog {
  transition: transform 0.3s ease, opacity 0.3s ease;
  transform: translateY(-20px);
  opacity: 0;
}
</style>
`);