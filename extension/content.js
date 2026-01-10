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

  // Track processed videos to avoid duplicates
  const processedVideos = new Set();

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
      <p class="panel-title">Avocado</p>
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
      <p class="panel-title">Avocado</p>
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

  // Get the URL of the next upcoming video
  function getNextVideoUrl() {
    // Find all video containers
    const containers = document.querySelectorAll('[data-scroll-index]');
    if (!containers.length) return null;

    // Find the currently visible container (closest to top of viewport)
    let currentIndex = null;
    for (const container of containers) {
      const rect = container.getBoundingClientRect();
      // Container is "current" if it's mostly visible in the viewport
      if (rect.top >= -rect.height / 2 && rect.top <= window.innerHeight / 2) {
        currentIndex = parseInt(container.getAttribute('data-scroll-index'), 10);
        break;
      }
    }

    if (currentIndex === null) return null;

    // Find the next container
    const nextContainer = document.querySelector(`[data-scroll-index="${currentIndex + 1}"]`);
    if (!nextContainer) return null;

    const videoWrapper = nextContainer.querySelector('[id^="xgwrapper-"]');
    const videoId = videoWrapper ? videoWrapper.id.split('-').pop() : null;

    const authorLink = nextContainer.querySelector('a[href^="/@"]');
    const author = authorLink ? authorLink.href.split('/@').pop() : null;

    return author && videoId
      ? `https://www.tiktok.com/@${author}/video/${videoId}`
      : null;
  }

  // Get the URL of the next upcoming video (Favorites/DM UI)
  function getNextVideoUrlOverlay() {
    const currentPath = window.location.pathname;

    // Try to find video links in the Favorites/Profile grid
    let links = Array.from(document.querySelectorAll('div[class*="DivItemContainerV2"] a[href*="/video/"]'));

    // Fallback to any video links if grid not found
    if (links.length === 0) {
      links = Array.from(document.querySelectorAll('a[href*="/video/"]'));
    }

    const urls = links.map(a => new URL(a.href).pathname);
    const currentIndex = urls.findIndex(path => path === currentPath);

    if (currentIndex !== -1 && currentIndex < links.length - 1) {
      const nextUrl = links[currentIndex + 1].href.split('?')[0];
      return nextUrl;
    }

    return null;
  }

  // Create fact-check button
  function createFactCheckButton() {
    // Create wrapper to match TikTok's grid structure (button + text label)
    const wrapper = document.createElement('div');
    wrapper.className = 'fact-check-wrapper';

    const button = document.createElement('button');
    button.className = 'fact-check-btn';

    // Use the avocado logo image
    const logo = document.createElement('img');
    logo.src = chrome.runtime.getURL('logo.png');
    logo.alt = 'Fact Check';
    logo.className = 'fact-check-logo';
    button.appendChild(logo);

    button.title = 'Fact Check This Video';
    button.addEventListener('click', (e) => {
      e.stopPropagation();
      e.preventDefault();

      // Log the next video URL
      const rawUrl = getNextVideoUrl();
      const nextVideoUrl = rawUrl ? rawUrl.split("?lang=en").join("") : null;
      console.log('[TikTok Fact Checker] Next video URL:', nextVideoUrl);

      openPanel();
    });

    // Empty text placeholder to match TikTok's layout (uses strong tag)
    const textPlaceholder = document.createElement('strong');
    textPlaceholder.className = 'fact-check-label';
    textPlaceholder.textContent = ''; // Empty like TikTok's structure

    wrapper.appendChild(button);
    wrapper.appendChild(textPlaceholder);

    return wrapper;
  }

  // Create fact-check button for video player overlay (Favorites/DM UI)
  function createVideoOverlayFactCheckButton() {
    const button = document.createElement('button');
    button.className = 'fact-check-btn-video-overlay';
    button.setAttribute('aria-label', 'Fact Check');

    // Use the avocado logo image
    const logo = document.createElement('img');
    logo.src = chrome.runtime.getURL('logo.png');
    logo.alt = 'Fact Check';
    logo.className = 'fact-check-logo-video-overlay';
    button.appendChild(logo);

    button.title = 'Fact Check This Video';
    button.addEventListener('click', (e) => {
      e.stopPropagation();
      e.preventDefault();

      // Log the next video URL
      const nextVideoUrl = getNextVideoUrlOverlay();
      console.log('[TikTok Fact Checker] Next video URL (Overlay UI):', nextVideoUrl);

      openPanel();
    });

    return button;
  }

  // Find and process TikTok video containers
  function processVideos() {
    // Find all action button sidebars (the column with like, comment, share, etc.)
    const sidebars = document.querySelectorAll('section[class*="SectionActionBarContainer"]');

    sidebars.forEach(sidebar => {
      // Check if button already exists in this sidebar
      if (sidebar.querySelector('.fact-check-btn')) return;

      // Create unique identifier
      const videoId = Math.random().toString(36).substr(2, 9);
      if (processedVideos.has(videoId)) return;

      // Create and prepend button (so it appears at the top, above profile pic)
      const button = createFactCheckButton();
      sidebar.prepend(button);

      processedVideos.add(videoId);
      console.log('[TikTok Fact Checker] Button added to sidebar');
    });
  }

  // Find and process video player overlay UI (Favorites/DM video player)
  function processVideoOverlayUI() {
    // Target the video container (DivVideoContainer)
    const videoContainers = document.querySelectorAll('div[class*="DivVideoContainer"]');

    videoContainers.forEach(container => {
      // Check if button already exists in this container
      if (container.querySelector('.fact-check-btn-video-overlay')) return;

      // Ensure the container has position relative for absolute positioning
      const computedStyle = getComputedStyle(container);
      if (computedStyle.position === 'static') {
        container.style.position = 'relative';
      }

      // Create and append button to the video container
      const button = createVideoOverlayFactCheckButton();
      container.appendChild(button);

      console.log('[TikTok Fact Checker] Button added to video overlay');
    });
  }

  // Initialize the extension
  function init() {
    console.log('[TikTok Fact Checker] Extension loaded');

    // Process existing videos (vertical sidebar - For You page)
    processVideos();

    // Process video overlay UI (Favorites/DM video player)
    processVideoOverlayUI();

    // Watch for new videos being loaded (infinite scroll)
    const observer = new MutationObserver((mutations) => {
      let shouldProcess = false;
      for (const mutation of mutations) {
        if (mutation.addedNodes.length > 0) {
          shouldProcess = true;
          break;
        }
      }
      if (shouldProcess) {
        processVideos();
        processVideoOverlayUI();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  // Wait for page to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();