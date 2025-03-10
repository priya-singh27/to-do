document.addEventListener('DOMContentLoaded', () => {
  const toolCards = document.querySelectorAll('.tool-card');
  const API_BASE_URL = 'http://0.0.0.0:8000';
  
  // Load all available tools from the API
  async function loadTools() {
    try {
      const response = await fetch(`${API_BASE_URL}/tool/all`);
      if (!response.ok) {
        throw new Error('Failed to load tools');
      }
      
      const tools = await response.json();
      
      // Update the tool cards with authorization type badges
      tools.forEach(tool => {
        const cardElement = document.querySelector(`.tool-card[data-tool="${tool.name}"]`);
        if (cardElement) {
          cardElement.setAttribute('data-auth-type', tool.auth_type);
          
          // Add a badge for email-link based auth
          if (tool.auth_type === 'email_link') {
            const badge = document.createElement('span');
            badge.className = 'auth-badge';
            badge.textContent = 'Email Link';
            cardElement.appendChild(badge);
          }
        }
      });
      
    } catch (error) {
      console.error('Error loading tools:', error);
    }
  }
  
  // Load tools when the page loads
  loadTools();
  
  toolCards.forEach(card => {
    card.addEventListener('click', async () => {
      const tool = card.getAttribute('data-tool');
      card.classList.add('loading');
      
      // Call the backend API to get account credentials
      try {
        const response = await fetch(`${API_BASE_URL}/credential/get`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ tool_name: tool }),
        });
        
        if (!response.ok) {
          throw new Error('Failed to get credential');
        }
        
        const data = await response.json();
        
        // Store credentials and tool info temporarily
        chrome.storage.local.set({ 
          currentTool: data.tool,
          credentials: {
            id: data.id,
            email: data.email,
            password: data.password
          }
        });
        
        // If session data is available, store it
        if (data.session_data) {
          chrome.storage.local.set({
            sessionData: data.session_data
          });
        }
        
        // Navigate to the tool's login page
        navigateToTool(tool);
        
      } catch (error) {
        console.error('Error getting credential:', error);
        card.classList.remove('loading');
        
        // Show error message
        const errorMessage = document.createElement('div');
        errorMessage.className = 'error-message';
        errorMessage.textContent = 'Failed to get credentials. Please try again later.';
        card.appendChild(errorMessage);
        
        // Remove error message after 3 seconds
        setTimeout(() => {
          errorMessage.remove();
        }, 3000);
      }
    });
  });
  
  function navigateToTool(tool) {
    const urls = {
      'claude': 'https://claude.ai/login',
      'chatgpt': 'https://chat.openai.com/auth/login',
      'gemini': 'https://gemini.google.com',
      'grok': 'https://grok.x.ai',
      'v0': 'https://v0.dev',
      'perplexity': 'https://perplexity.ai/login'
    };
    
    window.location.href = urls[tool];
  }
  
  // Add session capture button for admin use
  const adminSection = document.createElement('div');
  adminSection.className = 'admin-section';
  adminSection.innerHTML = `
    <h3>Admin Tools</h3>
    <button id="capture-session">Capture Current Session</button>
    <div id="capture-result" class="hidden">
      <p>Copy the session data below and save it in the backend:</p>
      <textarea id="session-data" rows="5"></textarea>
      <div class="button-group">
        <button id="copy-session-data">Copy</button>
        <button id="save-session-data">Save to Backend</button>
      </div>
    </div>
  `;
  
  document.querySelector('.container').appendChild(adminSection);
  
  // Capture session functionality (for admin use)
  document.getElementById('capture-session').addEventListener('click', async () => {
    // Create a popup to capture the current page's session
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // Execute content script to capture session data
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: captureSessionData
      }, (results) => {
        if (results && results[0] && results[0].result) {
          const sessionData = results[0].result;
          document.getElementById('session-data').value = JSON.stringify(sessionData, null, 2);
          document.getElementById('capture-result').classList.remove('hidden');
        }
      });
    } catch (error) {
      console.error('Error capturing session:', error);
    }
  });
  
  // Copy session data
  document.getElementById('copy-session-data').addEventListener('click', () => {
    const textarea = document.getElementById('session-data');
    textarea.select();
    document.execCommand('copy');
  });
  
  // Save session data to backend
  document.getElementById('save-session-data').addEventListener('click', async () => {
    try {
      const sessionData = document.getElementById('session-data').value;
      
      // Get the current tab to determine which tool this is for
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const url = tab.url;
      
      // Determine which tool based on URL
      let toolName = '';
      if (url.includes('claude.ai')) toolName = 'claude';
      else if (url.includes('chat.openai.com')) toolName = 'chatgpt';
      else if (url.includes('perplexity.ai')) toolName = 'perplexity';
      else if (url.includes('gemini.google.com')) toolName = 'gemini';
      else if (url.includes('grok.x.ai')) toolName = 'grok';
      else if (url.includes('v0.dev')) toolName = 'v0';
      
      if (!toolName) {
        alert('Could not determine which tool this session is for. Please navigate to an AI tool page first.');
        return;
      }
      
      // Prompt for credential ID
      const credentialId = prompt('Enter the credential ID to associate with this session:');
      if (!credentialId || isNaN(parseInt(credentialId))) {
        alert('Please enter a valid credential ID.');
        return;
      }
      
      // Save to backend
      const response = await fetch(`${API_BASE_URL}/credential/session/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tool_name: toolName,
          credential_id: parseInt(credentialId),
          session_data: sessionData,
          expires_days: 30 // Default expiry of 30 days
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to save session');
      }
      
      alert('Session saved successfully!');
      document.getElementById('capture-result').classList.add('hidden');
      
    } catch (error) {
      console.error('Error saving session:', error);
      alert(`Failed to save session: ${error.message}`);
    }
  });
});

// Function to capture session data from the current page
function captureSessionData() {
  const sessionData = {
    cookies: getCookies(),
    localStorage: getLocalStorage(),
    sessionStorage: getSessionStorage()
  };
  
  return sessionData;
  
  function getCookies() {
    return document.cookie.split(';')
      .map(cookie => {
        const parts = cookie.trim().split('=');
        return {
          name: parts[0],
          value: parts.slice(1).join('='),
          domain: window.location.hostname,
          path: '/'
        };
      });
  }
  
  function getLocalStorage() {
    const items = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      items[key] = localStorage.getItem(key);
    }
    return items;
  }
  
  function getSessionStorage() {
    const items = {};
    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i);
      items[key] = sessionStorage.getItem(key);
    }
    return items;
  }
}