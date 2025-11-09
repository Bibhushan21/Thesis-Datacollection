// Smart Templates Library functionality
class TemplatesManager {
    constructor() {
        this.templates = [];
        this.categories = [];
        this.currentOffset = 0;
        this.currentLimit = 12;
        this.hasMore = true;
        this.currentSearch = '';
        this.currentCategory = '';
        
        this.initializeElements();
        this.bindEvents();
        this.loadInitialData();
    }
    
    initializeElements() {
        // Control elements
        this.searchInput = document.getElementById('searchInput');
        this.categoryFilter = document.getElementById('categoryFilter');
        this.refreshBtn = document.getElementById('refreshTemplates');
        
        // Content elements
        this.loadingState = document.getElementById('loadingState');
        this.templatesContent = document.getElementById('templatesContent');
        this.categoryStats = document.getElementById('categoryStats');
        this.templatesGrid = document.getElementById('templatesGrid');
        this.loadMoreBtn = document.getElementById('loadMoreBtn');
        this.loadMoreSection = document.getElementById('loadMoreSection');
        
        // Modal elements
        this.templateModal = document.getElementById('templateModal');
        this.closeModal = document.getElementById('closeModal');
        this.modalCancel = document.getElementById('modalCancel');
        this.modalUseTemplate = document.getElementById('modalUseTemplate');
        this.modalTitle = document.getElementById('modalTitle');
        this.modalCategory = document.getElementById('modalCategory');
        this.modalDescription = document.getElementById('modalDescription');
        this.modalQuestion = document.getElementById('modalQuestion');
        this.modalTimeFrame = document.getElementById('modalTimeFrame');
        this.modalRegion = document.getElementById('modalRegion');
        this.modalInstructions = document.getElementById('modalInstructions');
        this.modalTags = document.getElementById('modalTags');
        this.modalUsageCount = document.getElementById('modalUsageCount');
        this.modalCreatedBy = document.getElementById('modalCreatedBy');
        
        this.currentTemplate = null;
    }
    
    bindEvents() {
        // Search functionality
        this.searchInput.addEventListener('input', this.debounce(() => {
            this.currentSearch = this.searchInput.value;
            this.resetAndLoad();
        }, 300));
        
        // Category filter
        this.categoryFilter.addEventListener('change', () => {
            this.currentCategory = this.categoryFilter.value;
            this.resetAndLoad();
        });
        
        // Refresh button
        this.refreshBtn.addEventListener('click', () => {
            this.loadInitialData();
        });
        
        // Load more button
        this.loadMoreBtn.addEventListener('click', () => {
            this.loadMoreTemplates();
        });
        
        // Modal events
        this.closeModal.addEventListener('click', () => this.hideModal());
        this.modalCancel.addEventListener('click', () => this.hideModal());
        this.modalUseTemplate.addEventListener('click', () => this.useTemplate());
        
        // Close modal on outside click
        this.templateModal.addEventListener('click', (e) => {
            if (e.target === this.templateModal) {
                this.hideModal();
            }
        });
        
        // Mobile menu is handled by mobile-menu.js
    }
    
    async loadInitialData() {
        this.showLoading();
        try {
            await Promise.all([
                this.loadCategories(),
                this.loadTemplates(true)
            ]);
            this.showContent();
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showError();
        }
    }
    
    async loadCategories() {
        try {
            const response = await fetch('/api/templates/categories');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.categories = result.data.categories;
                this.renderCategoryFilter();
                this.renderCategoryStats();
            }
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    }
    
    async loadTemplates(reset = false) {
        if (reset) {
            this.currentOffset = 0;
            this.templates = [];
        }
        
        try {
            const params = new URLSearchParams({
                limit: this.currentLimit,
                offset: this.currentOffset
            });
            
            if (this.currentSearch) {
                params.append('search', this.currentSearch);
            }
            
            if (this.currentCategory) {
                params.append('category', this.currentCategory);
            }
            
            const response = await fetch(`/api/templates?${params}`);
            const result = await response.json();
            
            if (result.status === 'success') {
                const newTemplates = result.data.templates;
                
                if (reset) {
                    this.templates = newTemplates;
                } else {
                    this.templates = [...this.templates, ...newTemplates];
                }
                
                this.hasMore = result.data.pagination.has_more;
                this.currentOffset += newTemplates.length;
                
                this.renderTemplates(reset);
                this.updateLoadMoreButton();
            }
        } catch (error) {
            console.error('Error loading templates:', error);
        }
    }
    
    resetAndLoad() {
        this.loadTemplates(true);
    }
    
    async loadMoreTemplates() {
        this.loadMoreBtn.textContent = 'Loading...';
        this.loadMoreBtn.disabled = true;
        
        await this.loadTemplates(false);
        
        this.loadMoreBtn.textContent = 'Load More Templates';
        this.loadMoreBtn.disabled = false;
    }
    
    renderCategoryFilter() {
        // Clear existing options (except "All Categories")
        while (this.categoryFilter.children.length > 1) {
            this.categoryFilter.removeChild(this.categoryFilter.lastChild);
        }
        
        // Add category options
        this.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.name;
            option.textContent = `${category.name} (${category.count})`;
            this.categoryFilter.appendChild(option);
        });
    }
    
    renderCategoryStats() {
        this.categoryStats.innerHTML = this.categories.map(category => `
            <div class="bg-gradient-to-br from-white to-gray-50 rounded-xl p-4 border border-gray-200 hover:border-indigo-300 hover:shadow-lg transition-all duration-300 cursor-pointer category-card" data-category="${category.name}">
                <div class="text-center">
                    <div class="w-12 h-12 bg-gradient-to-r from-brand-lapis to-brand-pervenche rounded-full flex items-center justify-center mx-auto mb-3">
                        <span class="text-white font-bold text-lg">${category.count}</span>
                    </div>
                    <h3 class="font-semibold text-gray-800 text-sm">${category.name}</h3>
                </div>
            </div>
        `).join('');
        
        // Add click handlers for category cards
        document.querySelectorAll('.category-card').forEach(card => {
            card.addEventListener('click', () => {
                const categoryName = card.dataset.category;
                this.categoryFilter.value = categoryName;
                this.currentCategory = categoryName;
                this.resetAndLoad();
            });
        });
    }
    
    renderTemplates(reset = false) {
        if (reset) {
            this.templatesGrid.innerHTML = '';
        }
        
        const newTemplatesHTML = this.templates.slice(reset ? 0 : this.templates.length - (this.currentOffset - this.templates.length)).map(template => `
            <div class="bg-gradient-to-br from-white to-gray-50 rounded-3xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-200 hover:border-indigo-300 template-card" data-template-id="${template.id}">
                <div class="p-6">
                    <!-- Template Header -->
                    <div class="flex justify-between items-start mb-4">
                        <div class="flex-1">
                            <h3 class="text-xl font-bold text-gray-800 mb-2">${template.name}</h3>
                            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                                ${template.category}
                            </span>
                        </div>
                        <div class="text-right text-sm text-gray-500">
                            <div class="flex items-center">
                                <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                <span>${template.usage_count} uses</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Description -->
                    <p class="text-gray-600 text-sm leading-relaxed mb-4 line-clamp-3">${template.description}</p>
                    
                    <!-- Strategic Question Preview -->
                    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 p-3 rounded-xl mb-4 border border-blue-200">
                        <p class="text-gray-700 text-sm italic line-clamp-2">${template.strategic_question}</p>
                    </div>
                    
                    <!-- Template Details -->
                    <div class="grid grid-cols-2 gap-3 mb-4 text-xs text-gray-600">
                        <div>
                            <span class="font-medium">Time Frame:</span>
                            <p class="truncate">${template.default_time_frame || 'Not specified'}</p>
                        </div>
                        <div>
                            <span class="font-medium">Region:</span>
                            <p class="truncate">${template.default_region || 'Not specified'}</p>
                        </div>
                    </div>
                    
                    <!-- Tags -->
                    <div class="flex flex-wrap gap-1 mb-4">
                        ${template.tags.slice(0, 3).map(tag => `
                            <span class="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">${tag}</span>
                        `).join('')}
                        ${template.tags.length > 3 ? `<span class="px-2 py-1 bg-gray-200 text-gray-600 rounded-full text-xs">+${template.tags.length - 3}</span>` : ''}
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="flex space-x-3">
                        <button class="flex-1 bg-gradient-to-r from-brand-lapis to-brand-pervenche text-white font-brand-black font-medium py-2 px-4 rounded-xl hover:from-brand-oxford hover:to-brand-lapis focus:outline-none focus:ring-2 focus:ring-brand-lapis/30 transition-all duration-300 use-template-btn">
                            Use Template
                        </button>
                        <button class="px-4 py-2 border border-brand-kodama text-brand-oxford rounded-xl hover:border-brand-lapis hover:text-brand-lapis focus:outline-none focus:ring-2 focus:ring-brand-lapis/30 transition-all duration-300 preview-template-btn font-brand-regular">
                            Preview
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
        if (reset) {
            this.templatesGrid.innerHTML = newTemplatesHTML;
        } else {
            this.templatesGrid.insertAdjacentHTML('beforeend', newTemplatesHTML);
        }
        
        // Add event listeners to new template cards
        this.bindTemplateEvents();
    }
    
    bindTemplateEvents() {
        // Preview buttons
        document.querySelectorAll('.preview-template-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const templateId = parseInt(btn.closest('.template-card').dataset.templateId);
                this.showTemplatePreview(templateId);
            });
        });
        
        // Use template buttons
        document.querySelectorAll('.use-template-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const templateId = parseInt(btn.closest('.template-card').dataset.templateId);
                this.useTemplateById(templateId);
            });
        });
        
        // Card click for preview
        document.querySelectorAll('.template-card').forEach(card => {
            card.addEventListener('click', () => {
                const templateId = parseInt(card.dataset.templateId);
                this.showTemplatePreview(templateId);
            });
        });
    }
    
    showTemplatePreview(templateId) {
        const template = this.templates.find(t => t.id === templateId);
        if (!template) return;
        
        this.currentTemplate = template;
        
        // Populate modal content
        this.modalTitle.textContent = template.name;
        this.modalCategory.textContent = template.category;
        this.modalDescription.textContent = template.description;
        this.modalQuestion.textContent = template.strategic_question;
        this.modalTimeFrame.textContent = template.default_time_frame || 'Not specified';
        this.modalRegion.textContent = template.default_region || 'Not specified';
        this.modalInstructions.textContent = template.additional_instructions || 'No additional instructions';
        this.modalUsageCount.textContent = template.usage_count;
        this.modalCreatedBy.textContent = template.created_by;
        
        // Render tags
        this.modalTags.innerHTML = template.tags.map(tag => `
            <span class="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm font-medium">${tag}</span>
        `).join('');
        
        this.showModal();
    }
    
    async useTemplateById(templateId) {
        const template = this.templates.find(t => t.id === templateId);
        if (!template) return;
        
        this.currentTemplate = template;
        await this.useTemplate();
    }
    
    async useTemplate() {
        if (!this.currentTemplate) return;
        
        try {
            // Record template usage
            await fetch(`/api/templates/${this.currentTemplate.id}/use`, {
                method: 'POST'
            });
            
            // Navigate to main page with template data
            const templateData = {
                strategic_question: this.currentTemplate.strategic_question,
                time_frame: this.currentTemplate.default_time_frame,
                region: this.currentTemplate.default_region,
                additional_instructions: this.currentTemplate.additional_instructions,
                template_id: this.currentTemplate.id,
                template_name: this.currentTemplate.name
            };
            
            // Store template data in sessionStorage
            sessionStorage.setItem('selectedTemplate', JSON.stringify(templateData));
            
            // Navigate to main page
            window.location.href = '/?template=true';
            
        } catch (error) {
            console.error('Error using template:', error);
        }
    }
    
    updateLoadMoreButton() {
        if (this.hasMore && this.templates.length > 0) {
            this.loadMoreBtn.classList.remove('hidden');
        } else {
            this.loadMoreBtn.classList.add('hidden');
        }
    }
    
    showModal() {
        this.templateModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
    
    hideModal() {
        this.templateModal.classList.add('hidden');
        document.body.style.overflow = 'auto';
        this.currentTemplate = null;
    }
    
    showLoading() {
        this.loadingState.classList.remove('hidden');
        this.templatesContent.classList.add('hidden');
    }
    
    showContent() {
        this.loadingState.classList.add('hidden');
        this.templatesContent.classList.remove('hidden');
    }
    
    showError() {
        this.loadingState.classList.add('hidden');
        this.templatesContent.innerHTML = `
            <div class="text-center py-16">
                <div class="max-w-md mx-auto">
                    <svg class="w-16 h-16 text-red-400 mx-auto mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <h3 class="text-xl font-bold text-gray-800 mb-2">Unable to Load Templates</h3>
                    <p class="text-gray-600 mb-6">There was an error loading the template library. Please try refreshing the page.</p>
                    <button onclick="window.location.reload()" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
                        Refresh Page
                    </button>
                </div>
            </div>
        `;
        this.templatesContent.classList.remove('hidden');
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new TemplatesManager();
}); 