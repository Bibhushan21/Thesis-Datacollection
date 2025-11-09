// History page functionality
class HistoryManager {
    constructor() {
        this.currentPage = 0;
        this.pageSize = 12;
        this.sessions = [];
        this.totalSessions = 0;
        this.isLoading = false;
        this.currentFilters = {};
        this.hasMore = false;
        
        this.initializeElements();
        this.bindEvents();
        this.loadHistory();
    }
    
    initializeElements() {
        this.searchInput = document.getElementById('searchInput');
        this.statusFilter = document.getElementById('statusFilter');
        this.regionFilter = document.getElementById('regionFilter');
        this.applyFiltersBtn = document.getElementById('applyFilters');
        this.clearFiltersBtn = document.getElementById('clearFilters');
        this.historyGrid = document.getElementById('historyGrid');
        this.loadingState = document.getElementById('loadingState');
        this.emptyState = document.getElementById('emptyState');
        this.loadMoreSection = document.getElementById('loadMoreSection');
        this.loadMoreBtn = document.getElementById('loadMoreBtn');
        this.resultCount = document.getElementById('resultCount');
        this.sessionModal = document.getElementById('sessionModal');
        this.modalContent = document.getElementById('modalContent');
        this.closeModal = document.getElementById('closeModal');
    }
    
    bindEvents() {
        // Filter controls
        this.applyFiltersBtn.addEventListener('click', () => this.applyFilters());
        this.clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        
        // Search on Enter key
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.applyFilters();
            }
        });
        
        // Load more
        this.loadMoreBtn.addEventListener('click', () => this.loadMoreSessions());
        
        // Modal controls
        this.closeModal.addEventListener('click', () => this.closeSessionModal());
        this.sessionModal.addEventListener('click', (e) => {
            if (e.target === this.sessionModal) {
                this.closeSessionModal();
            }
        });
        
        // Mobile menu toggle
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (mobileMenuButton && mobileMenu) {
            mobileMenuButton.addEventListener('click', function() {
                mobileMenu.classList.toggle('hidden');
            });
        }
    }
    
    async loadHistory(reset = true) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        
        if (reset) {
            this.currentPage = 0;
            this.sessions = [];
            this.historyGrid.innerHTML = '';
            this.showLoading();
        }
        
        try {
            const params = new URLSearchParams({
                limit: this.pageSize,
                offset: this.currentPage * this.pageSize,
                ...this.currentFilters
            });
            
            const response = await fetch(`/api/analysis-history?${params}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                const newSessions = data.data.sessions || [];
                this.sessions = reset ? newSessions : [...this.sessions, ...newSessions];
                this.totalSessions = data.data.pagination?.total || this.sessions.length;
                this.hasMore = data.data.pagination?.has_more || false;
                
                this.renderSessions(newSessions, reset);
                this.updateResultCount();
                this.updateLoadMoreButton();
            } else {
                console.error('Failed to load history:', data.message);
                this.showEmptyState();
            }
        } catch (error) {
            console.error('Error loading history:', error);
            this.showEmptyState();
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    async loadMoreSessions() {
        this.currentPage++;
        await this.loadHistory(false);
    }
    
    applyFilters() {
        this.currentFilters = {
            search: this.searchInput.value.trim() || undefined,
            status: this.statusFilter.value || undefined,
            region: this.regionFilter.value || undefined
        };
        
        // Remove undefined values
        Object.keys(this.currentFilters).forEach(key => {
            if (this.currentFilters[key] === undefined) {
                delete this.currentFilters[key];
            }
        });
        
        this.loadHistory(true);
    }
    
    clearFilters() {
        this.searchInput.value = '';
        this.statusFilter.value = '';
        this.regionFilter.value = '';
        this.currentFilters = {};
        this.loadHistory(true);
    }
    
    renderSessions(sessions, reset = true) {
        if (reset) {
            this.historyGrid.innerHTML = '';
        }
        
        if (sessions.length === 0 && reset) {
            this.showEmptyState();
            return;
        }
        
        this.showHistoryGrid();
        
        sessions.forEach(session => {
            const sessionCard = this.createSessionCard(session);
            this.historyGrid.appendChild(sessionCard);
        });
    }
    
    createSessionCard(session) {
        const card = document.createElement('div');
        card.className = 'bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer transform hover:scale-105';
        
        const statusColor = this.getStatusColor(session.status);
        const regionDisplay = this.formatRegion(session.region);
        const timeFrameDisplay = this.formatTimeFrame(session.time_frame);
        
        card.innerHTML = `
            <div class="p-6">
                <!-- Header -->
                <div class="flex justify-between items-start mb-4">
                    <div class="flex-1">
                        <h3 class="text-lg font-semibold text-gray-800 line-clamp-2 mb-2">
                            ${this.truncateText(session.strategic_question, 80)}
                        </h3>
                        <div class="flex items-center space-x-2">
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColor}">
                                ${session.status}
                            </span>
                            <span class="text-xs text-gray-500">
                                Session #${session.id}
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- Details -->
                <div class="space-y-2 mb-4">
                    <div class="flex items-center text-sm text-gray-600">
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        ${regionDisplay}
                    </div>
                    <div class="flex items-center text-sm text-gray-600">
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        ${timeFrameDisplay}
                    </div>
                    <div class="flex items-center text-sm text-gray-600">
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                        </svg>
                        ${session.agent_results_count || 0} agents, ${Math.round(session.completion_rate || 0)}% complete
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="flex justify-between items-center text-xs text-gray-500 pt-4 border-t border-gray-100">
                    <span>${this.formatDate(session.created_at)}</span>
                                            <span class="text-brand-lapis hover:text-brand-oxford font-brand-regular font-medium">
                        View Details →
                    </span>
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => this.openSessionModal(session.id));
        
        return card;
    }
    
    async openSessionModal(sessionId) {
        try {
            this.sessionModal.classList.remove('hidden');
            
            // Scroll to the modal
            this.sessionModal.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            this.modalContent.innerHTML = `
                <div class="text-center py-12">
                    <div class="relative inline-block">
                        <div class="w-12 h-12 border-4 border-gray-200 rounded-full"></div>
                        <div class="absolute top-0 left-0 w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                    </div>
                    <p class="mt-4 text-gray-600 font-medium">Loading session details...</p>
                </div>
            `;
            
            const response = await fetch(`/api/analysis-session/${sessionId}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                const session = data.data;
                this.modalContent.innerHTML = `
                    <div class="space-y-6">
                        <!-- Session Overview -->
                        <div class="bg-gradient-to-r from-brand-lapis/5 to-brand-pervenche/5 rounded-xl p-6">
                            <h3 class="text-xl font-brand-black font-bold text-brand-oxford mb-4">Analysis Overview</h3>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <p class="text-sm text-brand-nickel mb-1">Strategic Question</p>
                                    <p class="font-brand-regular text-brand-oxford">${session.strategic_question}</p>
                                </div>
                                <div>
                                    <p class="text-sm text-brand-nickel mb-1">Region</p>
                                    <p class="font-brand-regular text-brand-oxford">${session.region || 'Not specified'}</p>
                                </div>
                                <div>
                                    <p class="text-sm text-brand-nickel mb-1">Time Frame</p>
                                    <p class="font-brand-regular text-brand-oxford">${session.time_frame || 'Not specified'}</p>
                                </div>
                                <div>
                                    <p class="text-sm text-brand-nickel mb-1">Status</p>
                                    <p class="font-brand-regular text-brand-oxford">${session.status}</p>
                                </div>
                            </div>
                            ${session.additional_instructions ? `
                                <div class="mt-4">
                                    <p class="text-sm text-brand-nickel mb-1">Additional Instructions</p>
                                    <p class="font-brand-regular text-brand-oxford">${session.additional_instructions}</p>
                                </div>
                            ` : ''}
                        </div>

                        <!-- Agent Results -->
                        <div class="space-y-4">
                            <h3 class="text-xl font-brand-black font-bold text-brand-oxford">Agent Results</h3>
                            ${session.agent_results.map(agent => `
                                <div class="bg-white rounded-xl shadow-sm border border-brand-kodama p-6">
                                    <div class="flex justify-between items-start mb-4">
                                        <div>
                                            <h4 class="text-lg font-brand-black font-bold text-brand-oxford">${agent.agent_name}</h4>
                                            <p class="text-sm text-brand-nickel">${agent.agent_type || 'Strategic Analysis'}</p>
                                        </div>
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                            agent.status === 'completed' ? 'bg-green-100 text-green-800' :
                                            agent.status === 'failed' ? 'bg-red-100 text-red-800' :
                                            agent.status === 'timeout' ? 'bg-yellow-100 text-yellow-800' :
                                            'bg-blue-100 text-blue-800'
                                        }">
                                            ${agent.status}
                                        </span>
                                    </div>
                                    ${agent.formatted_output ? `
                                        <div class="prose prose-sm max-w-none text-brand-oxford whitespace-pre-wrap">
                                            ${this.formatMarkdown(agent.formatted_output)}
                                        </div>
                                    ` : agent.error_message ? `
                                        <div class="text-red-600 text-sm">
                                            ${agent.error_message}
                                        </div>
                                    ` : `
                                        <div class="text-brand-nickel text-sm">
                                            No output available
                                        </div>
                                    `}
                                    ${agent.processing_time ? `
                                        <div class="mt-4 text-xs text-brand-nickel">
                                            Processing time: ${agent.processing_time.toFixed(2)} seconds
                                        </div>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>

                        <!-- Session Metadata -->
                        <div class="bg-gradient-to-r from-brand-lapis/5 to-brand-pervenche/5 rounded-xl p-6">
                            <h3 class="text-xl font-brand-black font-bold text-brand-oxford mb-4">Session Information</h3>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <p class="text-sm text-brand-nickel mb-1">Session ID</p>
                                    <p class="font-brand-regular text-brand-oxford">${session.id}</p>
                                </div>
                                <div>
                                    <p class="text-sm text-brand-nickel mb-1">Created At</p>
                                    <p class="font-brand-regular text-brand-oxford">${new Date(session.created_at).toLocaleString()}</p>
                                </div>
                                ${session.completed_at ? `
                                    <div>
                                        <p class="text-sm text-brand-nickel mb-1">Completed At</p>
                                        <p class="font-brand-regular text-brand-oxford">${new Date(session.completed_at).toLocaleString()}</p>
                                    </div>
                                ` : ''}
                                ${session.total_processing_time ? `
                                    <div>
                                        <p class="text-sm text-brand-nickel mb-1">Total Processing Time</p>
                                        <p class="font-brand-regular text-brand-oxford">${session.total_processing_time.toFixed(2)} seconds</p>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                `;
                
                // Scroll to the top of the modal content after it's loaded
                this.modalContent.scrollTop = 0;
            } else {
                this.modalContent.innerHTML = `
                    <div class="text-center py-12">
                        <p class="text-red-600 mb-4">Failed to load session details</p>
                        <p class="text-sm text-gray-500">${data.message || 'Please try again later'}</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading session details:', error);
            this.modalContent.innerHTML = `
                <div class="text-center py-12">
                    <p class="text-red-600 mb-4">Error loading session details</p>
                    <p class="text-sm text-gray-500">Please try again later</p>
                </div>
            `;
        }
    }
    
    closeSessionModal() {
        this.sessionModal.classList.add('hidden');
    }
    
    showLoading() {
        this.loadingState.classList.remove('hidden');
        this.historyGrid.classList.add('hidden');
        this.emptyState.classList.add('hidden');
    }
    
    hideLoading() {
        this.loadingState.classList.add('hidden');
    }
    
    showHistoryGrid() {
        this.historyGrid.classList.remove('hidden');
        this.emptyState.classList.add('hidden');
    }
    
    showEmptyState() {
        this.historyGrid.classList.add('hidden');
        this.emptyState.classList.remove('hidden');
        this.loadMoreSection.classList.add('hidden');
    }
    
    updateResultCount() {
        const displayed = this.sessions.length;
        const total = this.totalSessions;
        this.resultCount.textContent = `Showing ${displayed} of ${total} analyses`;
    }
    
    updateLoadMoreButton() {
        if (this.hasMore && this.sessions.length > 0) {
            this.loadMoreSection.classList.remove('hidden');
        } else {
            this.loadMoreSection.classList.add('hidden');
        }
    }
    
    getStatusColor(status) {
        const colors = {
            'completed': 'bg-green-100 text-green-800',
            'processing': 'bg-yellow-100 text-yellow-800',
            'failed': 'bg-red-100 text-red-800'
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    }
    
    formatRegion(region) {
        const regions = {
            'global': 'Global',
            'north_america': 'North America',
            'europe': 'Europe',
            'asia': 'Asia',
            'africa': 'Africa',
            'latin_america': 'Latin America'
        };
        return regions[region] || region || 'Unknown';
    }
    
    formatTimeFrame(timeFrame) {
        const frames = {
            'short_term': 'Short Term (1-2 years)',
            'medium_term': 'Medium Term (3-5 years)',
            'long_term': 'Long Term (5+ years)'
        };
        return frames[timeFrame] || timeFrame || 'Unknown';
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
    
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
    
    formatMarkdown(text) {
        if (!text) return '';
        
        // Remove scenario numbering (e.g., "#### Scenario 1" -> "#### Scenario")
        text = text.replace(/#### Scenario \d+/g, '#### Scenario');
        
        // Remove unnecessary line numbering (e.g., "1. Domain:" -> "Domain:")
        text = text.replace(/^\d+\.\s+/gm, '');
        
        // Replace markdown headers with styled headers
        text = text.replace(/^#### (.*$)/gm, '<h4 class="text-lg font-bold mt-4 mb-2 text-brand-oxford">$1</h4>');
        text = text.replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold mt-4 mb-2 text-brand-oxford">$1</h3>');
        text = text.replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold mt-6 mb-3 text-brand-oxford">$1</h2>');
        text = text.replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-8 mb-4 text-brand-oxford">$1</h1>');
        
        // Format structured data sections
        text = text.replace(/^Domain: (.*$)/gm, '<div class="mb-4"><span class="font-bold text-brand-oxford">Domain:</span> $1</div>');
        text = text.replace(/^Description: (.*$)/gm, '<div class="mb-4"><span class="font-bold text-brand-oxford">Description:</span> $1</div>');
        text = text.replace(/^Impact: (.*$)/gm, '<div class="mb-4"><span class="font-bold text-brand-oxford">Impact:</span> $1</div>');
        text = text.replace(/^Time: (.*$)/gm, '<div class="mb-4"><span class="font-bold text-brand-oxford">Time:</span> $1</div>');
        
        // Replace bold text
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold">$1</strong>');
        
        // Replace italic text
        text = text.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');
        
        // Replace bullet points
        text = text.replace(/^\s*[-*+]\s+(.*$)/gm, '<li class="ml-4">$1</li>');
        text = text.replace(/(<li class="ml-4">.*<\/li>)/gs, '<ul class="list-disc mb-4">$1</ul>');
        
        // // Replace numbered lists
        // text = text.replace(/^\s*\d+\.\s+(.*$)/gm, '<li class="ml-4">$1</li>');
        // text = text.replace(/(<li class="ml-4">.*<\/li>)/gs, '<ol class="list-decimal mb-4">$1</ol>');
        
        // Replace code blocks
        text = text.replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-100 p-4 rounded-lg my-4 overflow-x-auto"><code>$1</code></pre>');
        
        // Replace inline code
        text = text.replace(/`([^`]+)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>');
        
        // Replace horizontal rules
        text = text.replace(/^---$/gm, '<hr class="my-4 border-t border-gray-200">');
        
        // Replace blockquotes
        text = text.replace(/^>\s+(.*$)/gm, '<blockquote class="border-l-4 border-gray-300 pl-4 my-4 italic">$1</blockquote>');
        
        // Replace links
        text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-brand-lapis hover:text-brand-oxford underline">$1</a>');
        
        // Replace line breaks
        text = text.replace(/\n/g, '<br>');
        
        // Add spacing between sections
        text = text.replace(/<\/h4><br>/g, '</h4><div class="mb-6">');
        text = text.replace(/<\/div><br><h4/g, '</div><h4');
        
        return text;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new HistoryManager();
}); 