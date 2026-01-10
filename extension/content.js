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
      <div class="panel-header">
        <h2>
          ${ICONS.factCheck}
          Fact Check Results
        </h2>
        <button class="close-btn" aria-label="Close panel">
          ${ICONS.close}
        </button>
      </div>
      <div class="panel-content">
        <div class="loading-state">
          <div class="spinner"></div>
          <p class="loading-text">Analyzing video content...</p>
        </div>
      </div>
    `;

    // Add close button listener
    panel.querySelector('.close-btn').addEventListener('click', closePanel);

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
        <div class="spinner"></div>
        <p class="loading-text">Analyzing video content...</p>
      </div>
    `;
  }

  // Show demo results (placeholder for actual Gemini integration)
  function showDemoResults() {
    const content = panel.querySelector('.panel-content');
    content.innerHTML = `
      <div class="credibility-section">
        <div class="score-circle">
          <span class="score-value">70%</span>
        </div>
        <p class="score-label">Credibility Score</p>
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
        
        <div class="source-item">
          <div class="source-icon">${ICONS.link}</div>
          <div class="source-info">
            <p class="source-name">Reuters Fact Check</p>
            <a href="#" class="source-url">reuters.com/fact-check/...</a>
          </div>
        </div>
        
        <div class="source-item">
          <div class="source-icon">${ICONS.link}</div>
          <div class="source-info">
            <p class="source-name">Associated Press</p>
            <a href="#" class="source-url">apnews.com/article/...</a>
          </div>
        </div>
        
        <div class="source-item">
          <div class="source-icon">${ICONS.link}</div>
          <div class="source-info">
            <p class="source-name">Snopes</p>
            <a href="#" class="source-url">snopes.com/fact-check/...</a>
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
