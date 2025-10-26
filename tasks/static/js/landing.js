// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        // Add/remove scrolled class
        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        // Hide/show navbar on scroll (optional)
        if (currentScroll > lastScroll && currentScroll > 300) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScroll = currentScroll;
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            
            if (target) {
                const offset = 80; // Navbar height
                const targetPosition = target.offsetTop - offset;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Animate numbers on scroll
    const animateNumbers = () => {
        const numbers = document.querySelectorAll('.stat-number');
        
        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -100px 0px'
        };

        const observerCallback = (entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const targetText = element.textContent;
                    const targetNumber = parseInt(targetText.replace(/\D/g, ''));
                    const suffix = targetText.replace(/[0-9]/g, '');
                    const duration = 2000; // Animation duration in ms
                    const start = 0;
                    const increment = targetNumber / (duration / 16);
                    let current = start;

                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= targetNumber) {
                            current = targetNumber;
                            clearInterval(timer);
                        }
                        element.textContent = Math.floor(current) + suffix;
                    }, 16);

                    observer.unobserve(element);
                }
            });
        };

        const observer = new IntersectionObserver(observerCallback, observerOptions);
        numbers.forEach(number => observer.observe(number));
    };

    animateNumbers();

    // Add animation classes on scroll
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.stat-card, .feature-image, .solution-card');
        
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observerCallback = (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        };

        const observer = new IntersectionObserver(observerCallback, observerOptions);
        elements.forEach(element => observer.observe(element));
    };

    animateOnScroll();

    // Parallax effect for floating elements
    const parallaxElements = document.querySelectorAll('.float-card, .float-pill');
    
    if (parallaxElements.length > 0) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach((element, index) => {
                const speed = 0.5 + (index * 0.1);
                const yPos = -(scrolled * speed * 0.5);
                
                if (element.style) {
                    element.style.transform = `translateY(${yPos}px)`;
                }
            });
        });
    }

    // Active navigation link highlighting
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');

    window.addEventListener('scroll', () => {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (pageYOffset >= (sectionTop - 100)) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').slice(1) === current) {
                link.classList.add('active');
            }
        });
    });

    // Mobile menu toggle enhancement
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                if (navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            }
        });

        // Close mobile menu when clicking on a nav link
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            });
        });
    }

    // Add hover effect to cards
    const cards = document.querySelectorAll('.stat-card, .solution-card, .float-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
            this.style.transition = 'all 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Typing animation for hero title (optional)
    const typeWriter = (element, text, speed = 50) => {
        let index = 0;
        element.textContent = '';
        
        const type = () => {
            if (index < text.length) {
                element.textContent += text.charAt(index);
                index++;
                setTimeout(type, speed);
            }
        };
        
        type();
    };

    // Uncomment to enable typing animation
    // const heroTitle = document.querySelector('.hero-title');
    // if (heroTitle) {
    //     const originalText = heroTitle.textContent;
    //     typeWriter(heroTitle, originalText, 50);
    // }

    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn-hero-primary, .btn-get-started, .btn-cta, .btn-solution, .btn-insights');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(255, 255, 255, 0.6)';
            ripple.style.transform = 'scale(0)';
            ripple.style.animation = 'ripple-animation 0.6s ease-out';
            ripple.style.pointerEvents = 'none';
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add ripple animation CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // Lazy loading for images
    const images = document.querySelectorAll('img');
    
    const imageOptions = {
        threshold: 0,
        rootMargin: '0px 0px 50px 0px'
    };

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                // If the image has a data-src attribute, use it for lazy loading
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                }
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    }, imageOptions);

    images.forEach(img => imageObserver.observe(img));

    // Form validation (for future forms)
    const validateEmail = (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    };

    // Handle any future forms
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const emailInput = this.querySelector('input[type="email"]');
            
            if (emailInput && !validateEmail(emailInput.value)) {
                e.preventDefault();
                emailInput.classList.add('is-invalid');
                
                // Show error message
                let errorMsg = emailInput.nextElementSibling;
                if (!errorMsg || !errorMsg.classList.contains('invalid-feedback')) {
                    errorMsg = document.createElement('div');
                    errorMsg.classList.add('invalid-feedback');
                    errorMsg.textContent = 'Please enter a valid email address';
                    emailInput.parentNode.appendChild(errorMsg);
                }
            }
        });
    });

    // Dynamic copyright year
    const copyrightElement = document.querySelector('.footer-bottom p');
    if (copyrightElement) {
        const currentYear = new Date().getFullYear();
        copyrightElement.innerHTML = copyrightElement.innerHTML.replace(/2025/g, currentYear);
    }

    // Performance optimization: Debounce scroll events
    let scrollTimeout;
    const debounce = (func, wait) => {
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(scrollTimeout);
                func(...args);
            };
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(later, wait);
        };
    };

    // Apply debounce to scroll-heavy functions
    const debouncedScroll = debounce(() => {
        // Add any scroll-dependent functions here
    }, 100);

    window.addEventListener('scroll', debouncedScroll);

    // Initialize Bootstrap tooltips (if any)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined' && tooltipTriggerList.length > 0) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Console message
    console.log('%c Misala - Task Management System ', 'background: #6C5CE7; color: white; padding: 5px 10px; border-radius: 3px;');
    console.log('Welcome to Misala! 🚀');
});

// Handle page visibility changes (pause animations when tab is not visible)
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Pause animations
        document.querySelectorAll('.float-card, .float-pill').forEach(el => {
            if (el.style) {
                el.style.animationPlayState = 'paused';
            }
        });
    } else {
        // Resume animations
        document.querySelectorAll('.float-card, .float-pill').forEach(el => {
            if (el.style) {
                el.style.animationPlayState = 'running';
            }
        });
    }
});