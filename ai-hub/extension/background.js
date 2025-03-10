chrome.webNavigation.onCompleted.addListener(async (details) => {
  // Get current tool and credentials
  const data = await chrome.storage.local.get(['currentTool', 'credentials', 'sessionData']);
  
  if (!data.currentTool || !data.credentials) {
    return;
  }
  
  const { currentTool, credentials, sessionData } = data;
  
  // Match URL patterns for login pages
  const isLoginPage = (
    (currentTool.name === 'claude' && details.url.includes('claude.ai/login')) ||
    (currentTool.name === 'chatgpt' && details.url.includes('chat.openai.com/auth/login')) ||
    (currentTool.name === 'perplexity' && details.url.includes('perplexity.ai/login')) ||
    (currentTool.name === 'gemini' && details.url.includes('gemini.google.com')) ||
    (currentTool.name === 'grok' && details.url.includes('grok.x.ai')) ||
    (currentTool.name === 'v0' && details.url.includes('v0.dev'))
  );
  
  if (isLoginPage) {
    // Check if we have session data for email-link based auth
    if (currentTool.auth_type === 'email_link' && sessionData) {
      // Execute content script to apply session cookies
      chrome.scripting.executeScript({
        target: { tabId: details.tabId },
        function: applySessionCookies,
        args: [sessionData]
      });
    } else {
      // Execute content script to auto-fill login credentials
      chrome.scripting.executeScript({
        target: { tabId: details.tabId },
        function: autoFillCredentials,
        args: [currentTool, credentials]
      });
    }
    
    // Clear stored credentials for security
    chrome.storage.local.remove(['credentials', 'sessionData']);
    
    // Notify the API about the usage
    try {
      await fetch('https://your-fastapi-service.com/credential/release', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          credential_id: credentials.id
        }),
      });
    } catch (error) {
      console.error('Error logging usage:', error);
    }
  }
}, {
  url: [
    { urlContains: 'claude.ai' },
    { urlContains: 'chat.openai.com' },
    { urlContains: 'gemini.google.com' },
    { urlContains: 'grok.x.ai' },
    { urlContains: 'v0.dev' },
    { urlContains: 'perplexity.ai' }
  ]
});

// Function to auto-fill credentials based on tool type
function autoFillCredentials(tool, credentials) {
  console.log(`Attempting to auto-fill for ${tool.name}`);
  
  // Delay to ensure page is fully loaded
  setTimeout(() => {
    try {
      let emailInput, passwordInput, loginButton;
      
      if (tool.name === 'claude') {
        if (tool.auth_type === 'email_link') {
          // Claude uses email-based login
          emailInput = document.querySelector('input[type="email"]');
          loginButton = document.querySelector('button[type="submit"]');
          
          if (emailInput) {
            emailInput.value = credentials.email;
            emailInput.dispatchEvent(new Event('input', { bubbles: true }));
          }
          
          // Click to send magic link
          setTimeout(() => {
            if (loginButton) {
              loginButton.click();
            }
          }, 500);
          
        } else {
          // Standard login with password
          emailInput = document.querySelector('input[type="email"]');
          passwordInput = document.querySelector('input[type="password"]');
          loginButton = document.querySelector('button[type="submit"]');
          
          if (emailInput) {
            emailInput.value = credentials.email;
            emailInput.dispatchEvent(new Event('input', { bubbles: true }));
          }
          
          if (passwordInput) {
            passwordInput.value = credentials.password;
            passwordInput.dispatchEvent(new Event('input', { bubbles: true }));
          }
          
          // Click login
          setTimeout(() => {
            if (loginButton) {
              loginButton.click();
            }
          }, 500);
        }
      } else if (tool.name === 'chatgpt') {
        emailInput = document.querySelector('input[name="username"]');
        passwordInput = document.querySelector('input[name="password"]');
        loginButton = document.querySelector('button[type="submit"]');
        
        // Handle different states of OpenAI login flow
        if (emailInput) {
          emailInput.value = credentials.email;
          emailInput.dispatchEvent(new Event('input', { bubbles: true }));
          
          // Click next/continue
          setTimeout(() => {
            if (loginButton) {
              loginButton.click();
            }
          }, 500);
        } else if (passwordInput) {
          passwordInput.value = credentials.password;
          passwordInput.dispatchEvent(new Event('input', { bubbles: true }));
          
          // Click login
          setTimeout(() => {
            if (loginButton) {
              loginButton.click();
            }
          }, 500);
        }
      } else if (tool.name === 'perplexity') {
        // Perplexity could use email link or password
        if (tool.auth_type === 'email_link') {
          emailInput = document.querySelector('input[type="email"]');
          loginButton = document.querySelector('button[type="submit"]');
          
          if (emailInput) {
            emailInput.value = credentials.email;
            emailInput.dispatchEvent(new Event('input', { bubbles: true }));
          }
          
          setTimeout(() => {
            if (loginButton) {
              loginButton.click();
            }
          }, 500);
        } else {
          emailInput = document.querySelector('input[type="email"]');
          passwordInput = document.querySelector('input[type="password"]');
          loginButton = document.querySelector('button[type="submit"]');
          
          if (emailInput) {
            emailInput.value = credentials.email;
            emailInput.dispatchEvent(new Event('input', { bubbles: true }));
          }
          
          if (passwordInput) {
            passwordInput.value = credentials.password;
            passwordInput.dispatchEvent(new Event('input', { bubbles: true }));
          }
          
          setTimeout(() => {
            if (loginButton) {
              loginButton.click();
            }
          }, 500);
        }
      }
      // Add more tool-specific login flows as needed
      
    } catch (error) {
      console.error('Error during auto-fill:', error);
    }
  }, 1000);
}

// Function to apply stored session cookies
function applySessionCookies(sessionData) {
  console.log('Applying stored session cookies');
  
  try {
    // Parse the session data (which could be cookies, localStorage items, etc.)
    const sessionInfo = JSON.parse(sessionData);
    
    // Apply cookies if present
    if (sessionInfo.cookies) {
      for (const cookie of sessionInfo.cookies) {
        document.cookie = `${cookie.name}=${cookie.value}; path=${cookie.path || '/'}; domain=${cookie.domain || window.location.hostname}; ${cookie.secure ? 'secure;' : ''} ${cookie.httpOnly ? 'httpOnly;' : ''}`;
      }
    }
    
    // Apply localStorage items if present
    if (sessionInfo.localStorage) {
      for (const [key, value] of Object.entries(sessionInfo.localStorage)) {
        window.localStorage.setItem(key, value);
      }
    }
    
    // Apply sessionStorage items if present
    if (sessionInfo.sessionStorage) {
      for (const [key, value] of Object.entries(sessionInfo.sessionStorage)) {
        window.sessionStorage.setItem(key, value);
      }
    }
    
    // Reload the page to apply the session
    setTimeout(() => {
      window.location.reload();
    }, 500);
    
  } catch (error) {
    console.error('Error applying session cookies:', error);
  }
}