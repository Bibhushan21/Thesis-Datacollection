// Dedicated Mobile Menu Handler
// This ensures mobile menu works consistently across all pages

(function() {
    'use strict';
    
    let isInitialized = false;
    
    function initializeMobileMenu() {
        // Prevent multiple initializations
        if (isInitialized) {
            return;
        }
        
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (!mobileMenuButton || !mobileMenu) {
            console.warn('Mobile menu elements not found');
            return;
        }
        
        console.log('Initializing mobile menu...');
        
        // Remove any existing event listeners
        const newButton = mobileMenuButton.cloneNode(true);
        mobileMenuButton.parentNode.replaceChild(newButton, mobileMenuButton);
        
        // Add click event listener
        newButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Mobile menu button clicked');
            
            // Toggle the mobile menu
            mobileMenu.classList.toggle('hidden');
            
            // Toggle aria-expanded for accessibility
            const isExpanded = !mobileMenu.classList.contains('hidden');
            newButton.setAttribute('aria-expanded', isExpanded);
            
            // Change hamburger icon to X when menu is open
            const svg = newButton.querySelector('svg');
            if (svg) {
                if (isExpanded) {
                    // Change to X icon
                    svg.innerHTML = '<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M6 18L18 6M6 6l12 12\"></path>';
                } else {
                    // Change back to hamburger icon
                    svg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>';
                }
            }
            
            console.log('Mobile menu toggled, hidden:', mobileMenu.classList.contains('hidden'));
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!newButton.contains(e.target) && !mobileMenu.contains(e.target)) {
                if (!mobileMenu.classList.contains('hidden')) {
                    mobileMenu.classList.add('hidden');
                    newButton.setAttribute('aria-expanded', 'false');
                    
                    // Reset to hamburger icon
                    const svg = newButton.querySelector('svg');
                    if (svg) {
                        svg.innerHTML = '<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M4 6h16M4 12h16M4 18h16\"></path>';
                    }
                                 }
            }
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !mobileMenu.classList.contains('hidden')) {
                mobileMenu.classList.add('hidden');
                newButton.setAttribute('aria-expanded', 'false');
                newButton.focus();
                
                // Reset to hamburger icon
                const svg = newButton.querySelector('svg');
                if (svg) {
                    svg.innerHTML = '<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M4 6h16M4 12h16M4 18h16\"></path>';
                }
            }
        });
        
        // Set initial aria-expanded
        newButton.setAttribute('aria-expanded', 'false');
        
        isInitialized = true;
        console.log('Mobile menu initialized successfully');
    }
    
    function initializeMoreMenu() {
        const moreMenuButton = document.getElementById('more-menu-button');
        const moreMenu = document.getElementById('more-menu');
        
        if (!moreMenuButton || !moreMenu) {
            return; // Elements not found on this page
        }
        
        moreMenuButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            moreMenu.classList.toggle('hidden');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!moreMenuButton.contains(e.target) && !moreMenu.contains(e.target)) {
                moreMenu.classList.add('hidden');
            }
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !moreMenu.classList.contains('hidden')) {
                moreMenu.classList.add('hidden');
                moreMenuButton.focus();
            }
        });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeMobileMenu);
    } else {
        initializeMobileMenu();
    }
    
    // Also initialize after a short delay to catch any dynamically loaded content
    setTimeout(initializeMobileMenu, 100);
    
            // Export for manual initialization if needed
        window.initializeMobileMenu = initializeMobileMenu;
        
        // Initialize "More" menu for intermediate sizes
        initializeMoreMenu();
    
})(); 