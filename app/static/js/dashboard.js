// Dashboard functionality with Chart.js visualizations
class DashboardManager {
    constructor() {
        this.currentPeriod = 30;
        this.dashboardData = null;
        this.charts = {};
        
        this.initializeElements();
        this.bindEvents();
        this.loadDashboard();
    }
    
    initializeElements() {
        this.timePeriodSelect = document.getElementById('timePeriodSelect');
        this.refreshBtn = document.getElementById('refreshDashboard');
        this.loadingState = document.getElementById('loadingState');
        this.dashboardContent = document.getElementById('dashboardContent');
        
        // Stats elements
        this.totalSessionsEl = document.getElementById('totalSessions');
        this.recentSessionsEl = document.getElementById('recentSessions');
        this.successRateEl = document.getElementById('successRate');
        this.avgTimeEl = document.getElementById('avgTime');
        this.agentRunsEl = document.getElementById('agentRuns');
        
        // Table and list elements
        this.agentPerformanceTable = document.getElementById('agentPerformanceTable');
        this.recentSessionsList = document.getElementById('recentSessionsList');
        
        // Chart canvas elements
        this.dailyActivityCanvas = document.getElementById('dailyActivityChart');
        this.statusChartCanvas = document.getElementById('statusChart');
        this.regionChartCanvas = document.getElementById('regionChart');
        this.timeframeChartCanvas = document.getElementById('timeframeChart');
    }
    
    bindEvents() {
        this.timePeriodSelect.addEventListener('change', () => {
            this.currentPeriod = parseInt(this.timePeriodSelect.value);
            this.loadDashboard();
        });
        
        this.refreshBtn.addEventListener('click', () => {
            this.loadDashboard();
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
    
    async loadDashboard() {
        this.showLoading();
        
        try {
            const response = await fetch(`/api/dashboard-stats?days_back=${this.currentPeriod}`);
            const result = await response.json();
            
            if (result.status === 'success') {
                this.dashboardData = result.data;
                this.renderDashboard();
            } else {
                console.error('Failed to load dashboard:', result.message);
                this.showError();
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError();
        } finally {
            this.hideLoading();
        }
    }
    
    renderDashboard() {
        if (!this.dashboardData) return;
        
        this.renderOverviewCards();
        this.renderCharts();
        this.renderAgentPerformanceTable();
        this.renderRecentSessions();
        this.showDashboard();
    }
    
    renderOverviewCards() {
        const overview = this.dashboardData.overview || {};
        
        this.totalSessionsEl.textContent = overview.total_sessions_all_time || 0;
        this.recentSessionsEl.textContent = `${overview.recent_sessions || 0} recent`;
        this.successRateEl.textContent = `${overview.success_rate || 0}%`;
        this.avgTimeEl.textContent = `${overview.avg_processing_time || 0}s`;
        
        // Calculate total agent runs
        const agentPerformance = this.dashboardData.agent_performance || [];
        const totalRuns = agentPerformance.reduce((sum, agent) => sum + (agent.total_runs || 0), 0);
        this.agentRunsEl.textContent = totalRuns;
    }
    
    renderCharts() {
        // Destroy existing charts
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
        
        this.renderDailyActivityChart();
        this.renderStatusChart();
        this.renderRegionChart();
        this.renderTimeframeChart();
    }
    
    renderDailyActivityChart() {
        const dailyActivity = this.dashboardData.daily_activity || [];
        
        const ctx = this.dailyActivityCanvas.getContext('2d');
        this.charts.dailyActivity = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dailyActivity.map(item => {
                    const date = new Date(item.date);
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                }),
                datasets: [{
                    label: 'Daily Sessions',
                    data: dailyActivity.map(item => item.count),
                    backgroundColor: 'rgba(22, 102, 151, 0.1)', // Lapis Jewel with transparency
                    borderColor: 'rgb(22, 102, 151)', // Lapis Jewel
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: 'rgb(22, 102, 151)', // Lapis Jewel
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    }
    
    renderStatusChart() {
        const statusBreakdown = this.dashboardData.status_breakdown || {};
        const labels = Object.keys(statusBreakdown);
        const data = Object.values(statusBreakdown);
        
        if (labels.length === 0) {
            this.statusChartCanvas.parentElement.innerHTML = '<div class="h-64 flex items-center justify-center text-gray-500">No data available</div>';
            return;
        }
        
        const colors = {
            'completed': '#166697', // Lapis Jewel
            'processing': '#008CED', // Pervenche
            'failed': '#00264B'  // Oxford Blue
        };
        
        const ctx = this.statusChartCanvas.getContext('2d');
        this.charts.status = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels.map(status => status.charAt(0).toUpperCase() + status.slice(1)),
                datasets: [{
                    data: data,
                    backgroundColor: labels.map(status => colors[status] || '#6B7280'),
                    borderWidth: 3,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }
    
    renderRegionChart() {
        const regionBreakdown = this.dashboardData.region_breakdown || {};
        const labels = Object.keys(regionBreakdown);
        const data = Object.values(regionBreakdown);
        
        if (labels.length === 0) {
            this.regionChartCanvas.parentElement.innerHTML = '<div class="h-64 flex items-center justify-center text-gray-500">No data available</div>';
            return;
        }
        
        const colors = [
            '#166697', '#008CED', '#00264B', '#939393', '#E6F1FF', '#ffffff' // Brand palette colors
        ];
        
        const ctx = this.regionChartCanvas.getContext('2d');
        this.charts.region = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels.map(region => this.formatRegionName(region)),
                datasets: [{
                    label: 'Sessions',
                    data: data,
                    backgroundColor: colors,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    renderTimeframeChart() {
        const timeframeBreakdown = this.dashboardData.timeframe_breakdown || {};
        const labels = Object.keys(timeframeBreakdown);
        const data = Object.values(timeframeBreakdown);
        
        if (labels.length === 0) {
            this.timeframeChartCanvas.parentElement.innerHTML = '<div class="h-64 flex items-center justify-center text-gray-500">No data available</div>';
            return;
        }
        
        const ctx = this.timeframeChartCanvas.getContext('2d');
        this.charts.timeframe = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels.map(tf => this.formatTimeframeName(tf)),
                datasets: [{
                    data: data,
                    backgroundColor: ['#166697', '#008CED', '#00264B'], // Lapis, Pervenche, Oxford Blue
                    borderWidth: 3,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }
    
    renderAgentPerformanceTable() {
        const agentPerformance = this.dashboardData.agent_performance || [];
        
        if (agentPerformance.length === 0) {
            this.agentPerformanceTable.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center py-8 text-gray-500">No agent performance data available</td>
                </tr>
            `;
            return;
        }
        
        this.agentPerformanceTable.innerHTML = agentPerformance.map(agent => `
            <tr class="hover:bg-gray-50 transition-colors">
                <td class="py-4 px-4 border-b border-gray-100">
                    <div class="flex items-center">
                        <div class="w-8 h-8 bg-gradient-to-r from-brand-lapis to-brand-pervenche rounded-full flex items-center justify-center mr-3">
                            <span class="text-white text-xs font-bold">${agent.agent_name.charAt(0)}</span>
                        </div>
                        <span class="font-medium text-gray-800">${agent.agent_name}</span>
                    </div>
                </td>
                <td class="py-4 px-4 border-b border-gray-100 text-gray-600">${agent.total_runs}</td>
                <td class="py-4 px-4 border-b border-gray-100">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${this.getSuccessRateColor(agent.success_rate)}">
                        ${agent.success_rate}%
                    </span>
                </td>
                <td class="py-4 px-4 border-b border-gray-100 text-gray-600">${agent.avg_processing_time}s</td>
                <td class="py-4 px-4 border-b border-gray-100">
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full" style="width: ${agent.success_rate}%"></div>
                    </div>
                </td>
            </tr>
        `).join('');
    }
    
    renderRecentSessions() {
        const recentSessions = this.dashboardData.recent_sessions || [];
        
        if (recentSessions.length === 0) {
            this.recentSessionsList.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <p>No recent sessions found</p>
                    <a href="/" class="text-brand-lapis hover:text-brand-oxford font-brand-regular font-medium mt-2 inline-block">
                        Start a new analysis →
                    </a>
                </div>
            `;
            return;
        }
        
        this.recentSessionsList.innerHTML = recentSessions.map(session => `
            <div class="border border-gray-200 rounded-xl p-4 hover:border-indigo-300 hover:shadow-md transition-all duration-200 cursor-pointer">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h4 class="font-semibold text-gray-800 mb-2 line-clamp-2">
                            ${this.truncateText(session.strategic_question, 80)}
                        </h4>
                        <div class="flex items-center space-x-4 text-sm text-gray-600">
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${this.getStatusColor(session.status)}">
                                ${session.status}
                            </span>
                            <span>${session.agent_count || 0} agents</span>
                            <span>${this.formatDate(session.created_at)}</span>
                        </div>
                    </div>
                    <div class="ml-4">
                        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    showLoading() {
        this.loadingState.classList.remove('hidden');
        this.dashboardContent.classList.add('hidden');
    }
    
    hideLoading() {
        this.loadingState.classList.add('hidden');
    }
    
    showDashboard() {
        this.dashboardContent.classList.remove('hidden');
    }
    
    showError() {
        this.hideLoading();
        // Could implement a proper error state here
        console.error('Dashboard loading failed');
    }
    
    getSuccessRateColor(rate) {
        if (rate >= 90) return 'bg-green-100 text-green-800';
        if (rate >= 70) return 'bg-yellow-100 text-yellow-800';
        return 'bg-red-100 text-red-800';
    }
    
    getStatusColor(status) {
        const colors = {
            'completed': 'bg-green-100 text-green-800',
            'processing': 'bg-yellow-100 text-yellow-800',
            'failed': 'bg-red-100 text-red-800'
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    }
    
    formatRegionName(region) {
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
    
    formatTimeframeName(timeframe) {
        const timeframes = {
            'short_term': 'Short Term',
            'medium_term': 'Medium Term',
            'long_term': 'Long Term'
        };
        return timeframes[timeframe] || timeframe || 'Unknown';
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }
    
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new DashboardManager();
}); 