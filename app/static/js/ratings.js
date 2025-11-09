/**
 * Simple Agent Rating System
 * Single review button that opens agent selection form
 */

class AgentRatingSystem {
    constructor() {
        this.ratings = new Map();
        this.currentUserId = null;
        this.ratingEndpoint = '/ratings';
        
        // Initialize when DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }

    /**
     * Initialize the rating system
     */
    initialize() {
        // Try to add button immediately
        this.addReviewButton();
        
        // Try again after 2 seconds (for dynamic content)
        setTimeout(() => {
            this.addReviewButton();
        }, 2000);
        
        // Try again after 5 seconds
        setTimeout(() => {
            this.addReviewButton();
        }, 5000);
        
        // Listen for analysis completion events
        this.listenForAnalysisCompletion();
    }

    /**
     * Listen for analysis completion to add button
     */
    listenForAnalysisCompletion() {
        // Listen for custom events that might indicate analysis completion
        document.addEventListener('analysisCompleted', () => {
            setTimeout(() => this.addReviewButton(), 1000);
        });
        
        // Also check periodically if buttons container becomes available
        const checkInterval = setInterval(() => {
            const buttonContainer = document.querySelector('.flex.flex-wrap.justify-center.gap-4');
            const downloadBtn = document.getElementById('downloadPdfBtn');
            const saveBtn = document.getElementById('saveAsTemplateBtn');
            
            // If we can see the action buttons and they're visible, try adding review button
            if (buttonContainer && (downloadBtn || saveBtn)) {
                const downloadVisible = downloadBtn && downloadBtn.style.display !== 'none';
                const saveVisible = saveBtn && saveBtn.style.display !== 'none';
                
                if (downloadVisible || saveVisible) {
                    this.addReviewButton();
                    
                    // Stop checking once we've found the buttons
                    if (document.querySelector('.main-review-btn')) {
                        clearInterval(checkInterval);
                    }
                }
            }
        }, 2000); // Check every 2 seconds
        
        // Stop checking after 30 seconds to avoid infinite checking
        setTimeout(() => {
            clearInterval(checkInterval);
        }, 30000);
    }

    /**
     * Add single review button to the action buttons container
     */
    addReviewButton() {
        // Target the specific button container
        const buttonContainer = document.querySelector('.flex.flex-wrap.justify-center.gap-4');
        
        if (!buttonContainer) {
            // Alternative selectors
            const altContainer = document.querySelector('[data-step="6"] .flex.gap-4') ||
                                document.getElementById('saveAsTemplateBtn')?.parentElement ||
                                document.querySelector('.flex.justify-center.pt-6 .flex') ||
                                document.querySelector('div.flex.flex-wrap.justify-center') ||
                                document.querySelector('.flex.gap-4') ||
                                document.querySelector('[data-step="6"]');
            
            if (altContainer) {
                this.createAndInsertReviewButton(altContainer);
            }
            return;
        }

        // Create review button in the same container
        this.createAndInsertReviewButton(buttonContainer);
    }

    /**
     * Create and insert the review button
     */
    createAndInsertReviewButton(container, referenceElement = null) {
        // Check if review button already exists
        if (container.querySelector('.main-review-btn')) {
            return;
        }

        const reviewButton = document.createElement('button');
        reviewButton.type = 'button';
        reviewButton.className = 'main-review-btn group relative bg-gradient-to-r from-brand-lapis to-brand-pervenche text-white font-brand-black font-bold px-8 py-4 rounded-2xl hover:from-brand-oxford hover:to-brand-lapis focus:outline-none focus:ring-4 focus:ring-brand-lapis/30 shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 text-lg';
        reviewButton.style.display = 'inline-flex';
        
        reviewButton.innerHTML = `
            <span class="flex items-center">
                <svg class="w-5 h-5 mr-2 group-hover:animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
                </svg>
                Review Analysis
            </span>
            <!-- Hover effect overlay -->
            <div class="absolute inset-0 bg-white/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        `;
        
        reviewButton.onclick = () => this.showReviewModal();
        
        // Add button to the container (it will appear alongside the other buttons)
        container.appendChild(reviewButton);
    }

    /**
     * Show review modal with agent selection
     */
    showReviewModal() {
        // Remove existing modal if any
        const existingModal = document.getElementById('reviewModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Get list of completed agents
        const agents = this.getCompletedAgents();
        
        // Find the review button that was clicked to position modal near it
        const reviewButton = document.querySelector('.main-review-btn');
        console.log('Found review button:', reviewButton, reviewButton ? reviewButton.getBoundingClientRect() : 'not found');
        
        // Create modal
        const modal = this.createReviewModal(agents);
        document.body.appendChild(modal);
        
        // Position modal near the review button
        if (reviewButton) {
            this.positionModalNearButton(modal, reviewButton);
        }
    }

    /**
     * Get list of completed agents from the page
     */
    getCompletedAgents() {
        const agents = [
            'Problem Explorer',
            'Best Practices', 
            'Horizon Scanning',
            'Scenario Planning',
            'Research Synthesis',
            'Strategic Action',
            'High Impact',
            'Backcasting'
        ];
        
        // Filter to only show agents that are actually completed on the page
        return agents.filter(agent => {
            const text = document.body.textContent.toLowerCase();
            return text.includes(agent.toLowerCase()) && text.includes('completed');
        });
    }

    /**
     * Create review modal HTML
     */
    createReviewModal(agents) {
        const modal = document.createElement('div');
        modal.id = 'reviewModal';
        modal.className = 'review-modal-overlay';
        
        modal.innerHTML = `
            <div class="review-modal">
                <div class="review-modal-header">
                    <h2>Review Analysis</h2>
                    <button class="modal-close" onclick="AgentRatingSystem.closeModal(this)">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                        </svg>
                    </button>
                </div>
                
                <div class="review-modal-content">
                    <p>Select the agents you want to review:</p>
                    
                    <div class="agent-selection">
                        ${agents.map(agent => `
                            <label class="agent-option">
                                <input type="checkbox" value="${agent}" class="agent-checkbox">
                                <span class="agent-name">${agent}</span>
                            </label>
                        `).join('')}
                    </div>
                    
                    <div class="review-form" id="reviewForm" style="display: none;">
                        <div class="form-group">
                            <label class="form-label">Overall Rating *</label>
                            <div class="star-rating">
                                ${[1, 2, 3, 4, 5].map(i => `
                                    <span class="star" data-rating="${i}" onclick="AgentRatingSystem.selectRating(this, ${i})">★</span>
                                `).join('')}
                                <span class="rating-value">Select a rating</span>
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Review</label>
                            <textarea class="form-textarea" placeholder="Share your thoughts about the selected agents..." rows="4"></textarea>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Suggestions for improvement</label>
                            <textarea class="form-textarea" placeholder="How could the analysis be improved?" rows="3"></textarea>
                        </div>
                    </div>
                    
                    <div class="modal-actions">
                        <button class="btn-cancel" onclick="AgentRatingSystem.closeModal(this)">Cancel</button>
                        <button class="btn-next" onclick="AgentRatingSystem.showReviewForm()">Next</button>
                        <button class="btn-submit" onclick="AgentRatingSystem.submitModalReview()" style="display: none;">Submit Review</button>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }
    
    /**
     * Position modal directly below the review button
     */
    positionModalNearButton(modal, reviewButton) {
        const modalContent = modal.querySelector('.review-modal');
        
        // Function to calculate and apply positioning
        const updatePosition = () => {
            const buttonRect = reviewButton.getBoundingClientRect();
            const viewportWidth = window.innerWidth;
            
            // Check if we're on mobile
            const isMobile = viewportWidth < 768;
            
            if (isMobile) {
                // On mobile, position at top with some margin
                modal.style.alignItems = 'flex-start';
                modal.style.justifyContent = 'center';
                modal.style.paddingTop = '2rem';
                modalContent.style.marginTop = '0';
                modalContent.style.position = 'relative';
                modalContent.style.top = 'auto';
                modalContent.style.left = 'auto';
                modalContent.style.transform = 'none';
                return;
            }
            
            // Position modal directly below the button
            modal.style.alignItems = 'flex-start';
            modal.style.justifyContent = 'flex-start';
            
            // Calculate position directly below the button
            const margin = 10; // Small margin between button and modal
            const topPosition = buttonRect.bottom + margin + window.scrollY;
            
            // Get actual modal width (after it's rendered)
            modalContent.style.position = 'absolute';
            modalContent.style.visibility = 'hidden'; // Hide temporarily to measure
            modalContent.style.left = '0px'; // Reset position for measurement
            
            const actualModalWidth = modalContent.offsetWidth;
            
            // Center the modal horizontally relative to the button, then move 20px left
            const buttonCenter = buttonRect.left + (buttonRect.width / 2) + window.scrollX;
            const leftPosition = buttonCenter - (actualModalWidth / 2) - 100;
            
            // Ensure modal doesn't go off-screen horizontally
            const minLeft = 100; // Minimum margin from left edge
            const maxLeft = viewportWidth - actualModalWidth - 20; // Maximum position before right edge
            const finalLeft = Math.max(minLeft, Math.min(leftPosition, maxLeft));
            
            // Apply final positioning
            modalContent.style.top = `${topPosition}px`;
            modalContent.style.left = `${finalLeft}px`;
            modalContent.style.margin = '0';
            modalContent.style.transform = 'none';
            modalContent.style.visibility = 'visible'; // Show again
        };
        
        // Reset overlay positioning
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.right = '0';
        modal.style.bottom = '0';
        
        // Initial positioning
        // Use setTimeout to ensure modal is fully rendered
        setTimeout(updatePosition, 10);
        
        // Add resize listener for responsiveness
        const resizeHandler = () => updatePosition();
        window.addEventListener('resize', resizeHandler);
        
        // Store cleanup function on modal for removal later
        modal._resizeHandler = resizeHandler;
        
        // Add scroll listener to maintain position relative to button
        const scrollHandler = () => updatePosition();
        window.addEventListener('scroll', scrollHandler);
        modal._scrollHandler = scrollHandler;
    }

    /**
     * Close modal and cleanup event listeners
     */
    static closeModal(button) {
        const modal = button.closest('.review-modal-overlay');
        if (modal) {
            // Cleanup event listeners
            if (modal._resizeHandler) {
                window.removeEventListener('resize', modal._resizeHandler);
            }
            if (modal._scrollHandler) {
                window.removeEventListener('scroll', modal._scrollHandler);
            }
            // Remove modal
            modal.remove();
        }
    }

    /**
     * Show review form after agent selection
     */
    static showReviewForm() {
        const selectedAgents = Array.from(document.querySelectorAll('.agent-checkbox:checked'));
        
        if (selectedAgents.length === 0) {
            alert('Please select at least one agent to review.');
            return;
        }
        
        // Show review form
        document.getElementById('reviewForm').style.display = 'block';
        
        // Update buttons
        document.querySelector('.btn-next').style.display = 'none';
        document.querySelector('.btn-submit').style.display = 'inline-block';
        
        // Update form title
        const selectedNames = selectedAgents.map(cb => cb.value).join(', ');
        document.querySelector('.review-modal h2').textContent = `Review: ${selectedNames}`;
    }

    /**
     * Handle star rating selection
     */
    static selectRating(starElement, rating) {
        const modal = starElement.closest('.review-modal-overlay');
        const container = starElement.closest('.review-modal');
        const stars = container.querySelectorAll('.star');
        const ratingValue = container.querySelector('.rating-value');

        // Update visual state
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('filled');
            } else {
                star.classList.remove('filled');
            }
        });

        // Update rating value display
        const ratingText = rating === 1 ? 'Poor' : 
                          rating === 2 ? 'Fair' : 
                          rating === 3 ? 'Good' : 
                          rating === 4 ? 'Very Good' : 'Excellent';
        ratingValue.textContent = `${rating}/5 - ${ratingText}`;

        // Store selected rating on the modal overlay (the element we query later)
        modal.setAttribute('data-selected-rating', rating);

        // Enable submit button
        const submitBtn = container.querySelector('.btn-submit');
        if (submitBtn) {
            submitBtn.disabled = false;
        }
    }

    /**
     * Submit modal review
     */
    static async submitModalReview() {
        const modal = document.getElementById('reviewModal');
        const submitBtn = modal.querySelector('.btn-submit');
        
        // Prevent multiple clicks by disabling button
        if (submitBtn.disabled) {
            return; // Already submitting
        }
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';
        
        const selectedAgents = Array.from(modal.querySelectorAll('.agent-checkbox:checked')).map(cb => cb.value);
        const rating = parseInt(modal.getAttribute('data-selected-rating'));
        const review = modal.querySelector('.form-textarea').value;
        const suggestions = modal.querySelectorAll('.form-textarea')[1]?.value || '';
        
        if (!rating || rating === 0 || isNaN(rating)) {
            alert('Please select a rating');
            // Re-enable button on error
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Review';
            return;
        }

        try {
            // Get current session ID (must be real)
            const sessionId = AgentRatingSystem.getCurrentSessionId();
            
            if (!sessionId) {
                AgentRatingSystem.showErrorMessage(
                    'Cannot Submit Review', 
                    'No analysis session found. Please complete an analysis first before submitting a review.'
                );
                // Re-enable button on error
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Review';
                return;
            }
            
            console.log(`📊 Submitting ratings for session ${sessionId}`);
            
            // Submit individual ratings for each selected agent
            const submissionPromises = selectedAgents.map(async (agentName) => {
                const agentResultId = AgentRatingSystem.getAgentResultId(agentName);
                
                if (!agentResultId) {
                    throw new Error(`No result found for ${agentName}. This agent may not have completed successfully.`);
                }
                
                const ratingData = {
                    session_id: sessionId,
                    agent_result_id: agentResultId,
                    agent_name: agentName,
                    rating: rating,
                    review_text: review || null,
                    helpful_aspects: null, // Could be expanded later
                    improvement_suggestions: suggestions || null,
                    would_recommend: rating >= 4, // 4 or 5 stars = recommend
                    user_id: null
                };

                console.log(`📊 Submitting rating for ${agentName}:`, {
                    session_id: sessionId,
                    agent_result_id: agentResultId,
                    rating: rating
                });
                
                console.log(`📊 Full ratingData being sent:`, ratingData);

                const response = await fetch('/ratings/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(ratingData)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`Failed to submit rating for ${agentName}: ${errorData.detail}`);
                }

                const result = await response.json();
                console.log(`✅ Successfully submitted rating for ${agentName}:`, result);
                return result;
            });

            // Wait for all submissions to complete
            const results = await Promise.all(submissionPromises);
            
            console.log(`✅ All ratings submitted successfully:`, results);
            
            // Get submit button position before removing modal
            const submitBtnRect = submitBtn.getBoundingClientRect();
            
            AgentRatingSystem.showSuccessMessage('Review submitted successfully!', 'Thank you for your feedback!', {
                top: submitBtnRect.top + window.scrollY,
                left: submitBtnRect.left + window.scrollX,
                width: submitBtnRect.width
            });
            modal.remove();
            
        } catch (error) {
            console.error('❌ Error submitting review:', error);
            AgentRatingSystem.showErrorMessage('Failed to submit review', error.message || 'Please try again.');
            // Re-enable button on error
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Review';
        }
    }

    /**
     * Get current session ID from analysis response or URL
     */
    static getCurrentSessionId() {
        // First try to get from window.analysisData (set during analysis)
        if (window.analysisData && window.analysisData.session_id) {
            console.log(`🔍 Found session ID from analysis data: ${window.analysisData.session_id}`);
            return window.analysisData.session_id;
        }
        
        // Try to get session ID from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const sessionId = urlParams.get('session_id');
        
        if (sessionId) {
            console.log(`🔍 Found session ID from URL: ${sessionId}`);
            return parseInt(sessionId);
        }
        
        // Try to get from current analysis session (if available)
        if (window.currentSessionId) {
            console.log(`🔍 Found session ID from window: ${window.currentSessionId}`);
            return window.currentSessionId;
        }
        
        console.warn('⚠️ No real session ID found, analysis may not have been completed');
        return null;
    }

    /**
     * Get agent result ID for a specific agent
     */
    static getAgentResultId(agentName) {
        // Check if we have stored agent result IDs from the analysis
        if (window.agentResultIds && window.agentResultIds[agentName]) {
            console.log(`🔍 Found agent result ID for ${agentName}: ${window.agentResultIds[agentName]}`);
            return window.agentResultIds[agentName];
        }
        
        // Check in analysis data
        if (window.analysisData && window.analysisData[agentName] && window.analysisData[agentName].agent_result_id) {
            console.log(`🔍 Found agent result ID in analysis data for ${agentName}: ${window.analysisData[agentName].agent_result_id}`);
            return window.analysisData[agentName].agent_result_id;
        }
        
        console.warn(`⚠️ No real agent result ID found for ${agentName}`);
        return null;
    }

    /**
     * Show success message popup
     */
    static showSuccessMessage(title, message, position = null) {
        const overlay = document.createElement('div');
        overlay.className = 'success-popup-overlay';
        
        // If position is provided, position at specific location
        if (position) {
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.right = '0';
            overlay.style.bottom = '0';
            overlay.style.display = 'flex';
            overlay.style.alignItems = 'flex-start';
            overlay.style.justifyContent = 'flex-start';
            overlay.style.pointerEvents = 'none'; // Allow clicks through overlay
        }
        
        const popup = document.createElement('div');
        popup.className = 'success-popup';
        
        // If position provided, position the popup at the exact location
        if (position) {
            popup.style.position = 'absolute';
            popup.style.top = `${position.top}px`;
            
            // If width is provided, center horizontally within that width
            if (position.width) {
                const popupWidth = 300; // Approximate popup width
                const centerLeft = position.left + (position.width / 2) - (popupWidth / 2);
                popup.style.left = `${centerLeft}px`;
            } else {
                popup.style.left = `${position.left}px`;
            }
            
            popup.style.pointerEvents = 'auto'; // Allow clicks on popup
        }
        
        popup.innerHTML = `
            <span class="success-popup-icon">✅</span>
            <div class="success-popup-title">${title}</div>
            <div class="success-popup-message">${message}</div>
        `;
        
        overlay.appendChild(popup);
        document.body.appendChild(overlay);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            overlay.remove();
        }, 3000);
        
        // Remove on click
        overlay.addEventListener('click', () => {
            overlay.remove();
        });
    }

    /**
     * Show error message popup
     */
    static showErrorMessage(title, message) {
        const overlay = document.createElement('div');
        overlay.className = 'success-popup-overlay';
        
        const popup = document.createElement('div');
        popup.className = 'success-popup';
        popup.style.background = 'linear-gradient(135deg, #f56565, #e53e3e)';
        popup.innerHTML = `
            <span class="success-popup-icon">❌</span>
            <div class="success-popup-title">${title}</div>
            <div class="success-popup-message">${message}</div>
        `;
        
        overlay.appendChild(popup);
        document.body.appendChild(overlay);
        
        // Auto remove after 4 seconds
        setTimeout(() => {
            overlay.remove();
        }, 4000);
        
        // Remove on click
        overlay.addEventListener('click', () => {
            overlay.remove();
        });
    }
}

// Initialize global instance
document.addEventListener('DOMContentLoaded', () => {
    const ratingSystem = new AgentRatingSystem();
    ratingSystem.initialize();
    
    // Store global reference
    window.AgentRating = window.AgentRating || {};
    window.AgentRating.instance = ratingSystem;
    window.AgentRating.addReviewButton = () => ratingSystem.addReviewButton();
    window.AgentRating.selectRating = AgentRatingSystem.selectRating;
    window.AgentRating.showReviewForm = AgentRatingSystem.showReviewForm;
    window.AgentRating.submitModalReview = AgentRatingSystem.submitModalReview;
});

// Global function to manually add review button (can be called from console or other scripts)
window.addReviewButton = function() {
    if (window.AgentRating && window.AgentRating.addReviewButton) {
        window.AgentRating.addReviewButton();
    }
};

// Function to be called when analysis completes
window.onAnalysisComplete = function() {
    if (window.AgentRating && window.AgentRating.addReviewButton) {
        // Wait a bit for DOM to update
        setTimeout(() => {
            window.AgentRating.addReviewButton();
        }, 500);
    }
}; 