// Horizon Scanning Component
function createHorizonScanningComponent(data) {
    const container = document.createElement('div');
    container.className = 'horizon-scanning bg-white rounded-lg shadow-md p-6';

    // Weak Signals Section
    const weakSignalsSection = document.createElement('div');
    weakSignalsSection.className = 'mb-8';
    weakSignalsSection.innerHTML = `
        <h2 class="text-xl font-semibold mb-4">Weak Signals</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            ${data.weak_signals.map((signal, index) => `
                <div class="signal-card bg-gray-50 p-4 rounded-lg">
                    <h3 class="text-lg font-medium mb-2">${index + 1}. ${signal.title}</h3>
                    <div class="space-y-2">
                        <p><span class="font-medium">Domain:</span> ${signal.domain}</p>
                        <p><span class="font-medium">Date:</span> ${signal.date}</p>
                        <p><span class="font-medium">Description:</span> ${signal.description}</p>
                        <p><span class="font-medium">Evidence:</span> ${signal.evidence}</p>
                        <p><span class="font-medium">Implications:</span> ${signal.implications}</p>
                        <div class="grid grid-cols-3 gap-2">
                            <div class="metric">
                                <span class="font-medium">Impact:</span>
                                <div class="progress-bar">
                                    <div class="progress" style="width: ${(signal.impact / 10) * 100}%"></div>
                                </div>
                                <span class="text-sm">${signal.impact}/10</span>
                            </div>
                            <div class="metric">
                                <span class="font-medium">Certainty:</span>
                                <div class="progress-bar">
                                    <div class="progress" style="width: ${(signal.certainty / 10) * 100}%"></div>
                                </div>
                                <span class="text-sm">${signal.certainty}/10</span>
                            </div>
                            <div class="metric">
                                <span class="font-medium">Probability:</span>
                                <div class="progress-bar">
                                    <div class="progress" style="width: ${signal.probability * 100}%"></div>
                                </div>
                                <span class="text-sm">${signal.probability}</span>
                            </div>
                        </div>
                        <p><span class="font-medium">Time Horizon:</span> ${signal.time_horizon}</p>
                        <p><span class="font-medium">Related Signals:</span> ${signal.related_signals.join(', ')}</p>
                        <div class="tags">
                            ${signal.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                        ${signal.notes ? `<p><span class="font-medium">Notes:</span> ${signal.notes}</p>` : ''}
                        <p><span class="font-medium">Citations:</span> ${signal.citations.join(', ')}</p>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    container.appendChild(weakSignalsSection);

    // Key Uncertainties Section
    const keyUncertaintiesSection = document.createElement('div');
    keyUncertaintiesSection.className = 'mb-8';
    keyUncertaintiesSection.innerHTML = `
        <h2 class="text-xl font-semibold mb-4">Key Uncertainties</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            ${data.key_uncertainties.map((uncertainty, index) => `
                <div class="uncertainty-card bg-gray-50 p-4 rounded-lg">
                    <h3 class="text-lg font-medium mb-2">${index + 1}. ${uncertainty.title}</h3>
                    <div class="space-y-2">
                        <p><span class="font-medium">Domain:</span> ${uncertainty.domain}</p>
                        <p><span class="font-medium">Date:</span> ${uncertainty.date}</p>
                        <p><span class="font-medium">Description:</span> ${uncertainty.description}</p>
                        <p><span class="font-medium">Key Drivers:</span> ${uncertainty.key_drivers.join(', ')}</p>
                        <div class="grid grid-cols-3 gap-2">
                            <div class="metric">
                                <span class="font-medium">Impact:</span>
                                <div class="progress-bar">
                                    <div class="progress" style="width: ${(uncertainty.impact / 10) * 100}%"></div>
                                </div>
                                <span class="text-sm">${uncertainty.impact}/10</span>
                            </div>
                            <div class="metric">
                                <span class="font-medium">Certainty:</span>
                                <div class="progress-bar">
                                    <div class="progress" style="width: ${(uncertainty.certainty / 10) * 100}%"></div>
                                </div>
                                <span class="text-sm">${uncertainty.certainty}/10</span>
                            </div>
                            <div class="metric">
                                <span class="font-medium">Probability:</span>
                                <div class="progress-bar">
                                    <div class="progress" style="width: ${uncertainty.probability * 100}%"></div>
                                </div>
                                <span class="text-sm">${uncertainty.probability}</span>
                            </div>
                        </div>
                        <p><span class="font-medium">Time Horizon:</span> ${uncertainty.time_horizon}</p>
                        <p><span class="font-medium">Potential Impact Scenarios:</span> ${uncertainty.potential_impact_scenarios.join(', ')}</p>
                        <div class="tags">
                            ${uncertainty.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                        ${uncertainty.notes ? `<p><span class="font-medium">Notes:</span> ${uncertainty.notes}</p>` : ''}
                        <p><span class="font-medium">Citations:</span> ${uncertainty.citations.join(', ')}</p>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    container.appendChild(keyUncertaintiesSection);

    // Change Drivers Section
    const changeDriversSection = document.createElement('div');
    changeDriversSection.className = 'mb-8';
    changeDriversSection.innerHTML = `
        <h2 class="text-xl font-semibold mb-4">Change Drivers</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            ${Object.entries(data.change_drivers).map(([category, drivers]) => `
                <div class="driver-category bg-gray-50 p-4 rounded-lg">
                    <h3 class="text-lg font-medium mb-2">${category.charAt(0).toUpperCase() + category.slice(1)}</h3>
                    <ul class="space-y-2">
                        ${drivers.map(driver => `<li class="flex items-start">
                            <span class="bullet">•</span>
                            <span class="ml-2">${driver}</span>
                        </li>`).join('')}
                    </ul>
                </div>
            `).join('')}
        </div>
    `;
    container.appendChild(changeDriversSection);

    return container;
}

// Add styles
const styles = `
    .horizon-scanning {
        font-family: system-ui, -apple-system, sans-serif;
    }

    .signal-card, .uncertainty-card, .driver-category {
        transition: transform 0.2s;
    }

    .signal-card:hover, .uncertainty-card:hover, .driver-category:hover {
        transform: translateY(-2px);
    }

    .progress-bar {
        width: 100%;
        height: 8px;
        background-color: #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
        margin: 4px 0;
    }

    .progress {
        height: 100%;
        background-color: #4f46e5;
        transition: width 0.3s ease;
    }

    .metric {
        text-align: center;
    }

    .tags {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        margin-top: 8px;
    }

    .tag {
        background-color: #e5e7eb;
        color: #374151;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.875rem;
    }

    .bullet {
        color: #4f46e5;
        font-size: 1.25rem;
        line-height: 1;
    }
`;

// Add styles to document
const styleSheet = document.createElement('style');
styleSheet.textContent = styles;
document.head.appendChild(styleSheet);

// Export the component
export { createHorizonScanningComponent }; 