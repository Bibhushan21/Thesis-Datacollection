// Performance Analytics functionality with advanced visualizations
class PerformanceAnalytics {
    constructor() {
        this.currentPeriod = 30;
        this.analyticsData = null;
        this.charts = {};
        this.currentTrendsView = 'time'; // 'time' or 'success'
        
        this.initializeElements();
        this.bindEvents();
        this.loadAnalytics();
    }
    
    initializeElements() {
        this.timePeriodSelect = document.getElementById('timePeriodSelect');
        this.refreshBtn = document.getElementById('refreshAnalytics');
        this.exportBtn = document.getElementById('exportReport');
        this.loadingState = document.getElementById('loadingState');
        this.analyticsContent = document.getElementById('analyticsContent');
        
        // Metrics elements
        this.systemHealthScore = document.getElementById('systemHealthScore');
        this.benchmarkTime = document.getElementById('benchmarkTime');
        this.activeIssues = document.getElementById('activeIssues');
        
        // Recommendations
        this.recommendationsSection = document.getElementById('recommendationsSection');
        this.recommendationsList = document.getElementById('recommendationsList');
        
        // Chart controls
        this.trendsViewTime = document.getElementById('trendsViewTime');
        this.trendsViewSuccess = document.getElementById('trendsViewSuccess');
        
        // Table and content areas
        this.performanceAnalysisTable = document.getElementById('performanceAnalysisTable');
        this.errorAnalysisContent = document.getElementById('errorAnalysisContent');
        
        // Chart canvas elements
        this.performanceTrendsCanvas = document.getElementById('performanceTrendsChart');
        this.processingTimeCanvas = document.getElementById('processingTimeChart');
        this.performanceScoreCanvas = document.getElementById('performanceScoreChart');
    }
    
    bindEvents() {
        this.timePeriodSelect.addEventListener('change', () => {
            this.currentPeriod = parseInt(this.timePeriodSelect.value);
            this.loadAnalytics();
        });
        
        this.refreshBtn.addEventListener('click', () => {
            this.loadAnalytics();
        });
        
        this.exportBtn.addEventListener('click', () => {
            this.exportReport();
        });
        
        // Trends view toggles
        this.trendsViewTime.addEventListener('click', () => {
            this.switchTrendsView('time');
        });
        
        this.trendsViewSuccess.addEventListener('click', () => {
            this.switchTrendsView('success');
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
    
    async loadAnalytics() {
        this.showLoading();
        
        try {
            const response = await fetch(`/api/performance-analytics?days_back=${this.currentPeriod}`);
            const result = await response.json();
            
            if (result.status === 'success') {
                this.analyticsData = result.data;
                this.renderAnalytics();
            } else {
                console.error('Failed to load analytics:', result.message);
                this.showError();
            }
        } catch (error) {
            console.error('Error loading analytics:', error);
            this.showError();
        } finally {
            this.hideLoading();
        }
    }
    
    renderAnalytics() {
        if (!this.analyticsData) return;
        
        console.log('Rendering analytics with data:', this.analyticsData);
        
        this.renderMetricCards();
        this.renderRecommendations();
        this.renderCharts();
        this.renderPerformanceTable();
        this.renderErrorAnalysis();
        
        // Show a welcome message if no significant data exists
        this.checkForEmptyState();
        
        this.showAnalytics();
    }
    
    checkForEmptyState() {
        const processingAnalysis = this.analyticsData.processing_analysis || [];
        const agentComparisons = this.analyticsData.agent_comparisons || [];
        const recommendations = this.analyticsData.recommendations || [];
        const systemBenchmarks = this.analyticsData.system_benchmarks || {};
        
        const hasData = processingAnalysis.length > 0 || 
                       agentComparisons.length > 0 || 
                       recommendations.length > 0 ||
                       (systemBenchmarks.total_runs && systemBenchmarks.total_runs > 0);
        
        if (!hasData) {
            // Add a welcome banner for empty state
            const welcomeBanner = document.createElement('div');
            welcomeBanner.className = 'bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-8 mb-8';
            welcomeBanner.innerHTML = `
                <div class="text-center">
                    <div class="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                        </svg>
                    </div>
                    <h3 class="text-2xl font-bold text-gray-800 mb-3">Welcome to Performance Analytics!</h3>
                    <p class="text-gray-600 mb-4 max-w-2xl mx-auto">
                        This dashboard will show detailed performance insights once you start running analysis sessions. 
                        The system is ready and monitoring all agent activities.
                    </p>
                    <div class="flex items-center justify-center space-x-6 text-sm text-gray-500">
                        <div class="flex items-center">
                            <div class="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
                            <span>System Online</span>
                        </div>
                        <div class="flex items-center">
                            <div class="w-3 h-3 bg-blue-400 rounded-full mr-2"></div>
                            <span>9 Agents Ready</span>
                        </div>
                        <div class="flex items-center">
                            <div class="w-3 h-3 bg-purple-400 rounded-full mr-2"></div>
                            <span>Monitoring Active</span>
                        </div>
                    </div>
                    <div class="mt-6">
                        <a href="/" class="bg-gradient-to-r from-brand-lapis to-brand-pervenche text-white px-6 py-3 rounded-xl hover:from-brand-oxford hover:to-brand-lapis transition-all duration-300 inline-flex items-center font-brand-black">
                            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                            </svg>
                            Start First Analysis
                        </a>
                    </div>
                </div>
            `;
            
            // Insert the banner at the beginning of the analytics content
            this.analyticsContent.insertBefore(welcomeBanner, this.analyticsContent.firstChild);
        }
    }
    
    renderMetricCards() {
        const systemBenchmarks = this.analyticsData.system_benchmarks || {};
        const agentComparisons = this.analyticsData.agent_comparisons || [];
        const recommendations = this.analyticsData.recommendations || [];
        
        console.log('System benchmarks:', systemBenchmarks);
        console.log('Agent comparisons:', agentComparisons);
        console.log('Recommendations:', recommendations);
        
        // Calculate system health score (average of all agent performance scores)
        const avgPerformanceScore = agentComparisons.length > 0 
            ? agentComparisons.reduce((sum, agent) => sum + agent.performance_score, 0) / agentComparisons.length
            : 0;
        
        this.systemHealthScore.textContent = Math.round(avgPerformanceScore);
        this.benchmarkTime.textContent = `${(systemBenchmarks.avg_processing_time || 0).toFixed(1)}s`;
        
        // Count high priority issues
        const highPriorityIssues = recommendations.filter(rec => rec.priority === 'high').length;
        this.activeIssues.textContent = highPriorityIssues;
    }
    
    renderRecommendations() {
        const recommendations = this.analyticsData.recommendations || [];
        
        if (recommendations.length === 0) {
            this.recommendationsSection.classList.add('hidden');
            return;
        }
        
        this.recommendationsSection.classList.remove('hidden');
        
        this.recommendationsList.innerHTML = recommendations.map(rec => `
            <div class="flex items-start space-x-3 p-3 bg-white/70 rounded-lg">
                <div class="flex-shrink-0">
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${this.getPriorityColor(rec.priority)}">
                        ${rec.priority.toUpperCase()}
                    </span>
                </div>
                <div class="flex-1">
                    <p class="text-sm font-medium text-gray-800">${rec.agent}</p>
                    <p class="text-sm text-gray-600 mt-1">${rec.message}</p>
                </div>
                <div class="flex-shrink-0">
                    <div class="w-6 h-6 rounded-full ${this.getTypeColor(rec.type)} flex items-center justify-center">
                        ${this.getTypeIcon(rec.type)}
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    renderCharts() {
        // Destroy existing charts
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
        
        this.renderPerformanceTrendsChart();
        this.renderProcessingTimeChart();
        this.renderPerformanceScoreChart();
    }
    
    renderPerformanceTrendsChart() {
        const performanceTrends = this.analyticsData.performance_trends || [];
        
        if (performanceTrends.length === 0) {
            this.performanceTrendsCanvas.parentElement.innerHTML = '<div class="h-80 flex items-center justify-center text-gray-500">No trend data available</div>';
            return;
        }
        
        // Get all unique agent names
        const allAgents = new Set();
        performanceTrends.forEach(day => {
            Object.keys(day.agents).forEach(agent => allAgents.add(agent));
        });
        
        const agentsList = Array.from(allAgents);
        
        // Check if we have any agents at all
        if (agentsList.length === 0) {
            this.performanceTrendsCanvas.parentElement.innerHTML = '<div class="h-80 flex items-center justify-center text-gray-500">No agent activity data available for the selected period</div>';
            return;
        }
        
        const colors = ['#166697', '#008CED', '#00264B', '#939393', '#E6F1FF', '#ffffff']; // Brand palette colors
        
        const datasets = agentsList.map((agent, index) => {
            const data = performanceTrends.map(day => {
                const agentData = day.agents[agent];
                if (!agentData) return null;
                
                return this.currentTrendsView === 'time' 
                    ? agentData.avg_processing_time 
                    : agentData.success_rate;
            });
            
            return {
                label: agent,
                data: data,
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length] + '20',
                fill: false,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: colors[index % colors.length],
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            };
        });
        
        const ctx = this.performanceTrendsCanvas.getContext('2d');
        this.charts.performanceTrends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: performanceTrends.map(day => {
                    const date = new Date(day.date);
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                }),
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: this.currentTrendsView === 'time' ? 'Processing Time (seconds)' : 'Success Rate (%)'
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
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }
    
    renderProcessingTimeChart() {
        const processingAnalysis = this.analyticsData.processing_analysis || [];
        
        if (processingAnalysis.length === 0) {
            this.processingTimeCanvas.parentElement.innerHTML = '<div class="h-64 flex items-center justify-center text-gray-500">No processing data available</div>';
            return;
        }
        
        const ctx = this.processingTimeCanvas.getContext('2d');
        this.charts.processingTime = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: processingAnalysis.map(agent => agent.agent_name),
                datasets: [
                    {
                        label: 'Min Time',
                        data: processingAnalysis.map(agent => agent.min_time),
                        backgroundColor: '#166697', // Lapis Jewel
                        borderRadius: 4
                    },
                    {
                        label: 'Avg Time',
                        data: processingAnalysis.map(agent => agent.avg_time),
                        backgroundColor: '#008CED', // Pervenche
                        borderRadius: 4
                    },
                    {
                        label: 'Max Time',
                        data: processingAnalysis.map(agent => agent.max_time),
                        backgroundColor: '#00264B', // Oxford Blue
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Processing Time (seconds)'
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
    
    renderPerformanceScoreChart() {
        const agentComparisons = this.analyticsData.agent_comparisons || [];
        
        if (agentComparisons.length === 0) {
            this.performanceScoreCanvas.parentElement.innerHTML = '<div class="h-64 flex items-center justify-center text-gray-500">No performance data available</div>';
            return;
        }
        
        const ctx = this.performanceScoreCanvas.getContext('2d');
        this.charts.performanceScore = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: agentComparisons.map(agent => agent.agent_name),
                datasets: [{
                    label: 'Performance Score',
                    data: agentComparisons.map(agent => agent.performance_score),
                    backgroundColor: agentComparisons.map(agent => {
                        if (agent.performance_score >= 90) return '#166697'; // Lapis Jewel for excellent
                        if (agent.performance_score >= 70) return '#008CED'; // Pervenche for good  
                        return '#00264B'; // Oxford Blue for needs improvement
                    }),
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Performance Score'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    renderPerformanceTable() {
        const processingAnalysis = this.analyticsData.processing_analysis || [];
        const agentComparisons = this.analyticsData.agent_comparisons || [];
        
        // Merge the data
        const mergedData = processingAnalysis.map(proc => {
            const comparison = agentComparisons.find(comp => comp.agent_name === proc.agent_name);
            return {
                ...proc,
                performance_score: comparison ? comparison.performance_score : 0,
                system_avg_ratio: comparison ? comparison.system_avg_ratio : 1
            };
        });
        
        if (mergedData.length === 0) {
            this.performanceAnalysisTable.innerHTML = `
                <tr>
                    <td colspan="8" class="py-8 text-center text-gray-500">
                        <div class="flex flex-col items-center">
                            <svg class="w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                            <p class="text-lg font-medium">No performance data available</p>
                            <p class="text-sm text-gray-400 mt-1">Run some analysis sessions to see detailed performance metrics</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }
        
        this.performanceAnalysisTable.innerHTML = mergedData.map(agent => `
            <tr class="hover:bg-gray-50 transition-colors">
                <td class="py-4 px-4 border-b border-gray-100">
                    <div class="flex items-center">
                        <div class="w-8 h-8 bg-gradient-to-r from-brand-lapis to-brand-pervenche rounded-full flex items-center justify-center mr-3">
                            <span class="text-white text-xs font-bold">${agent.agent_name.charAt(0)}</span>
                        </div>
                        <span class="font-medium text-gray-800">${agent.agent_name}</span>
                    </div>
                </td>
                <td class="py-4 px-4 border-b border-gray-100">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${this.getPerformanceScoreColor(agent.performance_score || 0)}">
                        ${Math.round(agent.performance_score || 0)}
                    </span>
                </td>
                <td class="py-4 px-4 border-b border-gray-100 text-gray-600">${(agent.avg_time || 0).toFixed(1)}s</td>
                <td class="py-4 px-4 border-b border-gray-100 text-gray-600">${(agent.min_time || 0).toFixed(1)}s</td>
                <td class="py-4 px-4 border-b border-gray-100 text-gray-600">${(agent.max_time || 0).toFixed(1)}s</td>
                <td class="py-4 px-4 border-b border-gray-100 text-gray-600">${(agent.time_variance || 0).toFixed(1)}s</td>
                <td class="py-4 px-4 border-b border-gray-100">
                    <span class="text-sm ${agent.system_avg_ratio > 1.2 ? 'text-red-600' : agent.system_avg_ratio < 0.8 ? 'text-green-600' : 'text-gray-600'}">
                        ${(agent.system_avg_ratio || 1).toFixed(1)}x
                    </span>
                </td>
                <td class="py-4 px-4 border-b border-gray-100 text-gray-600">${agent.total_runs || 0}</td>
            </tr>
        `).join('');
    }
    
    renderErrorAnalysis() {
        const errorBreakdown = this.analyticsData.error_breakdown || {};
        
        if (Object.keys(errorBreakdown).length === 0) {
            this.errorAnalysisContent.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <p>No error data available for the selected period</p>
                </div>
            `;
            return;
        }
        
        this.errorAnalysisContent.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                ${Object.entries(errorBreakdown).map(([agentName, statuses]) => {
                    const total = Object.values(statuses).reduce((sum, count) => sum + count, 0);
                    const completed = statuses.completed || 0;
                    const failed = statuses.failed || 0;
                    const processing = statuses.processing || 0;
                    
                    const successRate = total > 0 ? (completed / total * 100) : 0;
                    const failureRate = total > 0 ? (failed / total * 100) : 0;
                    
                    return `
                        <div class="bg-gradient-to-br from-gray-50 to-white rounded-xl p-4 border border-gray-200">
                            <div class="flex items-center justify-between mb-3">
                                <h4 class="font-semibold text-gray-800">${agentName}</h4>
                                <span class="text-xs text-gray-500">${total} runs</span>
                            </div>
                            <div class="space-y-2">
                                <div class="flex justify-between text-sm">
                                    <span class="text-green-600">Completed</span>
                                    <span class="font-medium">${completed} (${successRate.toFixed(1)}%)</span>
                                </div>
                                <div class="flex justify-between text-sm">
                                    <span class="text-red-600">Failed</span>
                                    <span class="font-medium">${failed} (${failureRate.toFixed(1)}%)</span>
                                </div>
                                ${processing > 0 ? `
                                    <div class="flex justify-between text-sm">
                                        <span class="text-yellow-600">Processing</span>
                                        <span class="font-medium">${processing}</span>
                                    </div>
                                ` : ''}
                            </div>
                            <div class="mt-3">
                                <div class="w-full bg-gray-200 rounded-full h-2">
                                    <div class="bg-green-500 h-2 rounded-full" style="width: ${successRate}%"></div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }
    
    switchTrendsView(view) {
        this.currentTrendsView = view;
        
        // Update button states
        if (view === 'time') {
            this.trendsViewTime.className = 'px-4 py-2 bg-indigo-100 text-indigo-700 rounded-lg font-medium transition-colors';
            this.trendsViewSuccess.className = 'px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium transition-colors hover:bg-gray-200';
        } else {
            this.trendsViewTime.className = 'px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium transition-colors hover:bg-gray-200';
            this.trendsViewSuccess.className = 'px-4 py-2 bg-indigo-100 text-indigo-700 rounded-lg font-medium transition-colors';
        }
        
        // Re-render the trends chart
        this.renderPerformanceTrendsChart();
    }
    
    exportReport() {
        // Generate a simple text report
        const systemBenchmarks = this.analyticsData.system_benchmarks || {};
        const agentComparisons = this.analyticsData.agent_comparisons || [];
        const recommendations = this.analyticsData.recommendations || [];
        
        const reportContent = `
PERFORMANCE ANALYTICS REPORT
Generated: ${new Date().toLocaleString()}
Analysis Period: ${this.currentPeriod} days

SYSTEM OVERVIEW
- Average Processing Time: ${systemBenchmarks.avg_processing_time || 0}s
- Total Runs: ${systemBenchmarks.total_runs || 0}
- Active Issues: ${recommendations.filter(r => r.priority === 'high').length}

AGENT PERFORMANCE
${agentComparisons.map(agent => `
- ${agent.agent_name}:
  Performance Score: ${agent.performance_score}
  Average Time: ${agent.avg_time}s
  System Ratio: ${agent.system_avg_ratio}x
`).join('')}

RECOMMENDATIONS
${recommendations.map(rec => `
- [${rec.priority.toUpperCase()}] ${rec.agent}: ${rec.message}
`).join('')}
        `;
        
        // Create and download the report
        const blob = new Blob([reportContent], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `performance-report-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
    
    showLoading() {
        this.loadingState.classList.remove('hidden');
        this.analyticsContent.classList.add('hidden');
    }
    
    hideLoading() {
        this.loadingState.classList.add('hidden');
    }
    
    showAnalytics() {
        this.analyticsContent.classList.remove('hidden');
        console.log('Analytics content shown');
    }
    
    showError() {
        this.hideLoading();
        this.analyticsContent.classList.remove('hidden');
        
        // Show error state in the main content area
        this.analyticsContent.innerHTML = `
            <div class="text-center py-16">
                <div class="max-w-md mx-auto">
                    <svg class="w-16 h-16 text-red-400 mx-auto mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <h3 class="text-xl font-bold text-gray-800 mb-2">Unable to Load Analytics</h3>
                    <p class="text-gray-600 mb-6">There was an error loading the performance analytics. Please try refreshing the page.</p>
                    <button onclick="window.location.reload()" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
                        Refresh Page
                    </button>
                </div>
            </div>
        `;
        
        console.error('Analytics loading failed - showing error state');
    }
    
    getPriorityColor(priority) {
        const colors = {
            'high': 'bg-red-100 text-red-800',
            'medium': 'bg-yellow-100 text-yellow-800',
            'low': 'bg-blue-100 text-blue-800'
        };
        return colors[priority] || 'bg-gray-100 text-gray-800';
    }
    
    getTypeColor(type) {
        const colors = {
            'performance': 'bg-blue-500',
            'optimization': 'bg-orange-500',
            'reliability': 'bg-red-500'
        };
        return colors[type] || 'bg-gray-500';
    }
    
    getTypeIcon(type) {
        const icons = {
            'performance': '⚡',
            'optimization': '🔧',
            'reliability': '🛡️'
        };
        return icons[type] || '⚠️';
    }
    
    getPerformanceScoreColor(score) {
        if (score >= 90) return 'bg-green-100 text-green-800';
        if (score >= 70) return 'bg-yellow-100 text-yellow-800';
        return 'bg-red-100 text-red-800';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new PerformanceAnalytics();
}); 