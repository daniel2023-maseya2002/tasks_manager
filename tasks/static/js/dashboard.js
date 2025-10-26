/**
 * Modern Dashboard Animations and Interactions
 */

// Initialize animations when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Animate cards on page load
  animateCards();
  
  // Initialize notification counters
  initNotificationCounters();
  
  // Add hover effects to task cards
  setupTaskCardHovers();
  
  // Add parallax effect to card headers
  setupParallaxEffect();
  
  // Animate charts when they come into view
  observeCharts();
  
  // Smooth scroll for navigation links
  setupSmoothScroll();
});

// Animate cards with staggered entrance
function animateCards() {
  const cards = document.querySelectorAll('.modern-card, .card');
  
  cards.forEach((card, index) => {
    // Add initial invisible state if not already present
    if (!card.classList.contains('animate-ready')) {
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      card.classList.add('animate-ready');
    }
    
    // Animate with staggered delay
    setTimeout(() => {
      card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, 100 * index);
  });
}

// Initialize notification counter animations
function initNotificationCounters() {
  const counters = document.querySelectorAll('.display-3, .modern-progress-text');
  
  counters.forEach(counter => {
    const target = parseInt(counter.textContent);
    const duration = 1500; // ms
    const step = target / (duration / 30); // Update every 30ms
    
    let current = 0;
    const timer = setInterval(() => {
      current += step;
      if (current >= target) {
        counter.textContent = target;
        clearInterval(timer);
      } else {
        counter.textContent = Math.floor(current);
      }
    }, 30);
  });
}

// Add hover effects to task cards
function setupTaskCardHovers() {
  const taskRows = document.querySelectorAll('.modern-table tbody tr');
  
  taskRows.forEach(row => {
    row.addEventListener('mouseenter', () => {
      row.style.transition = 'all 0.3s ease';
      row.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
      row.style.cursor = 'pointer';
    });
    
    row.addEventListener('mouseleave', () => {
      row.style.boxShadow = 'none';
    });
    
    // Add click event to navigate to task detail
    row.addEventListener('click', () => {
      const taskId = row.getAttribute('data-task-id');
      if (taskId) {
        window.location.href = `/tasks/detail/${taskId}/`;
      }
    });
  });
}

// Add subtle parallax effect to card headers
function setupParallaxEffect() {
  const cards = document.querySelectorAll('.card');
  
  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      // Get card position
      const rect = card.getBoundingClientRect();
      
      // Calculate cursor position inside card
      const x = e.clientX - rect.left; 
      const y = e.clientY - rect.top;
      
      // Calculate rotation angles (subtle effect)
      const rotateX = (y / rect.height - 0.5) * 2; // -1 to 1
      const rotateY = (x / rect.width - 0.5) * -2; // -1 to 1
      
      // Apply transform only to the card header
      const header = card.querySelector('.card-header');
      if (header) {
        header.style.transition = 'transform 0.1s ease-out';
        header.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
      }
    });
    
    // Reset transform on mouse leave
    card.addEventListener('mouseleave', () => {
      const header = card.querySelector('.card-header');
      if (header) {
        header.style.transition = 'transform 0.5s ease-out';
        header.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
      }
    });
  });
}

// Animate charts when they become visible
function observeCharts() {
  if (!window.IntersectionObserver) return;
  
  const chartContainers = document.querySelectorAll('.chart-container');
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('chart-visible');
        // Add animation class to chart
        const canvas = entry.target.querySelector('canvas');
        if (canvas) {
          canvas.style.animation = 'fadeScale 0.8s ease-out forwards';
        }
        
        // Stop observing after animation
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  
  chartContainers.forEach(container => {
    // Add initial style
    container.style.opacity = '0.5';
    container.style.transform = 'scale(0.95)';
    // Start observing
    observer.observe(container);
  });
}

// Smooth scroll for navigation links
function setupSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
}

// Refresh data periodically (simulated for demo)
function setupDataRefresh() {
  // Auto-refresh data every 5 minutes
  setInterval(() => {
    if (document.visibilityState === 'visible') {
      // Simulated refresh effect
      const refreshButton = document.querySelector('.btn-outline-secondary .bi-arrow-repeat');
      if (refreshButton) {
        refreshButton.classList.add('spin-animation');
        setTimeout(() => {
          refreshButton.classList.remove('spin-animation');
          // Here you would normally fetch fresh data
          // For demo, we just show a message
          showToast('Dashboard data refreshed');
        }, 1000);
      }
    }
  }, 300000); // 5 minutes
}

// Show toast notification
function showToast(message) {
  // Create toast element
  const toast = document.createElement('div');
  toast.classList.add('dashboard-toast');
  toast.innerHTML = `
    <div class="toast-icon">
      <i class="bi bi-info-circle"></i>
    </div>
    <div class="toast-message">${message}</div>
  `;
  
  document.body.appendChild(toast);
  
  // Animate in
  setTimeout(() => {
    toast.classList.add('show');
  }, 100);
  
  // Remove after 3 seconds
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 500);
  }, 3000);
}

// Add CSS styles for animations
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeScale {
    from { opacity: 0.5; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
  }
  
  @keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
  }
  
  .chart-visible {
    opacity: 1 !important;
    transform: scale(1) !important;
    transition: opacity 0.8s ease, transform 0.8s ease;
  }
  
  .spin-animation {
    animation: spin 1s linear;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  .dashboard-toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    display: flex;
    align-items: center;
    background: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border-radius: 8px;
    padding: 12px 20px;
    transform: translateY(100px);
    opacity: 0;
    transition: transform 0.3s ease, opacity 0.3s ease;
    z-index: 1000;
  }
  
  .dashboard-toast.show {
    transform: translateY(0);
    opacity: 1;
  }
  
  .toast-icon {
    margin-right: 12px;
    color: #6366f1;
    font-size: 1.2rem;
  }
  
  .toast-message {
    font-size: 0.9rem;
    font-weight: 500;
  }
`;

document.head.appendChild(style);