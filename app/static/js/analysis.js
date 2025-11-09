// DOM Elements
const agentOutputs = document.getElementById('agentOutputs');
const analysisForm = document.getElementById('analysisForm');
const startAnalysisBtn = document.getElementById('startAnalysisBtn');
const stopAnalysisBtn = document.getElementById('stopAnalysisBtn');

// Button state management
let isAnalysisRunning = false;
let currentAnalysisController = null;

// Variables for analysis state
let analysisResults = {};
let originalFormData = {};
let analysisCompleted = false;

// Track expanded sections
const expandedSections = new Set();

// Global variables to store analysis data for PDF generation
let currentAnalysisData = {};
let currentSessionId = null;
let userId = 'anonymous'; // In production, get from authentication

// Analysis control functions
function startAnalysis() {
    if (isAnalysisRunning) return;
    
    isAnalysisRunning = true;
    startAnalysisBtn.disabled = true;
    startAnalysisBtn.style.cursor = 'wait';
    startAnalysisBtn.querySelector('span').innerHTML = `
        <svg class="w-5 h-5 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
        Analysis Started...
    `;
    stopAnalysisBtn.style.display = 'block';
    
    // Show progress indicator
    showProgressIndicator();
}

function stopAnalysis() {
    if (!isAnalysisRunning) return;
    
    isAnalysisRunning = false;
    
    // Cancel current analysis if running
    if (currentAnalysisController) {
        currentAnalysisController.abort();
        currentAnalysisController = null;
    }
    
    resetAnalysisButton();
    hideProgressIndicator();
}

// Reset analysis button to ready state
function resetAnalysisButton() {
    isAnalysisRunning = false;
    
    if (startAnalysisBtn) {
        startAnalysisBtn.disabled = false;
        startAnalysisBtn.style.cursor = 'pointer';
        startAnalysisBtn.querySelector('span').innerHTML = `
            <svg class="w-5 h-5 mr-2 group-hover:animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
            Start Analysis
        `;
    }
    
    if (stopAnalysisBtn) {
        stopAnalysisBtn.style.display = 'none';
    }
    
    console.log('Analysis button reset to ready state');
}

// Progress indicator functions
function showProgressIndicator() {
    const existingIndicator = document.getElementById('progressContainer');
    if (existingIndicator) {
        existingIndicator.remove();
    }
    
    const progressContainer = document.createElement('div');
    progressContainer.id = 'progressContainer';
            progressContainer.className = 'fixed top-20 right-4 bg-white rounded-lg shadow-lg p-4 z-40 max-w-sm border border-brand-lapis/20';
    progressContainer.style.opacity = '0';
    progressContainer.style.transform = 'translateX(100px)';
    progressContainer.style.transition = '0.3s';
    
    progressContainer.innerHTML = `
        <div class="flex items-center space-x-3 mb-3">
            <div class="flex-shrink-0">
                <svg class="w-6 h-6 text-brand-lapis animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
            </div>
            <div class="flex-1 min-w-0">
                <p id="progressIndicator" class="text-sm font-medium text-brand-lapis">Starting analysis...</p>
                <p id="progressDetails" class="text-xs text-brand-nickel mt-1">Preparing AI agents</p>
            </div>
            <button onclick="hideProgressIndicator()" class="flex-shrink-0 text-brand-nickel hover:text-brand-oxford transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
        <div class="mb-3">
            <div class="flex justify-between text-xs text-brand-nickel mb-1">
                <span>Overall Progress</span>
                <span id="progressPercentage">0%</span>
            </div>
            <div class="bg-brand-kodama rounded-full h-2">
                <div id="progressBar" class="bg-gradient-to-r from-brand-lapis to-brand-pervenche h-2 rounded-full transition-all duration-300" style="width: 0%" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
        </div>
        <div id="agentProgress" class="space-y-2">
            <div class="text-xs text-brand-nickel font-medium">Agent Status:</div>
            <div id="agentStatusList" class="space-y-1">
                <!-- Agent status items will be added here -->
            </div>
        </div>
    `;
    
    document.body.appendChild(progressContainer);
    
    // Animate in
    setTimeout(() => {
        progressContainer.style.opacity = '1';
        progressContainer.style.transform = 'translateX(0px)';
    }, 100);
}

function hideProgressIndicator() {
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.style.opacity = '0';
        progressContainer.style.transform = 'translateX(100px)';
        setTimeout(() => {
            progressContainer.remove();
        }, 300);
    }
}

function updateProgressDetails(message, details = '') {
    const progressIndicator = document.getElementById('progressIndicator');
    const progressDetails = document.getElementById('progressDetails');
    
    if (progressIndicator) {
        progressIndicator.textContent = message;
    }
    if (progressDetails && details) {
        progressDetails.textContent = details;
    }
}

function updateAgentProgressStatus(agentName, status, progress = 0) {
    const agentStatusList = document.getElementById('agentStatusList');
    if (!agentStatusList) return;
    
    let agentItem = agentStatusList.querySelector(`[data-agent="${agentName}"]`);
    
    if (!agentItem) {
        agentItem = document.createElement('div');
        agentItem.setAttribute('data-agent', agentName);
        agentItem.className = 'flex items-center justify-between text-xs';
        agentStatusList.appendChild(agentItem);
    }
    
    let statusIcon = '⏳';
    let statusText = 'Waiting';
    let statusColor = 'text-brand-nickel';
    
    switch (status) {
        case 'running':
            statusIcon = '🔄';
            statusText = 'Running';
            statusColor = 'text-brand-lapis';
            break;
        case 'completed':
            statusIcon = '✅';
            statusText = 'Completed';
            statusColor = 'text-green-600';
            break;
        case 'error':
            statusIcon = '❌';
            statusText = 'Error';
            statusColor = 'text-red-600';
            break;
    }
    
    agentItem.innerHTML = `
        <span class="font-medium">${statusIcon} ${agentName}</span>
        <span class="${statusColor}">${statusText}</span>
    `;
    
    updateOverallProgress();
}

function updateOverallProgress() {
    const agentStatusList = document.getElementById('agentStatusList');
    if (!agentStatusList) return;
    
    const agentItems = agentStatusList.querySelectorAll('[data-agent]');
    const totalAgents = agentItems.length;
    let completedAgents = 0;
    let runningAgents = 0;
    let waitingAgents = 0;
    
    agentItems.forEach(item => {
        const statusText = item.querySelector('span:last-child').textContent.toLowerCase().trim();
        // Also check for checkmark emoji which indicates completion
        const hasCheckmark = item.innerHTML.includes('✅');
        
        if (statusText === 'completed' || hasCheckmark) {
            completedAgents++;
        } else if (statusText === 'running') {
            runningAgents++;
        } else if (statusText === 'waiting') {
            waitingAgents++;
        }
    });
    
    // Calculate progress: completed agents get 100% credit, running agents get 25% credit
    const progressPercentage = totalAgents > 0 ? 
        Math.round(((completedAgents * 100) + (runningAgents * 25)) / totalAgents) : 0;
    
    // Update progress bar
    const progressBar = document.getElementById('progressBar');
    const progressPercentageElement = document.getElementById('progressPercentage');
    
    if (progressBar) {
        progressBar.style.width = `${progressPercentage}%`;
        progressBar.setAttribute('aria-valuenow', progressPercentage);
    }
    
    if (progressPercentageElement) {
        progressPercentageElement.textContent = `${progressPercentage}%`;
    }
    
    console.log(`Progress Update: ${completedAgents}/${totalAgents} completed (${progressPercentage}%)`);
    
    // Update progress details with more specific information
    if (completedAgents === totalAgents && totalAgents > 0) {
        updateProgressDetails('Analysis completed!', 'All agents finished successfully');
        
        // Reset analysis state and re-enable start button
        isAnalysisRunning = false;
        if (startAnalysisBtn) {
            startAnalysisBtn.disabled = false;
            startAnalysisBtn.style.cursor = 'pointer';
            startAnalysisBtn.querySelector('span').innerHTML = `
                <svg class="w-5 h-5 mr-2 group-hover:animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                Start Analysis
            `;
        }
        
        if (stopAnalysisBtn) {
            stopAnalysisBtn.style.display = 'none';
        }
        
        // Add completion animation to progress container
        const progressContainer = document.getElementById('progressContainer');
        if (progressContainer) {
            progressContainer.style.borderColor = '#10b981';
            progressContainer.style.backgroundColor = '#f0fdf4';
        }
        
        console.log('Analysis completed! Button re-enabled.');
    } else if (runningAgents > 0) {
        updateProgressDetails(`Processing agents...`, `${runningAgents} running, ${waitingAgents} waiting`);
    } else if (waitingAgents > 0) {
        updateProgressDetails('Preparing analysis...', 'Initializing agents');
    }
}

// Toggle agent section collapse/expand
function toggleAgentSection(agentName) {
    const content = document.getElementById(`${agentName}Content`);
    const arrow = document.getElementById(`${agentName}CollapseArrow`);
    
    if (!content || !arrow) return;
    
    const isExpanded = expandedSections.has(agentName);
    
    if (isExpanded) {
        // Collapse
        content.style.maxHeight = '0px';
        arrow.style.transform = 'rotate(0deg)';
        expandedSections.delete(agentName);
    } else {
        // Expand
        content.style.maxHeight = content.scrollHeight + 'px';
        arrow.style.transform = 'rotate(180deg)';
        expandedSections.add(agentName);
        
        // Auto-scroll to the section header after a short delay
        setTimeout(() => {
            const header = content.previousElementSibling;
            if (header) {
                header.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start',
                    inline: 'nearest'
                });
            }
        }, 300);
    }
}

// Auto-expand section when agent completes (if it's the first completion)
function autoExpandOnCompletion(agentName) {
    // Only auto-expand if no sections are currently expanded
    if (expandedSections.size === 0) {
        setTimeout(() => {
            toggleAgentSection(agentName);
        }, 500); // Small delay for visual effect
    }
}

// Recalculate height for expanded sections (useful when content changes)
function recalculateExpandedHeight(agentName) {
    if (expandedSections.has(agentName)) {
        const content = document.getElementById(`${agentName}Content`);
        if (content) {
            content.style.maxHeight = content.scrollHeight + 'px';
        }
    }
}

// Mobile menu toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!mobileMenuButton.contains(event.target) && !mobileMenu.contains(event.target)) {
                mobileMenu.classList.add('hidden');
            }
        });
    }
    
    // Add button event listeners
    if (startAnalysisBtn) {
        startAnalysisBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (!isAnalysisRunning) {
                startAnalysis();
                // Trigger the form submission
                analysisForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    if (stopAnalysisBtn) {
        stopAnalysisBtn.addEventListener('click', function() {
            if (isAnalysisRunning) {
                stopAnalysis();
                // Add any cleanup or cancellation logic here
                showToast('Analysis stopped', 'warning');
            }
        });
    }
    
    // Check for template auto-population
    checkAndPopulateFromTemplate();
    
    // Add download button event listener
    const downloadBtn = document.getElementById('downloadPdfBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadPDF);
    }
    
    // NEW SMART TEMPLATE FEATURES
    // Load AI template suggestions
    loadAITemplateSuggestions();
    
    // Set up template recommendation tracking
    setupTemplateRecommendations();
    
    // Set up save as template functionality
    setupSaveAsTemplate();
    
    // Track user query patterns
    setupQueryPatternTracking();
    
    // Check for existing analysis completion
    checkExistingAnalysisCompletion();
    
    // Check if analysis is already completed (for page refreshes or direct access)
    setTimeout(() => {
        const agentOutputsContainer = document.getElementById('agentOutputs');
        if (agentOutputsContainer && agentOutputsContainer.children.length > 0) {
            console.log('Found existing agent outputs, checking completion status...');
            checkAllAgentsCompleted();
        }
        
        // Also check if progress indicator exists and recalculate
        const progressContainer = document.getElementById('progressContainer');
        if (progressContainer) {
            console.log('Found existing progress container, recalculating...');
            forceRecalculateProgress();
        }
    }, 1000);
    
    // Tab functionality for agent outputs
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('tab-button') || event.target.closest('.tab-button')) {
            const button = event.target.classList.contains('tab-button') ? event.target : event.target.closest('.tab-button');
            const agentName = button.dataset.agent;
            const tabType = button.dataset.tab;
            
            // Update button states
            const allButtons = document.querySelectorAll(`[data-agent="${agentName}"].tab-button`);
            allButtons.forEach(btn => {
                btn.classList.remove('active', 'bg-white', 'shadow-sm', 'text-gray-700');
                btn.classList.add('text-gray-500', 'hover:text-gray-700');
            });
            
            button.classList.add('active', 'bg-white', 'shadow-sm', 'text-gray-700');
            button.classList.remove('text-gray-500', 'hover:text-gray-700');
            
            // Update content visibility
            const allContent = document.querySelectorAll(`[data-agent="${agentName}"].tab-content`);
            allContent.forEach(content => {
                content.classList.add('hidden');
                content.classList.remove('active');
            });
            
            const activeContent = document.querySelector(`[data-content="${tabType}"][data-agent="${agentName}"]`);
            if (activeContent) {
                activeContent.classList.remove('hidden');
                activeContent.classList.add('active');
            }
            
            // Recalculate height if section is expanded
            recalculateExpandedHeight(agentName);
        }
    });
});

// Template auto-population functionality
function checkAndPopulateFromTemplate() {
    // Check URL parameters for template usage
    const urlParams = new URLSearchParams(window.location.search);
    const isFromTemplate = urlParams.get('template') === 'true';
    
    // Check sessionStorage for template data
    const templateData = sessionStorage.getItem('selectedTemplate');
    
    if (isFromTemplate && templateData) {
        try {
            const template = JSON.parse(templateData);
            console.log('Auto-populating form with template:', template.template_name);
            
            // Populate form fields
            populateFormFromTemplate(template);
            
            // Show success message
            showTemplateSelectedMessage(template.template_name);
            
            // Clear the template data and URL parameter
            sessionStorage.removeItem('selectedTemplate');
            
            // Remove template parameter from URL without refreshing
            const newUrl = window.location.pathname;
            window.history.replaceState({}, document.title, newUrl);
            
        } catch (error) {
            console.error('Error parsing template data:', error);
            sessionStorage.removeItem('selectedTemplate');
        }
    }
}

function populateFormFromTemplate(templateData) {
    // Populate strategic question
    const questionField = document.getElementById('strategic_question');
    if (questionField && templateData.strategic_question) {
        questionField.value = templateData.strategic_question;
        questionField.focus();
        questionField.blur(); // Trigger any validation
    }
    
    // Populate time frame
    const timeFrameField = document.getElementById('time_frame');
    if (timeFrameField && templateData.time_frame) {
        // Map template time frame to form options
        const timeFrameMapping = {
            'Short Term (1-2 years)': 'short_term',
            'Next 12 months': 'short_term',
            'Next 6 months': 'short_term',
            'Current and next 6 months': 'short_term',
            'Medium Term (3-5 years)': 'medium_term',
            'Next 12-18 months': 'medium_term',
            'Current and next 3 years': 'medium_term',
            'Long Term (5+ years)': 'long_term',
            'Next 2-5 years': 'long_term',
            'Next 6-18 months': 'medium_term'
        };
        
        const mappedTimeFrame = timeFrameMapping[templateData.time_frame] || 'medium_term';
        timeFrameField.value = mappedTimeFrame;
    }
    
    // Populate region
    const regionField = document.getElementById('region');
    if (regionField && templateData.region) {
        // Map template region to form options
        const regionMapping = {
            'Global': 'global',
            'North America': 'north_america',
            'Europe': 'europe',
            'Asia': 'asia',
            'Africa': 'africa',
            'Latin America': 'latin_america',
            'Regional': 'global', // Default to global for generic "Regional"
            'Target market region': 'global',
            'Organizational scope': 'global',
            'Specified region': 'global'
        };
        
        const mappedRegion = regionMapping[templateData.region] || 'global';
        regionField.value = mappedRegion;
    }
    
    // Populate additional instructions
    const promptField = document.getElementById('prompt');
    if (promptField && templateData.additional_instructions) {
        promptField.value = templateData.additional_instructions;
    }
    
    // Add visual feedback - highlight populated fields briefly
    highlightPopulatedFields();
}

function highlightPopulatedFields() {
    const fields = ['strategic_question', 'time_frame', 'region', 'prompt'];
    
    fields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field && field.value) {
            // Add highlight effect
            field.style.transition = 'all 0.5s ease';
            field.style.boxShadow = '0 0 0 3px rgba(22, 102, 151, 0.3)'; // Lapis Jewel
            field.style.borderColor = '#166697'; // Lapis Jewel
            
            // Remove highlight after animation
            setTimeout(() => {
                field.style.boxShadow = '';
                field.style.borderColor = '';
            }, 2000);
        }
    });
}

function showTemplateSelectedMessage(templateName) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300';
    notification.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <span class="font-medium">Template "${templateName}" applied successfully!</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Animate out and remove
    setTimeout(() => {
        notification.style.transform = 'translateX(full)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Create agent output section
function createAgentOutputSection(agentName) {
    const section = document.createElement('div');
    section.className = 'relative bg-gradient-to-br from-white to-gray-50 rounded-3xl shadow-2xl border border-gray-100 overflow-hidden transform transition-all duration-500 hover:scale-102 hover:shadow-3xl';
    
    // Get agent-specific colors and icons
    const agentConfig = getAgentConfig(agentName);
    
    section.innerHTML = `
        <!-- Background Pattern -->
        <div class="absolute inset-0 opacity-5">
            <div class="absolute top-0 right-0 w-32 h-32 ${agentConfig.bgColor} rounded-full translate-x-16 -translate-y-16"></div>
            <div class="absolute bottom-0 left-0 w-24 h-24 ${agentConfig.accentColor} rounded-full -translate-x-12 translate-y-12"></div>
        </div>
        
        <!-- Collapsible Header Section -->
        <div class="collapsible-header cursor-pointer relative z-10 bg-gradient-to-r ${agentConfig.gradientFrom} ${agentConfig.gradientTo} p-6 border-b border-white/20 hover:opacity-90 transition-opacity duration-200" 
             onclick="toggleAgentSection('${agentName}')">
            <div class="flex items-center justify-between">
                <!-- Agent Title with Icon -->
            <div class="flex items-center">
                    <div class="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center mr-4 shadow-lg">
                        ${agentConfig.icon}
            </div>
                    <div>
                        <h2 class="text-xl font-bold text-white drop-shadow-sm">${agentName}</h2>
                        <p class="text-white/80 text-sm font-medium">${agentConfig.description}</p>
        </div>
                </div>
                
                <!-- Right side with Status and Collapse Arrow -->
                <div class="flex items-center space-x-4">
                    <!-- Status Indicator -->
                    <div id="${agentName}StatusIndicator" class="status-indicator flex items-center bg-white/10 backdrop-blur-sm rounded-full px-4 py-2 border border-white/20">
                        <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        <span class="text-sm text-white font-medium">Processing...</span>
                    </div>
                    
                    <!-- Collapse/Expand Arrow -->
                    <div class="collapse-arrow transition-transform duration-300 transform" id="${agentName}CollapseArrow">
                        <svg class="w-6 h-6 text-white drop-shadow-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                    </div>
                </div>
            </div>
            
        </div>
        
        <!-- Collapsible Content Section -->
        <div class="collapsible-content max-h-0 overflow-hidden transition-all duration-500 ease-in-out" id="${agentName}Content">
            <div class="relative z-10 p-6">
                <!-- Tabs for Content Views -->
                <div class="flex space-x-1 mb-6 bg-gray-100 rounded-xl p-1">
                    <button class="tab-button active flex-1 text-sm font-medium py-2 px-4 rounded-lg transition-all duration-200 bg-white shadow-sm text-gray-700" 
                            data-tab="formatted" data-agent="${agentName}">
                        <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        Formatted
                    </button>
                    <button class="tab-button flex-1 text-sm font-medium py-2 px-4 rounded-lg transition-all duration-200 text-gray-500 hover:text-gray-700" 
                            data-tab="raw" data-agent="${agentName}">
                        <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
                        </svg>
                        Raw Output
                    </button>
                </div>
                
                <!-- Content Container -->
                <div class="content-container">
                    <!-- Formatted Content -->
                    <div class="tab-content active" data-content="formatted" data-agent="${agentName}">
                        <div class="prose max-w-none bg-white/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 shadow-inner min-h-32" id="${agentName}Output">
                            <!-- Loading Animation -->
                            <div class="flex items-center justify-center py-12">
                                <div class="relative">
                                    <div class="w-12 h-12 border-4 border-gray-200 rounded-full"></div>
                                    <div class="absolute top-0 left-0 w-12 h-12 border-4 ${agentConfig.borderColor} border-t-transparent rounded-full animate-spin"></div>
                                </div>
                                <span class="ml-4 text-gray-600 font-medium">Analyzing...</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Raw Content -->
                    <div class="tab-content hidden" data-content="raw" data-agent="${agentName}">
                        <div class="bg-gray-900 rounded-2xl p-6 border border-gray-700 shadow-inner">
                            <pre class="text-green-400 text-sm font-mono overflow-x-auto whitespace-pre-wrap" id="${agentName}RawOutput">
                                <div class="text-gray-500">Raw output will appear here...</div>
                            </pre>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Footer with Timestamp -->
            <div class="relative z-10 px-6 pb-4">
                <div class="flex items-center justify-between text-xs text-gray-500">
                    <span id="${agentName}Timestamp" class="flex items-center">
                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        Started processing...
                    </span>
                    <span id="${agentName}Duration" class="opacity-0">Duration: --</span>
                </div>
            </div>
        </div>
    `;
    
    return section;
}

// Get agent-specific configuration (colors, icons, descriptions)
function getAgentConfig(agentName) {
    const configs = {
        'Problem Explorer': {
            gradientFrom: 'from-brand-lapis',
            gradientTo: 'to-brand-oxford',
            bgColor: 'bg-brand-lapis',
            accentColor: 'bg-brand-pervenche',
            borderColor: 'border-brand-lapis',
            description: 'Breaking down the strategic challenge',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>`
        },
        'Best Practices': {
            gradientFrom: 'from-brand-pervenche',
            gradientTo: 'from-brand-lapis',
            bgColor: 'bg-brand-pervenche',
            accentColor: 'bg-brand-oxford',
            borderColor: 'border-brand-pervenche',
            description: 'Identifying proven solutions and methods',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>
            </svg>`
        },
        'Horizon Scanning': {
            gradientFrom: 'from-brand-oxford',
            gradientTo: 'to-brand-pervenche',
            bgColor: 'bg-brand-oxford',
            accentColor: 'bg-brand-lapis',
            borderColor: 'border-brand-oxford',
            description: 'Scanning for emerging trends and signals',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>`
        },
        'Scenario Planning': {
            gradientFrom: 'from-brand-lapis',
            gradientTo: 'to-brand-pervenche',
            bgColor: 'bg-brand-lapis',
            accentColor: 'bg-brand-oxford',
            borderColor: 'border-brand-nickel',
            description: 'Exploring possible future scenarios',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
            </svg>`
        },
        'Research Synthesis': {
            gradientFrom: 'from-brand-pervenche',
            gradientTo: 'to-brand-oxford',
            bgColor: 'bg-brand-pervenche',
            accentColor: 'bg-brand-lapis',
            borderColor: 'border-brand-lapis',
            description: 'Synthesizing insights and findings',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>`
        },
        'Strategic Action': {
            gradientFrom: 'from-brand-oxford',
            gradientTo: 'to-brand-pervenche',
            bgColor: 'bg-brand-oxford',
            accentColor: 'bg-brand-lapis',
            borderColor: 'border-brand-pervenche',
            description: 'Developing actionable strategies',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>`
        },
        'High Impact': {
            gradientFrom: 'from-brand-pervenche',
            gradientTo: 'to-brand-lapis',
            bgColor: 'bg-brand-pervenche',
            accentColor: 'bg-brand-oxford',
            borderColor: 'border-brand-oxford',
            description: 'Identifying high-impact initiatives',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
            </svg>`
        },
        'Backcasting': {
            gradientFrom: 'from-brand-lapis',
            gradientTo: 'to-brand-oxford',
            bgColor: 'bg-brand-lapis',
            accentColor: 'bg-brand-nickel',
            borderColor: 'border-brand-nickel',
            description: 'Working backwards from desired future',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>`
        }
    };
    
    return configs[agentName] || configs['Problem Explorer']; // Fallback to default
}

// Update section content
function updateSection(sectionId, content) {
    const section = document.querySelector(`[data-section="${sectionId}"]`);
    if (!section) return;

    const loadingIndicator = section.querySelector('.loading-indicator');
    const contentElement = section.querySelector('pre');

    if (loadingIndicator) {
        loadingIndicator.remove();
    }

    if (contentElement) {
        contentElement.textContent = content;
        contentElement.classList.remove('hidden');
    }
}

// Function to check if all agents are completed (fallback detection)
// Function to decode base64 encoded content
function decodeBase64Content(data) {
    if (!data) return data;
    
    try {
        // Handle base64 encoded objects from safe_json_dumps
        if (typeof data === 'object' && data._base64_encoded === true && data.content) {
            const decoded = atob(data.content);
            console.log('Decoded base64 content:', decoded.substring(0, 100) + '...');
            return decoded;
        }
        
        // Handle regular strings that might be base64
        if (typeof data === 'string' && data.length > 100 && /^[A-Za-z0-9+/=]+$/.test(data)) {
            try {
                const decoded = atob(data);
                // Check if decoded content looks like valid text
                if (decoded.includes('#') || decoded.includes('**') || decoded.includes('##')) {
                    console.log('Detected and decoded base64 string content');
                    return decoded;
                }
            } catch (e) {
                // Not base64, return original
            }
        }
        
        return data;
    } catch (error) {
        console.log('Base64 decode error:', error);
        return data;
    }
}

// JSON validation and safe parsing functions
function isValidJSONStructure(str) {
    const trimmed = str.trim();
    return (trimmed.startsWith('{') && trimmed.endsWith('}')) || 
           (trimmed.startsWith('[') && trimmed.endsWith(']'));
}

function safeJSONParse(jsonString) {
    try {
        return { success: true, data: JSON.parse(jsonString) };
    } catch (error) {
        console.log('JSON parse failed:', error.message);
        
        // Try to repair common JSON issues
        let repairedJSON = jsonString;
        
        // 1. Fix unescaped quotes in content (common in Markdown)
        repairedJSON = repairedJSON.replace(/([^\\])"([^"]*[^\\])"([^:])/g, '$1\\"$2\\"$3');
        
        // 2. Fix unescaped newlines in strings
        repairedJSON = repairedJSON.replace(/([^\\])\n/g, '$1\\n');
        
        // 3. Fix unterminated strings by finding last quote position
        const lastQuotePos = repairedJSON.lastIndexOf('"');
        if (lastQuotePos > 0 && !repairedJSON.substring(lastQuotePos + 1).includes('"')) {
            // If we're missing a closing quote, try to add it before the last brace
            const lastBracePos = repairedJSON.lastIndexOf('}');
            if (lastBracePos > lastQuotePos) {
                repairedJSON = repairedJSON.substring(0, lastBracePos) + '"' + repairedJSON.substring(lastBracePos);
            }
        }
        
        // 4. Try parsing the repaired version
        try {
            return { success: true, data: JSON.parse(repairedJSON) };
        } catch (repairError) {
            console.log('JSON repair also failed:', repairError.message);
            
            // Last resort: try to extract the agent name and create a minimal valid structure
            const agentNameMatch = jsonString.match(/["']([^"']*Agent|Problem Explorer|Best Practices|Horizon Scanning|Scenario Planning|Research Synthesis|Strategic Action|High Impact|Backcasting)["']/);
            
            if (agentNameMatch) {
                const agentName = agentNameMatch[1];
                console.log('Creating fallback structure for:', agentName);
                
                return {
                    success: true,
                    data: {
                        [agentName]: {
                            status: "success",
                            data: {
                                formatted_output: "Agent completed successfully but response formatting was corrupted during transmission. The analysis was processed but may not display properly. Please try running the analysis again.",
                                raw_response: "Response parsing failed",
                                note: "This is a fallback response due to JSON parsing errors"
                            }
                        }
                    }
                };
            }
            
            return { success: false, error: repairError.message, originalError: error.message };
        }
    }
}

// Enhanced function to handle all agent output formats
function extractAgentContent(agentData, agentName) {
    if (!agentData) return "No data received";
    
    console.log(`Extracting content for ${agentName}:`, agentData);
    
    // Agent-specific content extraction based on actual formats
    const extractors = {
        'Problem Explorer': (data) => {
            return data.formatted_output || 
                   data.structured_output?.formatted_output ||
                   data.raw_response ||
                   data.analysis;
        },
        
        'Best Practices': (data) => {
            return data.formatted_output ||
                   data.raw_sections?.raw_response ||
                   data.raw_response ||
                   data.analysis;
        },
        
        'Horizon Scanning': (data) => {
            return data.formatted_output ||
                   data.raw_sections?.raw_response ||
                   data.raw_response ||
                   data.analysis;
        },
        
        'Scenario Planning': (data) => {
            return data.formatted_output ||
                   data.raw_sections?.raw_response_text ||
                   data.raw_response_llm ||
                   data.raw_response ||
                   data.analysis;
        },
        
        'Research Synthesis': (data) => {
            return data.formatted_output ||
                   data.structured_synthesis?.formatted_output ||
                   data.raw_response ||
                   data.analysis;
        },
        
        'Strategic Action': (data) => {
            return data.formatted_output ||
                   data.structured_action_plan?.formatted_output ||
                   data.raw_llm_response ||
                   data.raw_response ||
                   data.analysis;
        },
        
        'High Impact': (data) => {
            return data.formatted_output ||
                   data.execution_ready_initiatives ||
                   data.raw_llm_response ||
                   data.raw_response ||
                   data.analysis;
        },
        
        'Backcasting': (data) => {
            return data.formatted_output ||
                   data.prioritized_actions ||
                   data.raw_llm_response ||
                   data.raw_response ||
                   data.analysis;
        }
    };
    
    // Try agent-specific extraction
    const extractor = extractors[agentName];
    if (extractor) {
        const content = extractor(agentData);
        if (content && typeof content === 'string' && content.length > 10) {
            return decodeBase64Content(content);
        }
        
        // If structured data, try to convert to string
        if (content && typeof content === 'object') {
            return JSON.stringify(content, null, 2);
        }
    }
    
    // Fallback: try common field names
    const fallbackFields = [
        'formatted_output', 'analysis', 'response', 'raw_response', 
        'raw_llm_response', 'content', 'output', 'result'
    ];
    
    for (const field of fallbackFields) {
        if (agentData[field] && typeof agentData[field] === 'string' && agentData[field].length > 10) {
            return decodeBase64Content(agentData[field]);
        }
    }
    
    // Last resort: stringify the entire data object
    return JSON.stringify(agentData, null, 2);
}

function checkAllAgentsCompleted() {
    const allAgents = ['strategic', 'market', 'competitor', 'technology', 'regulatory', 'social', 'environmental', 'economic', 'political', 'legal'];
    const allCompleted = allAgents.every(agent => {
        const section = document.getElementById(`${agent}Content`);
        return section && !section.classList.contains('loading');
    });

    if (allCompleted) {
        analysisCompleted = true;
        isAnalysisRunning = false;
        startAnalysisBtn.disabled = false;
        startAnalysisBtn.style.cursor = 'pointer';
        startAnalysisBtn.querySelector('span').innerHTML = `
            <svg class="w-5 h-5 mr-2 group-hover:animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
            Start Analysis
        `;
        stopAnalysisBtn.style.display = 'none';
        showDownloadButton();
        showSuccessMessage('Analysis completed successfully!');
    }
}

// Function to show download button when analysis is complete
function showDownloadButton() {
    const downloadBtn = document.getElementById('downloadPdfBtn');
    if (downloadBtn) {
        console.log('Showing download button');
        downloadBtn.style.display = 'inline-block';
        downloadBtn.classList.add('animate-pulse');
        setTimeout(() => {
            downloadBtn.classList.remove('animate-pulse');
        }, 2000);
    } else {
        console.error('Download button not found in DOM');
    }
}

// Enhanced function to update agent output with completion tracking
function updateAgentOutput(agentName, output) {
    const outputDiv = document.getElementById(`${agentName}Output`);
    const rawOutputDiv = document.getElementById(`${agentName}RawOutput`);
    const timestampSpan = document.getElementById(`${agentName}Timestamp`);
    const durationSpan = document.getElementById(`${agentName}Duration`);
    if (!outputDiv) {
        console.warn(`Output div not found for ${agentName}`);
        return;
    }

    try {
        // Validate output
        if (!output || typeof output !== 'string') {
            console.warn(`Invalid output for ${agentName}:`, output);
            outputDiv.innerHTML = '<p class="text-red-500">Error: Invalid output format</p>';
            return;
        }

        // Log raw output to console
        console.log(`Raw output for ${agentName}:`, output);

        // Pre-process the output to handle single newlines
        let processedOutput = output
            .replace(/\n\n/g, '|||DOUBLE_NEWLINE|||')
            .replace(/\n/g, '  \n')
            .replace(/\|\|\|DOUBLE_NEWLINE\|\|\|/g, '\n\n');

        // Convert markdown to HTML
        const html = marked.parse(processedOutput);
        if (!html) {
            throw new Error('Markdown parsing failed');
        }

        // Update formatted content
        outputDiv.innerHTML = html;

        // Update raw content
        if (rawOutputDiv) {
            rawOutputDiv.innerHTML = `<div class="text-green-400">${output}</div>`;
        }

        // Update progress bar to 100%

        // Update status indicator
        const statusIndicator = document.getElementById(`${agentName}StatusIndicator`);
        if (statusIndicator) {
            statusIndicator.innerHTML = `
                <div class="w-4 h-4 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                <span class="text-sm text-white font-medium">Completed</span>
            `;
        }

        // Update agent progress status in the progress indicator
        updateAgentProgressStatus(agentName, 'completed', 100);

        // Update timestamp
        if (timestampSpan) {
            const now = new Date();
            timestampSpan.innerHTML = `
                <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Completed at ${now.toLocaleTimeString()}
            `;
        }

        // Show duration (placeholder - you could track actual start time)
        if (durationSpan) {
            durationSpan.classList.remove('opacity-0');
            durationSpan.innerHTML = 'Duration: ~30s'; // Placeholder
        }

        // Add completion animation
        const section = outputDiv.closest('.relative.bg-gradient-to-br');
        if (section) {
            section.classList.add('animate-pulse');
            setTimeout(() => {
                section.classList.remove('animate-pulse');
            }, 1000);
        }

        // Auto-expand this section if it's the first to complete
        autoExpandOnCompletion(agentName);

        // Recalculate height if this section is expanded
        recalculateExpandedHeight(agentName);

        // After updating the output, check if all agents are completed
        setTimeout(() => {
            checkAllAgentsCompleted();
        }, 1000); // Small delay to allow UI updates

    } catch (error) {
        console.error(`Error updating output for ${agentName}:`, error);
        
        // Update with error state
        outputDiv.innerHTML = `
            <div class="text-red-500 bg-red-50 rounded-lg p-4 border border-red-200">
                <div class="flex items-center mb-2">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                    </svg>
                    <strong class="font-semibold">Error displaying output</strong>
                </div>
                <pre class="text-sm bg-white rounded p-2 mt-2 overflow-x-auto">${output || 'No output available'}</pre>
            </div>
        `;
        
        // Update status to error
        const statusIndicator = document.getElementById(`${agentName}StatusIndicator`);
        if (statusIndicator) {
            statusIndicator.innerHTML = `
                <div class="w-4 h-4 bg-red-400 rounded-full mr-2"></div>
                <span class="text-sm text-white font-medium">Error</span>
            `;
        }

        // Still check completion even on error
        setTimeout(() => {
            checkAllAgentsCompleted();
        }, 1000);
    }
}

// Remove loading state
function removeLoadingState(agentName) {
    const outputDiv = document.getElementById(`${agentName}Output`);
    if (!outputDiv) {
        console.warn(`Output div not found for ${agentName}`);
        return;
    }

    const section = outputDiv.parentElement;
    if (!section) {
        console.warn(`Section not found for ${agentName}`);
        return;
    }

    const loadingDiv = section.querySelector('.flex.items-center');
    if (loadingDiv) {
        loadingDiv.innerHTML = `
            <span class="text-sm text-green-600">Completed</span>
        `;
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4';
    errorDiv.innerHTML = `
        <strong class="font-bold">Error!</strong>
        <span class="block sm:inline">${message}</span>
    `;
    agentOutputs.insertBefore(errorDiv, agentOutputs.firstChild);
}

// Form submission handler
analysisForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Reset analysis state
    analysisResults = {};
    analysisCompleted = false;
    
    // Hide download button
    const downloadBtn = document.getElementById('downloadPdfBtn');
    if (downloadBtn) {
        downloadBtn.style.display = 'none';
    }
    
    // Clear previous outputs
    agentOutputs.innerHTML = '';
    
    // Get form data
    const formData = new FormData(e.target);
    const inputData = {
        strategic_question: formData.get('strategic_question'),
        time_frame: formData.get('time_frame'),
        region: formData.get('region'),
        prompt: formData.get('prompt') || undefined
    };
    
    // Store original form data for PDF generation
    originalFormData = { ...inputData };
    
    try {
        // Start analysis
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(inputData)
        });
        
        if (!response.ok) {
            throw new Error(`Analysis failed: ${response.statusText}`);
        }
        
        // Create sections for each agent
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
        
        agents.forEach(agent => {
            const section = createAgentOutputSection(agent);
            agentOutputs.appendChild(section);
            // Initialize agent in progress tracker
            updateAgentProgressStatus(agent, 'waiting', 0);
        });
        
        // Auto-scroll to the analysis results section
        agentOutputs.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
        
        // Track completed agents
        let completedAgents = 0;
        const totalAgents = agents.length;
        
        // Process the response stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';  // Buffer to handle incomplete JSON across chunks
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            buffer += chunk;
            
            // Split by newlines but keep incomplete lines in buffer
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';  // Keep the last (potentially incomplete) line in buffer
            
            for (const line of lines) {
                if (!line.trim()) continue;
                
                // Validate JSON structure before parsing
                if (!isValidJSONStructure(line)) {
                    console.warn('Skipping non-JSON line:', line.substring(0, 100) + '...');
                    continue;
                }
                
                // Use safe JSON parsing
                const parseResult = safeJSONParse(line);
                
                if (!parseResult.success) {
                    console.error('Failed to parse JSON after all repair attempts:', parseResult.error);
                    console.log('Original error:', parseResult.originalError);
                    console.log('Problematic line (first 200 chars):', line.substring(0, 200));
                    
                    // Try to extract agent name and provide feedback
                    const agentNames = ['Problem Explorer', 'Best Practices', 'Horizon Scanning', 'Scenario Planning', 
                                      'Research Synthesis', 'Strategic Action', 'High Impact', 'Backcasting'];
                    
                    let identifiedAgent = null;
                    for (const agentName of agentNames) {
                        if (line.includes(`"${agentName}"`) || line.includes(agentName)) {
                            identifiedAgent = agentName;
                            break;
                        }
                    }
                    
                    if (identifiedAgent) {
                        const outputDiv = document.getElementById(`${identifiedAgent}Output`);
                        if (outputDiv) {
                            updateAgentOutput(identifiedAgent, `<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                                <div class="flex items-center mb-2">
                                    <svg class="w-5 h-5 mr-2 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                                    </svg>
                                    <strong class="font-semibold text-yellow-800">Response Formatting Issue</strong>
                                </div>
                                <p class="text-sm text-yellow-700">
                                    ${identifiedAgent} completed its analysis, but the response format was corrupted during transmission. 
                                    This is usually due to special characters in the content. Please try running the analysis again.
                                </p>
                                <details class="mt-2">
                                    <summary class="text-xs text-yellow-600 cursor-pointer">Technical Details</summary>
                                    <pre class="text-xs text-yellow-600 mt-1 overflow-x-auto">${parseResult.error}</pre>
                                </details>
                            </div>`);
                            removeLoadingState(identifiedAgent);
                            completedAgents++;
                        }
                    }
                    continue;
                }
                
                const data = parseResult.data;
                console.log('Received data:', data);
                
                // Check for session info
                if (data.session_info) {
                    console.log('Session info received:', data.session_info);
                    // Store session ID in global variables for ratings system
                    if (data.session_info.session_id) {
                        currentSessionId = data.session_info.session_id;
                        window.currentSessionId = data.session_info.session_id;
                        
                        // Initialize analysis data structure if it doesn't exist
                        if (!window.analysisData) {
                            window.analysisData = {};
                        }
                        window.analysisData.session_id = data.session_info.session_id;
                        
                        console.log(`📊 Stored session ID for ratings: ${data.session_info.session_id}`);
                    }
                    continue;
                }
                
                // Get the first key from the data object (agent name)
                const agentName = Object.keys(data)[0];
                if (!agentName) {
                    console.warn('No agent name found in data');
                    continue;
                }
                
                console.log('Processing agent:', agentName, 'with data:', data[agentName]);
                const outputDiv = document.getElementById(`${agentName}Output`);
                if (outputDiv) {
                    const agentData = data[agentName];
                    
                    // Handle error responses
                    if (typeof agentData === 'string' && agentData.startsWith('Error:')) {
                        console.error(`Agent ${agentName} failed:`, agentData);
                        updateAgentOutput(agentName, `<div class="text-red-500 bg-red-50 rounded-lg p-4 border border-red-200">
                            <div class="flex items-center mb-2">
                                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                                </svg>
                                <strong class="font-semibold">Agent Processing Failed</strong>
                            </div>
                            <p class="text-sm">${agentData}</p>
                        </div>`);
                        removeLoadingState(agentName);
                        completedAgents++;
                        continue;
                    }
                    
                    // Handle structured error responses
                    if (agentData && agentData.status === 'error') {
                        console.error(`Agent ${agentName} error:`, agentData.error);
                        updateAgentOutput(agentName, `<div class="text-red-500 bg-red-50 rounded-lg p-4 border border-red-200">
                            <div class="flex items-center mb-2">
                                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                                </svg>
                                <strong class="font-semibold">Processing Failed</strong>
                            </div>
                            <p class="text-sm"><strong>Error:</strong> ${agentData.error || 'Unknown error occurred'}</p>
                            </div>`);
                        removeLoadingState(agentName);
                        completedAgents++;
                        continue;
                    }
                    
                    // Handle successful responses - both with and without nested data
                    if (agentData && (agentData.status === 'success' || agentData.data || agentData.formatted_output)) {
                        console.log(`Agent ${agentName} completed successfully`);
                        
                        // Store analysis result
                        const agentKey = agentName.toLowerCase().replace(/\s+/g, '_');
                        analysisResults[agentKey] = agentData;
                        
                        // Store agent result ID and session ID for ratings system
                        if (agentData && typeof agentData === 'object') {
                            // Initialize storage objects if they don't exist
                            if (!window.agentResultIds) {
                                window.agentResultIds = {};
                            }
                            if (!window.analysisData) {
                                window.analysisData = {};
                            }
                            
                            // Store agent result ID if present
                            if (agentData.agent_result_id) {
                                window.agentResultIds[agentName] = agentData.agent_result_id;
                                console.log(`📊 Stored agent result ID for ${agentName}: ${agentData.agent_result_id}`);
                            }
                            
                            // Store session ID if present
                            if (agentData.session_id) {
                                currentSessionId = agentData.session_id;
                                window.currentSessionId = agentData.session_id;
                                window.analysisData.session_id = agentData.session_id;
                                console.log(`📊 Stored session ID from ${agentName}: ${agentData.session_id}`);
                            }
                            
                            // Store the complete agent data for ratings
                            window.analysisData[agentName] = agentData;
                        }
                        
                        // Extract content using the comprehensive extractor
                        let content;
                        
                        // Update agent status to running when we start processing
                        updateAgentProgressStatus(agentName, 'running', 50);
                        
                        // If there's nested data, extract from it
                        if (agentData.data) {
                            content = extractAgentContent(agentData.data, agentName);
                        } else {
                            // Extract directly from agent data
                            content = extractAgentContent(agentData, agentName);
                        }
                        
                        // Validate content
                        if (!content || (typeof content === 'string' && content.length < 10)) {
                            content = "Agent completed successfully but no formatted output was generated.";
                        }
                        
                        console.log(`Agent ${agentName} content to display:`, content.toString().substring(0, 200) + '...');
                        
                        updateAgentOutput(agentName, content);
                        removeLoadingState(agentName);
                        completedAgents++;
                        
                    } else {
                        // Fallback handling for unexpected data formats
                        console.warn(`Unexpected data format for agent: ${agentName}`, agentData);
                        
                        const agentKey = agentName.toLowerCase().replace(/\s+/g, '_');
                        analysisResults[agentKey] = agentData;
                        
                        const content = extractAgentContent(agentData, agentName);
                        updateAgentOutput(agentName, content);
                        removeLoadingState(agentName);
                        completedAgents++;
                    }
                    
                    // Check if all agents are completed
                    console.log(`Completion check: ${completedAgents}/${totalAgents} agents completed`);
                    if (completedAgents >= totalAgents) {
                        analysisCompleted = true;
                        console.log('All agents completed - showing download button');
                        showDownloadButton();
                        
                        const saveBtn = document.getElementById('saveAsTemplateBtn');
                        if (saveBtn) {
                            saveBtn.style.display = 'inline-flex';
                        }
                        
                        // Trigger analysis completion for rating system
                        setTimeout(() => {
                            console.log('📊 Triggering analysis completion callbacks');
                            if (window.onAnalysisComplete) {
                                window.onAnalysisComplete();
                            }
                            if (window.addReviewButton) {
                                window.addReviewButton();
                            }
                            
                            // Dispatch custom event for rating system
                            const analysisCompletedEvent = new CustomEvent('analysisCompleted', {
                                detail: {
                                    sessionId: window.currentSessionId || currentSessionId,
                                    agentResultIds: window.agentResultIds,
                                    analysisData: window.analysisData
                                }
                            });
                            document.dispatchEvent(analysisCompletedEvent);
                            console.log('📊 Dispatched analysisCompleted event');
                        }, 1000);
                    }
                } else {
                    console.warn(`Output div not found for agent: ${agentName}`);
                }
            }
        }
        
        // Process any remaining data in buffer
        if (buffer.trim()) {
            console.log('Processing remaining buffer data:', buffer.substring(0, 100) + '...');
            
            if (isValidJSONStructure(buffer)) {
                const parseResult = safeJSONParse(buffer);
                
                if (parseResult.success) {
                    const data = parseResult.data;
                    const agentName = Object.keys(data)[0];
                    if (agentName && ['Problem Explorer', 'Best Practices', 'Horizon Scanning', 'Scenario Planning', 
                                     'Research Synthesis', 'Strategic Action', 'High Impact', 'Backcasting'].includes(agentName)) {
                        
                        console.log('Processing buffered agent:', agentName);
                        const outputDiv = document.getElementById(`${agentName}Output`);
                        if (outputDiv) {
                            const agentData = data[agentName];
                            if (agentData && (agentData.status === 'success' || agentData.data || agentData.formatted_output)) {
                                const agentKey = agentName.toLowerCase().replace(/\s+/g, '_');
                                analysisResults[agentKey] = agentData;
                                
                                const content = agentData.data ? 
                                              extractAgentContent(agentData.data, agentName) : 
                                              extractAgentContent(agentData, agentName);
                                
                                updateAgentOutput(agentName, content);
                                removeLoadingState(agentName);
                                completedAgents++;
                                
                                console.log(`Buffer completion check: ${completedAgents}/${totalAgents} agents completed`);
                                if (completedAgents >= totalAgents) {
                                    analysisCompleted = true;
                                    showDownloadButton();
                                    
                                    const saveBtn = document.getElementById('saveAsTemplateBtn');
                                    if (saveBtn) {
                                        saveBtn.style.display = 'inline-flex';
                                    }
                                }
                            }
                        }
                    }
                } else {
                    console.log('Failed to parse buffer data:', parseResult.error);
                }
            } else {
                console.log('Buffer does not contain valid JSON structure, skipping');
            }
        }
    } catch (error) {
        console.error('Analysis error:', error);
        
        // Handle specific network errors
        if (error.message.includes('network error') || error.message.includes('QUIC_PROTOCOL_ERROR')) {
            console.log('Network error detected, attempting graceful recovery...');
            
            // Check if we have partial results to display
            if (completedAgents > 0) {
                console.log(`Partial analysis completed: ${completedAgents}/${totalAgents} agents finished`);
                
                // Show what we have
                if (completedAgents >= totalAgents * 0.5) { // If at least 50% completed
                    showDownloadButton();
                    showError('Network connection was interrupted, but partial analysis results are available for download.');
                } else {
                    showError('Network connection was interrupted. Please try running the analysis again.');
                }
            } else {
                showError('Network connection failed. Please check your internet connection and try again.');
            }
        } else {
            showError(error.message);
        }
    }
});

// Function to download PDF report
async function downloadPDF() {
    const downloadBtn = document.getElementById('downloadPdfBtn');
    
    if (!downloadBtn) {
        console.error('Download button not found');
        return;
    }
    
    // Collect analysis data from the UI if not stored in memory
    if (!analysisCompleted || Object.keys(analysisResults).length === 0) {
        console.log('Analysis data not in memory, attempting to collect from UI...');
        collectAnalysisDataFromUI();
    }
    
    if (Object.keys(analysisResults).length === 0 && !collectFormDataFromUI()) {
        alert('Please complete an analysis first before downloading the PDF report.');
        return;
    }
    
    try {
        // Store original button content
        const originalContent = downloadBtn.innerHTML;
        
        // Show loading state
        downloadBtn.innerHTML = `
            <span class="flex items-center">
                <svg class="w-5 h-5 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                Generating PDF...
            </span>
        `;
        downloadBtn.disabled = true;
        downloadBtn.classList.add('opacity-75', 'cursor-not-allowed');
        downloadBtn.classList.remove('hover:scale-105', 'hover:shadow-2xl');
        
        // Collect form data
        const formData = collectFormDataFromUI();
        
        // Prepare the request data
        const pdfRequest = {
            analysis_data: analysisResults,
            strategic_question: formData.strategic_question || originalFormData.strategic_question || 'Strategic Analysis',
            time_frame: formData.time_frame || originalFormData.time_frame || 'medium_term',
            region: formData.region || originalFormData.region || 'global'
        };
        
        console.log('📊 PDF Request Summary:');
        console.log('- Analysis data keys:', Object.keys(pdfRequest.analysis_data));
        console.log('- Strategic question:', pdfRequest.strategic_question);
        console.log('- Time frame:', pdfRequest.time_frame);
        console.log('- Region:', pdfRequest.region);
        console.log('🔍 Full PDF request data:', pdfRequest);
        
        // Validate that we have some analysis data
        if (Object.keys(pdfRequest.analysis_data).length === 0) {
            throw new Error('No analysis data available. Please complete an analysis first.');
        }
        
        // Make the request
        const response = await fetch('/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(pdfRequest)
        });
        
        console.log('📡 Response status:', response.status);
        console.log('📡 Response headers:', response.headers);
        
        if (!response.ok) {
            // Try to get error details from the response
            let errorMessage = `PDF generation failed: ${response.status} ${response.statusText}`;
            try {
                const errorData = await response.text();
                console.error('❌ Server error response:', errorData);
                errorMessage += ` - ${errorData}`;
            } catch (e) {
                console.error('❌ Could not parse error response');
            }
            throw new Error(errorMessage);
        }
        
        // Get the PDF blob
        const blob = await response.blob();
        console.log('📄 PDF blob size:', blob.size);
        
        if (blob.size === 0) {
            throw new Error('Received empty PDF file');
        }
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `strategic_analysis_${new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // Show success message
        showSuccessMessage('PDF report downloaded successfully! You can download it again anytime.');
        
    } catch (error) {
        console.error('❌ Error downloading PDF:', error);
        showErrorMessage(`Failed to download PDF: ${error.message}`);
    } finally {
        // Always restore button state
        const originalContent = `
            <span class="flex items-center">
                <svg class="w-5 h-5 mr-2 group-hover:animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                Download PDF Report
            </span>
            <div class="absolute inset-0 bg-white/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        `;
        
        downloadBtn.innerHTML = originalContent;
        downloadBtn.disabled = false;
        downloadBtn.classList.remove('opacity-75', 'cursor-not-allowed');
        downloadBtn.classList.add('hover:scale-105', 'hover:shadow-2xl');
    }
}

// Function to show error message
function showErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-6 py-3 rounded-lg shadow-lg z-50 transition-all duration-300';
    errorDiv.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
            <span class="font-medium">${message}</span>
        </div>
    `;
    
    document.body.appendChild(errorDiv);
    
    // Auto-remove after 7 seconds
    setTimeout(() => {
        errorDiv.style.opacity = '0';
        errorDiv.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (document.body.contains(errorDiv)) {
                document.body.removeChild(errorDiv);
            }
        }, 300);
    }, 7000);
}

// Function to collect analysis data from UI elements
function collectAnalysisDataFromUI() {
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
    
    console.log('Collecting analysis data from UI...');
    
    agents.forEach(agentName => {
        const outputDiv = document.getElementById(`${agentName}Output`);
        if (outputDiv && outputDiv.innerHTML.trim() !== '') {
            // Fix the agent key mapping to match backend expectations
            const agentKey = agentName.toLowerCase().replace(/\s+/g, '_');
            
            // Get HTML content and convert to markdown-style formatting
            const htmlContent = outputDiv.innerHTML;
            const markdownContent = convertHtmlToMarkdown(htmlContent);
            
            if (markdownContent && markdownContent.length > 50) {
                analysisResults[agentKey] = {
                    data: {
                        formatted_output: markdownContent,
                        raw_response: outputDiv.textContent || outputDiv.innerText || ''
                    }
                };
                console.log(`Collected formatted data for ${agentName} (key: ${agentKey}): ${markdownContent.substring(0, 100)}...`);
            }
        }
    });
    
    console.log('Collected analysis results:', Object.keys(analysisResults));
    console.log('Total agents collected:', Object.keys(analysisResults).length);
}

// Function to convert HTML content to markdown-style formatting
function convertHtmlToMarkdown(html) {
    if (!html) return '';
    
    // Create a temporary div to work with the HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    
    // Convert HTML elements to markdown-style formatting
    let markdown = '';
    
    function processNode(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            return node.textContent;
        }
        
        if (node.nodeType === Node.ELEMENT_NODE) {
            const tagName = node.tagName.toLowerCase();
            let content = '';
            
            // Process child nodes
            for (let child of node.childNodes) {
                content += processNode(child);
            }
            
            // Convert based on tag type
            switch (tagName) {
                case 'h1':
                    return `# ${content.trim()}\n\n`;
                case 'h2':
                    return `## ${content.trim()}\n\n`;
                case 'h3':
                    return `### ${content.trim()}\n\n`;
                case 'h4':
                    return `#### ${content.trim()}\n\n`;
                case 'h5':
                    return `##### ${content.trim()}\n\n`;
                case 'h6':
                    return `###### ${content.trim()}\n\n`;
                case 'p':
                    return `${content.trim()}\n\n`;
                case 'strong':
                case 'b':
                    return `**${content.trim()}**`;
                case 'em':
                case 'i':
                    return `*${content.trim()}*`;
                case 'li':
                    return `- ${content.trim()}\n`;
                case 'ul':
                case 'ol':
                    return `${content}\n`;
                case 'br':
                    return '\n';
                case 'hr':
                    return '\n---\n\n';
                case 'blockquote':
                    return `> ${content.trim()}\n\n`;
                case 'code':
                    return `\`${content}\``;
                case 'pre':
                    return `\`\`\`\n${content}\n\`\`\`\n\n`;
                default:
                    return content;
            }
        }
        
        return '';
    }
    
    markdown = processNode(tempDiv);
    
    // Clean up excessive newlines
    markdown = markdown.replace(/\n{3,}/g, '\n\n');
    
    // Fix any double ** issues
    markdown = markdown.replace(/\*\*\*\*/g, '**');
    
    // Handle numbered lists more carefully
    const lines = markdown.split('\n');
    let processedLines = [];
    let inOrderedList = false;
    let listCounter = 1;
    
    for (let line of lines) {
        line = line.trim();
        
        // Check if this line looks like it should be a numbered item
        if (line.match(/^\d+\.\s+/) || (inOrderedList && line.startsWith('- ') && line.length > 10)) {
            if (line.startsWith('- ')) {
                // Convert bullet to numbered
                processedLines.push(`${listCounter}. ${line.substring(2)}`);
                listCounter++;
            } else {
                // Already numbered
                processedLines.push(line);
                const match = line.match(/^(\d+)\./);
                if (match) {
                    listCounter = parseInt(match[1]) + 1;
                }
            }
            inOrderedList = true;
        } else if (line === '') {
            processedLines.push(line);
            if (inOrderedList) {
                inOrderedList = false;
                listCounter = 1;
            }
        } else {
            processedLines.push(line);
            inOrderedList = false;
            listCounter = 1;
        }
    }
    
    return processedLines.join('\n').trim();
}

// Function to collect form data from UI
function collectFormDataFromUI() {
    const strategicQuestion = document.getElementById('strategic_question').value;
    const timeFrame = document.getElementById('time_frame').value;
    const region = document.getElementById('region').value;
    const prompt = document.getElementById('prompt').value;
    
    // Collect new customization parameters
    const analysisDepth = document.getElementById('analysis_depth')?.value || 'standard';
    const creativityLevel = document.getElementById('creativity_level')?.value || 'balanced';
    const focusAreas = document.getElementById('focus_areas')?.value || 'general';
    
    return {
        strategic_question: strategicQuestion,
        time_frame: timeFrame,
        region: region,
        prompt: prompt,
        analysis_depth: analysisDepth,
        creativity_level: creativityLevel,
        focus_areas: focusAreas
    };
}

// Function to show success message
function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-6 py-3 rounded-lg shadow-lg z-50 transition-all duration-300';
    successDiv.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <span class="font-medium">${message}</span>
        </div>
    `;
    
    document.body.appendChild(successDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        successDiv.style.opacity = '0';
        successDiv.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (document.body.contains(successDiv)) {
                document.body.removeChild(successDiv);
            }
        }, 300);
    }, 5000);
}

// 🤖 AI TEMPLATE SUGGESTIONS
async function loadAITemplateSuggestions() {
    try {
        const response = await fetch(`/api/ai-template-suggestions/${userId}?limit=3`);
        const data = await response.json();
        
        if (data.success && data.suggestions.length > 0) {
            displayAISuggestions(data.suggestions);
        } else {
            displayNoSuggestions();
        }
    } catch (error) {
        console.error('Error loading AI suggestions:', error);
        displayNoSuggestions();
    }
}

function displayAISuggestions(suggestions) {
    const suggestionsList = document.getElementById('aiSuggestionsList');
    if (!suggestionsList) return;
    
    suggestionsList.innerHTML = '';
    
    suggestions.forEach((suggestion, index) => {
        const suggestionElement = document.createElement('div');
        suggestionElement.className = 'suggestion-card bg-white rounded-xl p-4 border border-purple-200 hover:border-purple-400 cursor-pointer transition-all duration-200 transform hover:scale-105';
        suggestionElement.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex-1">
                    <h4 class="font-semibold text-gray-800 mb-1">${suggestion.name}</h4>
                    <p class="text-sm text-gray-600 mb-2">${suggestion.category}</p>
                    <p class="text-xs text-brand-nickel italic font-brand-regular">${suggestion.reason}</p>
                </div>
                <div class="ml-4">
                    <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                        <span class="text-brand-lapis font-brand-black text-sm">${Math.round(suggestion.confidence * 100)}%</span>
                    </div>
                </div>
            </div>
        `;
        
        suggestionElement.addEventListener('click', () => applySuggestionAsTemplate(suggestion));
        suggestionsList.appendChild(suggestionElement);
    });
}

function displayNoSuggestions() {
    const suggestionsList = document.getElementById('aiSuggestionsList');
    if (!suggestionsList) return;
    
    suggestionsList.innerHTML = `
        <div class="text-center py-4 text-gray-500">
            <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
            <p>Start using the app to get personalized AI suggestions!</p>
        </div>
    `;
}

// 📋 TEMPLATE RECOMMENDATIONS
function setupTemplateRecommendations() {
    const strategicQuestionInput = document.getElementById('strategic_question');
    if (!strategicQuestionInput) return;
    
    let debounceTimer;
    
    strategicQuestionInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            if (this.value.length > 20) {
                getTemplateRecommendations(this.value);
            } else {
                hideTemplateRecommendations();
            }
        }, 1000); // Wait 1 second after user stops typing
    });
}

async function getTemplateRecommendations(strategicQuestion) {
    try {
        const response = await fetch('/api/get-template-recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                strategic_question: strategicQuestion,
                user_id: userId
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.recommendations.length > 0) {
            displayTemplateRecommendations(data.recommendations);
        } else {
            hideTemplateRecommendations();
        }
    } catch (error) {
        console.error('Error getting template recommendations:', error);
        hideTemplateRecommendations();
    }
}

function displayTemplateRecommendations(recommendations) {
    const recommendationsSection = document.getElementById('templateRecommendations');
    const recommendationsList = document.getElementById('recommendationsList');
    
    if (!recommendationsSection || !recommendationsList) return;
    
    recommendationsList.innerHTML = '';
    
    recommendations.slice(0, 3).forEach(template => {
        const templateElement = document.createElement('div');
        templateElement.className = 'template-recommendation bg-white rounded-xl p-4 border border-blue-200 hover:border-blue-400 cursor-pointer transition-all duration-200 transform hover:scale-105';
        templateElement.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex-1">
                    <h4 class="font-semibold text-gray-800 mb-1">${template.name}</h4>
                    <p class="text-sm text-gray-600 mb-2">${template.category}</p>
                    <p class="text-xs text-blue-600">${template.description}</p>
                </div>
                <div class="ml-4">
                    <div class="text-blue-600 font-semibold text-sm">
                        ${template.usage_count} uses
                    </div>
                </div>
            </div>
        `;
        
        templateElement.addEventListener('click', () => applyTemplateRecommendation(template));
        recommendationsList.appendChild(templateElement);
    });
    
    recommendationsSection.style.display = 'block';
}

function hideTemplateRecommendations() {
    const recommendationsSection = document.getElementById('templateRecommendations');
    if (recommendationsSection) {
        recommendationsSection.style.display = 'none';
    }
}

function applyTemplateRecommendation(template) {
    // Apply template to form
    const strategicQuestionField = document.getElementById('strategic_question');
    const timeFrameField = document.getElementById('time_frame');
    const regionField = document.getElementById('region');
    const promptField = document.getElementById('prompt');
    
    if (strategicQuestionField) strategicQuestionField.value = template.strategic_question;
    if (timeFrameField) timeFrameField.value = template.default_time_frame || '';
    if (regionField) regionField.value = template.default_region || '';
    if (promptField) promptField.value = template.additional_instructions || '';
    
    // Show success message
    showToast(`Applied template: ${template.name}`, 'success');
    
    // Hide recommendations
    hideTemplateRecommendations();
}

// 💾 SAVE AS TEMPLATE FUNCTIONALITY
function setupSaveAsTemplate() {
    const saveAsTemplateBtn = document.getElementById('saveAsTemplateBtn');
    const saveTemplateModal = document.getElementById('saveTemplateModal');
    const saveTemplateForm = document.getElementById('saveTemplateForm');
    const cancelBtn = document.getElementById('cancelSaveTemplate');
    
    if (!saveAsTemplateBtn || !saveTemplateModal || !saveTemplateForm || !cancelBtn) return;
    
    saveAsTemplateBtn.addEventListener('click', showSaveTemplateModal);
    cancelBtn.addEventListener('click', hideSaveTemplateModal);
    saveTemplateForm.addEventListener('submit', handleSaveAsTemplate);
    
    // Close modal when clicking outside
    saveTemplateModal.addEventListener('click', function(e) {
        if (e.target === saveTemplateModal) {
            hideSaveTemplateModal();
        }
    });
}

function showSaveTemplateModal() {
    const modal = document.getElementById('saveTemplateModal');
    if (!modal) return;
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    // Animate modal appearance
    setTimeout(() => {
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.transform = 'scale(1)';
        }
    }, 10);
}

function hideSaveTemplateModal() {
    const modal = document.getElementById('saveTemplateModal');
    if (!modal) return;
    
    const modalContent = modal.querySelector('.modal-content');
    if (modalContent) {
        modalContent.style.transform = 'scale(0.95)';
    }
    
    setTimeout(() => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        
        // Clear form
        const form = document.getElementById('saveTemplateForm');
        if (form) form.reset();
    }, 200);
}

async function handleSaveAsTemplate(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const templateData = {
        session_id: currentSessionId,
        template_name: formData.get('templateName'),
        template_description: formData.get('templateDescription'),
        category: formData.get('templateCategory'),
        user_id: userId
    };
    
    if (!currentSessionId) {
        showToast('No analysis session found. Please complete an analysis first.', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/save-analysis-as-template', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(templateData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message, 'success');
            hideSaveTemplateModal();
            
            // Refresh AI suggestions to include new template
            setTimeout(() => {
                loadAITemplateSuggestions();
            }, 1000);
        } else {
            showToast(data.error || 'Failed to save template', 'error');
        }
    } catch (error) {
        console.error('Error saving template:', error);
        showToast('Error saving template. Please try again.', 'error');
    }
}

// 🔍 USER QUERY PATTERN TRACKING
function setupQueryPatternTracking() {
    const analysisForm = document.getElementById('analysisForm');
    if (!analysisForm) return;
    
    analysisForm.addEventListener('submit', function(e) {
        // Track the query pattern when analysis starts
        const formData = new FormData(e.target);
        trackQueryPattern({
            strategic_question: formData.get('strategic_question'),
            time_frame: formData.get('time_frame'),
            region: formData.get('region'),
            additional_instructions: formData.get('prompt'),
            user_id: userId
        });
    });
}

async function trackQueryPattern(queryData) {
    try {
        await fetch('/api/track-query-pattern', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(queryData)
        });
    } catch (error) {
        console.error('Error tracking query pattern:', error);
    }
}

// 🔧 MISSING HELPER FUNCTIONS

function applySuggestionAsTemplate(suggestion) {
    // This would typically load a full template, but for AI suggestions,
    // we'll generate a basic template structure
    const strategicQuestion = generateQuestionFromSuggestion(suggestion);
    
    const strategicQuestionField = document.getElementById('strategic_question');
    const timeFrameField = document.getElementById('time_frame');
    const regionField = document.getElementById('region');
    
    if (strategicQuestionField) strategicQuestionField.value = strategicQuestion;
    
    // Set default values based on suggestion
    if (suggestion.category.toLowerCase().includes('market')) {
        if (timeFrameField) timeFrameField.value = 'medium_term';
        if (regionField) regionField.value = 'global';
    } else if (suggestion.category.toLowerCase().includes('risk')) {
        if (timeFrameField) timeFrameField.value = 'short_term';
        if (regionField) regionField.value = 'global';
    } else {
        if (timeFrameField) timeFrameField.value = 'medium_term';
        if (regionField) regionField.value = 'global';
    }
    
    showToast(`Applied AI suggestion: ${suggestion.name}`, 'success');
}

function generateQuestionFromSuggestion(suggestion) {
    const templates = {
        'market': 'What are the key market opportunities and strategic considerations for [specific market/industry]? Analyze market dynamics, competitive landscape, entry strategies, and growth potential.',
        'technology': 'How will emerging technologies impact our [industry/business area] and what strategic responses should we implement? Assess technology trends, adoption patterns, and competitive implications.',
        'risk': 'What are the primary risks and mitigation strategies for our [business area/initiative]? Identify key risk factors, assess probability and impact, and recommend strategic responses.',
        'competitive': 'What is our competitive positioning in [market/industry] and how should we respond to competitive threats? Analyze competitor strategies, market share dynamics, and strategic opportunities.',
        'strategy': 'What strategic approach should we take for [business objective/initiative]? Evaluate strategic options, resource requirements, and implementation pathways.',
        'default': 'What are the strategic considerations and opportunities for [specific business challenge/opportunity]? Provide comprehensive analysis and actionable recommendations.'
    };
    
    const category = suggestion.category.toLowerCase();
    let template = templates.default;
    
    for (const key in templates) {
        if (category.includes(key)) {
            template = templates[key];
            break;
        }
    }
    
    return template;
}

function checkExistingAnalysisCompletion() {
    // Check if there's already a completed analysis on page load
    setTimeout(() => {
        checkAnalysisCompletion();
    }, 1000);
}

function collectAnalysisData() {
    // Collect current analysis data for template saving
    const agentCards = document.querySelectorAll('.agent-card');
    const analysisData = {
        agents: [],
        timestamp: new Date().toISOString(),
        form_data: {
            strategic_question: document.getElementById('strategic_question')?.value || '',
            time_frame: document.getElementById('time_frame')?.value || '',
            region: document.getElementById('region')?.value || '',
            additional_instructions: document.getElementById('prompt')?.value || ''
        }
    };
    
    agentCards.forEach(card => {
        const agentName = card.querySelector('h3')?.textContent || '';
        const agentContent = card.querySelector('.agent-content')?.innerHTML || '';
        const status = card.querySelector('.status-indicator')?.classList.contains('status-completed') ? 'completed' : 'pending';
        
        analysisData.agents.push({
            name: agentName,
            content: agentContent,
            status: status
        });
    });
    
    return analysisData;
}

// 🎨 UI ENHANCEMENT FUNCTIONS

function showToast(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transform transition-all duration-300 translate-x-full`;
    
    // Set colors based on type
    const colors = {
        'success': 'bg-green-500 text-white',
        'error': 'bg-red-500 text-white',
        'warning': 'bg-yellow-500 text-black',
        'info': 'bg-blue-500 text-white'
    };
    
    toast.className += ` ${colors[type] || colors.info}`;
    
    const icon = {
        'success': '✓',
        'error': '✗',
        'warning': '⚠',
        'info': 'ℹ'
    };
    
    toast.innerHTML = `
        <div class="flex items-center">
            <span class="text-lg mr-2">${icon[type] || icon.info}</span>
            <span class="font-medium">${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 5000);
}

// 🔄 REFRESH SUGGESTIONS
function setupRefreshSuggestions() {
    const refreshBtn = document.getElementById('refreshSuggestions');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            this.classList.add('animate-spin');
            loadAITemplateSuggestions();
            
            setTimeout(() => {
                this.classList.remove('animate-spin');
            }, 1000);
        });
    }
}

// Enhanced analysis completion detection
function checkAnalysisCompletion() {
    const agentCards = document.querySelectorAll('.agent-card');
    let completedCount = 0;
    
    agentCards.forEach(card => {
        const statusIndicator = card.querySelector('.status-indicator');
        if (statusIndicator && statusIndicator.classList.contains('status-completed')) {
            completedCount++;
        }
    });
    
    const isCompleted = completedCount >= 7; // At least 7 out of 8 agents completed
    
    if (isCompleted && !analysisCompleted) {
        analysisCompleted = true;
        
        // Show download and save as template buttons
        const downloadBtn = document.getElementById('downloadPdfBtn');
        const saveBtn = document.getElementById('saveAsTemplateBtn');
        
        if (downloadBtn) {
            downloadBtn.style.display = 'inline-block';
        }
        if (saveBtn) {
            saveBtn.style.display = 'inline-block';
        }
        
        showToast('Analysis completed! You can now download the PDF report or save as template.', 'success');
        
        // Store current analysis data for template saving
        currentAnalysisData = collectAnalysisData();
    }
    
    return isCompleted;
}

// Initialize refresh suggestions setup
document.addEventListener('DOMContentLoaded', function() {
    setupRefreshSuggestions();
}); 

// Force recalculate progress (useful for debugging or page refresh)
function forceRecalculateProgress() {
    const agentStatusList = document.getElementById('agentStatusList');
    if (!agentStatusList) {
        console.log('No agent status list found');
        return;
    }
    
    const agentItems = agentStatusList.querySelectorAll('[data-agent]');
    console.log(`Found ${agentItems.length} agents in progress list`);
    
    let completedCount = 0;
    agentItems.forEach((item, index) => {
        const agentName = item.getAttribute('data-agent');
        const innerHTML = item.innerHTML;
        const hasCheckmark = innerHTML.includes('✅');
        const statusText = item.querySelector('span:last-child')?.textContent.toLowerCase().trim();
        
        if (hasCheckmark || statusText === 'completed') {
            completedCount++;
        }
        
        console.log(`Agent ${index + 1}: ${agentName} - Completed: ${hasCheckmark || statusText === 'completed'}`);
    });
    
    console.log(`${completedCount}/${agentItems.length} agents completed`);
    
    // If all agents are completed, reset the button
    if (completedCount === agentItems.length && agentItems.length > 0) {
        resetAnalysisButton();
    }
    
    updateOverallProgress();
}

// Make functions globally available for debugging
window.resetAnalysisButton = resetAnalysisButton;
window.forceRecalculateProgress = forceRecalculateProgress;

// Handle streaming response from /analyze endpoint
async function handleStreamingAnalysis(formData) {
    try {
        // Create abort controller for cancellation
        currentAnalysisController = new AbortController();
        
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
            signal: currentAnalysisController.signal
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
                console.log('Analysis stream completed');
                break;
            }

            // Decode the chunk
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.trim()) {
                    try {
                        const data = JSON.parse(line);
                        handleAnalysisData(data);
                    } catch (parseError) {
                        console.warn('Failed to parse line:', line, parseError);
                    }
                }
            }
        }
        
        // Analysis completed successfully
        handleAnalysisComplete();
        
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Analysis was cancelled');
            handleAnalysisError('Analysis was cancelled');
        } else {
            console.error('Analysis error:', error);
            handleAnalysisError(error.message);
        }
    }
}

// Handle individual agent data from streaming response
function handleAnalysisData(data) {
    // Each data object contains one agent's result
    for (const [agentName, agentData] of Object.entries(data)) {
        if (agentName === 'session_info') {
            // Handle session completion info
            console.log('📊 Session info:', agentData);
            if (agentData.session_id) {
                currentSessionId = agentData.session_id;
                window.currentSessionId = agentData.session_id;
                console.log(`📊 Stored session ID: ${currentSessionId}`);
                
                // Initialize analysis data structure with session ID
                if (!window.analysisData) {
                    window.analysisData = {};
                }
                window.analysisData.session_id = currentSessionId;
            }
            continue;
        }
        
        if (agentName === 'error') {
            handleAnalysisError(agentData);
            return;
        }
        
        // Update agent output
        console.log(`📊 Received data for ${agentName}:`, agentData);
        
        // Store agent result ID and session ID if available
        if (agentData && typeof agentData === 'object') {
            // Initialize storage objects if they don't exist
            if (!window.agentResultIds) {
                window.agentResultIds = {};
            }
            if (!window.analysisData) {
                window.analysisData = {};
            }
            
            // Store agent result ID if present
            if (agentData.agent_result_id) {
                window.agentResultIds[agentName] = agentData.agent_result_id;
                console.log(`📊 Stored agent result ID for ${agentName}: ${agentData.agent_result_id}`);
            }
            
            // Store session ID if present
            if (agentData.session_id) {
                currentSessionId = agentData.session_id;
                window.currentSessionId = agentData.session_id;
                window.analysisData.session_id = agentData.session_id;
                console.log(`📊 Stored session ID from ${agentName}: ${agentData.session_id}`);
            }
            
            // Store the complete agent data for ratings
            window.analysisData[agentName] = agentData;
        }
        
        updateAgentOutput(agentName, agentData);
        
        // Update progress status
        updateAgentProgressStatus(agentName, 'completed', 100);
        
        // Update overall progress
        updateOverallProgress();
    }
}

// Handle analysis completion
function handleAnalysisComplete() {
    console.log('📊 Analysis completed successfully');
    showSuccessMessage('Analysis completed successfully!');
    updateProgressDetails('Analysis completed!', 'All agents finished successfully');
    
    // Log stored IDs for debugging
    console.log('📊 Final stored data:');
    console.log('   Session ID:', window.currentSessionId || currentSessionId);
    console.log('   Agent Result IDs:', window.agentResultIds);
    console.log('   Analysis Data Keys:', window.analysisData ? Object.keys(window.analysisData) : 'None');
    
    // Reset analysis state
    resetAnalysisButton();
    
    // Show download button
    showDownloadButton();
    
    // Check all agents completed
    checkAllAgentsCompleted();
    
    // Initialize rating system for completed analysis
    if (window.onAnalysisComplete) {
        console.log('📊 Triggering onAnalysisComplete callback');
        window.onAnalysisComplete();
    }
    
    // Add review button immediately
    setTimeout(() => {
        if (window.addReviewButton) {
            console.log('📊 Adding review button');
            window.addReviewButton();
        }
    }, 1000);
    
    // Dispatch custom event for rating system
    const analysisCompletedEvent = new CustomEvent('analysisCompleted', {
        detail: {
            sessionId: window.currentSessionId || currentSessionId,
            agentResultIds: window.agentResultIds,
            analysisData: window.analysisData
        }
    });
    document.dispatchEvent(analysisCompletedEvent);
    console.log('📊 Dispatched analysisCompleted event');
}

// Handle analysis errors
function handleAnalysisError(errorMessage) {
    console.error('Analysis error:', errorMessage);
    showErrorMessage(`Analysis failed: ${errorMessage}`);
    updateProgressDetails('Analysis failed', errorMessage);
    
    // Reset analysis state
    resetAnalysisButton();
}
