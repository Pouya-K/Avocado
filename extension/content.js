// TikTok Fact Checker - Content Script

(function () {
  'use strict';

  // SVG Icons
  const ICONS = {
    factCheck: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
    </svg>`,
    close: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>
    </svg>`,
    link: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
    </svg>`,
    search: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
    </svg>`,
    avocado: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path fill="#568203" d="M12,2C8,2,5,6,5,12c0,6,3,10,7,10s7-4,7-10C19,6,16,2,12,2z"/>
      <path fill="#bef264" d="M12,4c-3,0-5,4-5,9c0,5,2,7,5,7s5-2,5-7C17,8,15,4,12,4z"/>
      <circle cx="12" cy="14" r="3" fill="#5C4033"/>
    </svg>`
  };

  // Panel reference
  let panel = null;
  let overlay = null;

  // Create the slide-out panel
  function createPanel() {
    // Create overlay
    overlay = document.createElement('div');
    overlay.className = 'panel-overlay';
    overlay.addEventListener('click', closePanel);
    document.body.appendChild(overlay);

    // Create panel
    panel = document.createElement('div');
    panel.className = 'fact-check-panel';
    panel.innerHTML = `
      <div class="panel-content">
        <div class="loading-state">
          <div class="spinner">${ICONS.avocado}</div>
          <p class="loading-text">Analyzing video content...</p>
        </div>
      </div>
    `;

    document.body.appendChild(panel);
  }

  // Open the panel
  function openPanel() {
    if (!panel) createPanel();

    // Show loading state
    showLoadingState();

    // Open panel with animation
    setTimeout(() => {
      panel.classList.add('open');
      overlay.classList.add('visible');
    }, 10);

    // Simulate loading and show demo results (replace with real API call later)
    setTimeout(() => {
      showDemoResults();
    }, 2000);
  }

  // Close the panel
  function closePanel() {
    if (panel) {
      panel.classList.remove('open');
      overlay.classList.remove('visible');
    }
  }

  // Show loading state
  function showLoadingState() {
    const content = panel.querySelector('.panel-content');
    content.innerHTML = `
      <div class="loading-state">
        <div class="spinner">${ICONS.avocado}</div>
        <p class="loading-text">Analyzing video content...</p>
      </div>
    `;
  }

  // Show demo results with SVG Speedometer
  function showDemoResults() {
    const content = panel.querySelector('.panel-content');
    const score = 70; // Demo score

    // Determine color based on score
    let color = '#ef4444'; // Red
    if (score >= 80) color = '#22c55e'; // Green
    else if (score >= 50) color = '#eab308'; // Yellow

    // SVG Geometry
    const radius = 85;
    const strokeWidth = 16;
    const center = 110; // ViewBox width / 2
    const circumference = Math.PI * radius;
    const dashValue = (score / 100) * circumference;

    content.innerHTML = `
      <div class="credibility-section">
        <div class="speedometer-container">
          <svg class="speedometer-svg" viewBox="0 0 220 170">
            <defs>
              <linearGradient id="grad-spectrum" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#bef264;stop-opacity:1" /> <!-- Avocado Light -->
                <stop offset="50%" style="stop-color:#4ade80;stop-opacity:1" /> <!-- Avocado Medium -->
                <stop offset="100%" style="stop-color:#15803d;stop-opacity:1" /> <!-- Avocado Dark -->
              </linearGradient>
            </defs>

            <!-- Background Arc -->
            <path d="M ${center - radius} 100 A ${radius} ${radius} 0 0 1 ${center + radius} 100" 
                  fill="none" 
                  stroke="rgba(255,255,255,0.1)" 
                  stroke-width="${strokeWidth}" 
                  stroke-linecap="round"/>
            
            <!-- Progress Arc -->
            <path d="M ${center - radius} 100 A ${radius} ${radius} 0 0 1 ${center + radius} 100" 
                  fill="none" 
                  stroke="url(#grad-spectrum)" 
                  stroke-width="${strokeWidth}" 
                  stroke-linecap="round"
                  stroke-dasharray="${dashValue}, ${circumference}"
                  class="meter-fill"/>
            
            <!-- Labels (Below the arc) -->
            <text x="${center}" y="80" text-anchor="middle" class="label-text" fill="#94a3b8">
              Reliable
            </text>
            <text x="${center}" y="130" text-anchor="middle" class="score-text" fill="#bef264">
              ${score}%
            </text>
          </svg>
      </div>

      <div class="summary-section">
        <h3 class="section-title">Claims Summary</h3>
        <p class="summary-text">
          This video makes claims about [topic]. The main assertions include 
          [claim 1] and [claim 2]. Our analysis suggests that while some 
          information is accurate, certain claims require additional verification.
        </p>
      </div>

      <div class="sources-section">
        <h3 class="section-title">Verification Sources</h3>
        <div class="sources-text-box">
          <div class="source-line">
            <span class="source-emoji">🔗</span>
            <a href="https://www.reuters.com/fact-check" target="_blank" class="source-link-text">Reuters Fact Check</a>
          </div>
          <div class="source-line">
            <span class="source-emoji">🔗</span>
            <a href="https://apnews.com/hub/ap-fact-check" target="_blank" class="source-link-text">Associated Press</a>
          </div>
          <div class="source-line">
            <span class="source-emoji">🔗</span>
            <a href="https://www.snopes.com" target="_blank" class="source-link-text">Snopes</a>
          </div>
        </div>
      </div>
    `;
  }

  // Create the fixed fact-check button
  function createFixedButton() {
    const button = document.createElement('button');
    button.className = 'fact-check-btn';
    button.innerHTML = ICONS.search;
    button.title = 'Fact Check This Video';
    button.addEventListener('click', (e) => {
      e.stopPropagation();
      e.preventDefault();
      openPanel();
    });
    document.body.appendChild(button);
    console.log('[TikTok Fact Checker] Button added to page');
  }

  // Initialize the extension
  function init() {
    console.log('[TikTok Fact Checker] Extension loaded');
    createFixedButton();
  }

  // Wait for page to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
