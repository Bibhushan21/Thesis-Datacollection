// Strategic Intelligence Analysis Home Page JavaScript

// DOM Elements
let analysisForm;
let analyzeBtn;
let buttonText;
let searchSection;
let loadingSection;
let resultsSection;
let progressBar;
let progressText;
let exportPdfBtn;
let exportWordBtn;

// Global variables
let analysisData = {};
let isAnalyzing = false;

// Agent mapping for display
const agentMapping = {
    'Problem Explorer': {
        section: 'problemAnalysis',
        title: 'Problem Analysis'
    },
    'Best Practices': {
        section: 'bestPractices',
        title: 'Best Practices & Proven Solutions'
    },
    'Horizon Scanning': {
        section: 'futureTrends',
        title: 'Future Trends & Opportunities'
    },
    'Scenario Planning': {
        section: 'scenarioAnalysis',
        title: 'Scenario Analysis'
    },
    'Research Synthesis': {
        section: 'researchSynthesis',
        title: 'Research Synthesis'
    },
    'Strategic Action': {
        section: 'strategicActions',
        title: 'Strategic Actions & Recommendations'
    },
    'High Impact': {
        section: 'highImpact',
        title: 'High Impact Initiatives'
    },
    'Backcasting': {
        section: 'implementationRoadmap',
        title: 'Implementation Roadmap'
    }
};

// Progress messages
const progressMessages = [
    "Initializing AI agents...",
    "Analyzing problem structure...",
    "Researching best practices...",
    "Scanning future trends...",
    "Developing scenarios...",
    "Synthesizing research...",
    "Formulating strategies...",
    "Identifying high-impact initiatives...",
    "Creating implementation roadmap...",
    "Finalizing analysis..."
];

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed. Initializing home.js...");
    cacheDomElements();
    if (!analysisForm || !analyzeBtn) {
        console.error('Required DOM elements are missing. Ensure the template includes the analysis form and button.');
        return;
    }
    console.log("Found analysisForm and analyzeBtn elements.");
    setupEventListeners();
});

function cacheDomElements() {
    console.log("Caching DOM elements...");
    analysisForm = document.getElementById('analysisForm');
    analyzeBtn = document.getElementById('submit-btn');
    buttonText = document.getElementById('buttonText');
    searchSection = document.getElementById('search-section');
    loadingSection = document.getElementById('loading-section');
    resultsSection = document.getElementById('resultsSection');
    progressBar = document.getElementById('progressBar');
    progressText = document.getElementById('progressText');
    exportPdfBtn = document.getElementById('exportPdf');
    exportWordBtn = document.getElementById('exportWord');
    console.log("Finished caching DOM elements.");
}

function setupEventListeners() {
    console.log("Setting up event listeners...");
    // Form submission
    if (analysisForm) {
        analysisForm.addEventListener('submit', handleFormSubmission);
        console.log("Successfully added submit event listener to analysisForm.");
    } else {
        console.error("analysisForm element not found, could not add event listener.");
    }
    
    // Export buttons
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', exportToPDF);
    }
    if (exportWordBtn) {
        exportWordBtn.addEventListener('click', exportToWord);
    }
}

async function handleFormSubmission(e) {
    console.log("Analysis form submitted. handleFormSubmission function started.");
    e.preventDefault();
    console.log("Default form submission behavior prevented.");
    
    if (isAnalyzing) {
        console.log("Analysis already in progress. Aborting.");
        return;
    }
    
    isAnalyzing = true;
    console.log("isAnalyzing flag set to true.");
    
    // Get form data
    const formData = new FormData(e.target);
    const inputData = {
        strategic_question: formData.get('strategic_question'),
        time_frame: formData.get('time_frame'),
        region: formData.get('region'),
        architecture: formData.get('architecture'),
        prompt: formData.get('prompt') || null
    };
    
    // Show loading state
    showLoadingState();
    
    try {
        console.log("Sending analysis request to the backend with data:", inputData);
        // Start the analysis
        await performAnalysis(inputData);
        
        // Create executive summary
        createExecutiveSummary(inputData);
        
        // Show results
        showResults();
        
    } catch (error) {
        console.error('Analysis failed:', error);
        showError('Analysis failed. Please try again.');
    } finally {
        isAnalyzing = false;
    }
}

function showLoadingState() {
    // Update button
    analyzeBtn.disabled = true;
    buttonText.innerHTML = `
        <svg class="w-5 h-5 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Analyzing...
    `;
    
    // Show loading section
    loadingSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    
    // Start progress animation
    startProgressAnimation();
    
    // Scroll to loading section
    loadingSection.scrollIntoView({ behavior: 'smooth' });
}

function startProgressAnimation() {
    let progress = 0;
    let messageIndex = 0;
    
    const interval = setInterval(() => {
        if (progress >= 100) {
            clearInterval(interval);
            return;
        }
        
        progress += Math.random() * 3 + 1; // Random increment between 1-4
        if (progress > 100) progress = 100;
        
        // Update progress bar
        progressBar.style.width = `${progress}%`;
        
        // Update message every 15% progress
        if (progress > (messageIndex + 1) * 10 && messageIndex < progressMessages.length - 1) {
            messageIndex++;
            progressText.textContent = progressMessages[messageIndex];
        }
        
        // Complete when analysis is done
        if (!isAnalyzing && progress < 100) {
            progress = 100;
            progressBar.style.width = '100%';
            progressText.textContent = 'Analysis complete!';
            clearInterval(interval);
        }
    }, 200);
}

async function performAnalysis(inputData) {
    try {
        const response = await fetch('/analysis/analyze-batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(inputData)
        });
        
        if (!response.ok) {
            throw new Error(`Analysis failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        analysisData = data.results || data;
        
        return analysisData;
        
    } catch (error) {
        console.error('Error in performAnalysis:', error);
        throw error;
    }
}

function createExecutiveSummary(inputData) {
    const executiveSummaryEl = document.getElementById('executiveSummary');
    
    // Generate a comprehensive executive summary based on the strategic question
    const summary = `
        <div class="text-slate-600 leading-relaxed">
            <p class="mb-4">
                This comprehensive strategic analysis examines "${inputData.strategic_question}" 
                within the context of ${inputData.region} over a ${inputData.time_frame} timeframe.
            </p>
            <p class="mb-4">
                Our AI-powered analysis has processed multiple dimensions of this strategic challenge, 
                including current problem structures, proven industry practices, emerging trends, 
                potential scenarios, and actionable recommendations.
            </p>
            <p class="mb-4">
                The analysis reveals key opportunities for strategic advancement while identifying 
                potential risks and mitigation strategies. High-impact initiatives have been 
                prioritized based on feasibility, resource requirements, and expected outcomes.
            </p>
            <p>
                The following sections provide detailed insights across eight strategic dimensions 
                to support informed decision-making and implementation planning.
            </p>
        </div>
    `;
    
    executiveSummaryEl.innerHTML = summary;
}

function showResults() {
    // Hide loading, show results
    loadingSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    
    // Reset button
    analyzeBtn.disabled = false;
    buttonText.textContent = 'Analyze Strategy';
    
    // Populate all sections with agent data
    populateAgentSections();
    
    // Animate sections
    animateSections();
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function populateAgentSections() {
    Object.entries(agentMapping).forEach(([agentName, config]) => {
        const sectionEl = document.getElementById(config.section);
        if (sectionEl && analysisData[agentName]) {
            const content = extractAgentContent(analysisData[agentName]);
            sectionEl.innerHTML = `<div class="text-slate-600 leading-relaxed">${content}</div>`;
        }
    });
    
    // Populate References section from Best Practices agent
    populateReferencesSection();
}

function populateReferencesSection() {
    const referencesListEl = document.getElementById('referencesList');
    if (!referencesListEl) return;
    
    // Get references from Best Practices agent
    const bestPracticesData = analysisData['Best Practices'];
    if (bestPracticesData && bestPracticesData.data && bestPracticesData.data.references) {
        const references = bestPracticesData.data.references;
        
        if (references && references.length > 0) {
            let referencesHtml = '';
            references.forEach((ref, index) => {
                const isUrl = ref.source && (ref.source.startsWith('http') || ref.source.startsWith('www'));
                
                referencesHtml += `
                    <div class="bg-brand-kodama bg-opacity-10 p-4 rounded-lg border-l-4 border-brand-lapis">
                        <div class="flex items-start">
                            <span class="inline-flex items-center justify-center w-6 h-6 bg-brand-lapis text-white rounded-full text-xs font-bold mr-3 mt-0.5">
                                ${index + 1}
                            </span>
                            <div class="flex-1">
                                <h4 class="font-brand-slab font-semibold text-brand-oxford mb-1">${ref.title}</h4>
                                <div class="text-brand-nickel text-sm">
                                    ${isUrl ? 
                                        `<a href="${ref.source}" target="_blank" rel="noopener noreferrer" class="text-brand-lapis hover:text-brand-oxford transition duration-200 underline">
                                            ${ref.source}
                                            <svg class="w-3 h-3 inline ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                            </svg>
                                        </a>` : 
                                        `<span class="font-brand-regular">${ref.source}</span>`
                                    }
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            referencesListEl.innerHTML = referencesHtml;
        } else {
            referencesListEl.innerHTML = '<p class="text-sm text-brand-nickel italic">No references were extracted from the Best Practices analysis.</p>';
        }
    } else {
        referencesListEl.innerHTML = '<p class="text-sm text-brand-nickel italic">References will appear here after Best Practices analysis completes.</p>';
    }
}

function extractAgentContent(agentData) {
    // Extract content from agent data structure
    if (agentData.data && agentData.data.formatted_output) {
        return marked.parse(agentData.data.formatted_output);
    } else if (agentData.data && typeof agentData.data === 'string') {
        return marked.parse(agentData.data);
    } else if (agentData.data && agentData.data.analysis) {
        return marked.parse(agentData.data.analysis);
    } else if (typeof agentData === 'string') {
        return marked.parse(agentData);
    } else {
        return '<p class="text-slate-500 italic">Content not available for this section.</p>';
    }
}

function animateSections() {
    const sections = document.querySelectorAll('.section-content');
    sections.forEach((section, index) => {
        setTimeout(() => {
            section.classList.add('loaded');
        }, index * 100);
    });
}

function showError(message) {
    // Hide loading
    loadingSection.classList.add('hidden');
    
    // Reset button
    analyzeBtn.disabled = false;
    buttonText.textContent = 'Analyze Strategy';
    
    // Show error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'bg-red-50 border border-red-200 rounded-lg p-6 mb-8';
    errorDiv.innerHTML = `
        <div class="flex items-center">
            <svg class="w-6 h-6 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div>
                <h3 class="text-lg font-semibold text-red-800">Analysis Error</h3>
                <p class="text-red-700">${message}</p>
            </div>
        </div>
    `;
    
    searchSection.insertAdjacentElement('afterend', errorDiv);
    
    // Remove error after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function exportToPDF() {
    if (!analysisData || Object.keys(analysisData).length === 0) {
        alert('No analysis data available to export.');
        return;
    }
    
    // Create PDF export request
    const exportData = {
        strategic_question: document.getElementById('strategic_question').value,
        time_frame: document.getElementById('time_frame').value,
        region: document.getElementById('region').value,
        additional_context: document.getElementById('prompt').value,
        analysis_data: analysisData
    };
    
    fetch('/generate-pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(exportData)
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('PDF generation failed');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'strategic-analysis.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('PDF export failed:', error);
        alert('Failed to export PDF. Please try again.');
    });
}

function exportToWord() {
    if (!analysisData || Object.keys(analysisData).length === 0) {
        alert('No analysis data available to export.');
        return;
    }
    
    // For now, create a simple HTML download that can be opened in Word
    const htmlContent = generateWordContent();
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'strategic-analysis.html';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

function generateWordContent() {
    const question = document.getElementById('strategic_question').value;
    const timeFrame = document.getElementById('time_frame').value;
    const region = document.getElementById('region').value;
    
    let content = `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Strategic Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }
                h1 { color: #003f7f; border-bottom: 3px solid #003f7f; padding-bottom: 10px; }
                h2 { color: #003f7f; margin-top: 30px; }
                .meta { background: #f5f5f5; padding: 15px; margin: 20px 0; border-left: 4px solid #003f7f; }
            </style>
        </head>
        <body>
            <h1>Strategic Intelligence Analysis Report</h1>
            <div class="meta">
                <strong>Strategic Question:</strong> ${question}<br>
                <strong>Time Frame:</strong> ${timeFrame}<br>
                <strong>Region:</strong> ${region}<br>
                <strong>Generated:</strong> ${new Date().toLocaleDateString()}
            </div>
    `;
    
    Object.entries(agentMapping).forEach(([agentName, config]) => {
        if (analysisData[agentName]) {
            content += `<h2>${config.title}</h2>`;
            content += extractAgentContent(analysisData[agentName]);
        }
    });
    
    // Add References section
    const bestPracticesData = analysisData['Best Practices'];
    if (bestPracticesData && bestPracticesData.data && bestPracticesData.data.references) {
        const references = bestPracticesData.data.references;
        if (references && references.length > 0) {
            content += `<h2>References & Sources</h2>`;
            content += `<p style="font-style: italic; margin-bottom: 10px;">Sources and references from Best Practices analysis:</p>`;
            references.forEach((ref, index) => {
                content += `
                    <div style="margin-bottom: 15px; padding: 10px; background-color: #f5f5f5; border-left: 4px solid #003f7f;">
                        <p><strong>${index + 1}. ${ref.title}</strong></p>
                        <p style="margin: 5px 0;">${ref.source}</p>
                    </div>
                `;
            });
        }
    }
    
    content += '</body></html>';
    return content;
} 