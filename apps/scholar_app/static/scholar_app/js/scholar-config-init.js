/**
 * Scholar Configuration Initializer
 * Reads configuration from data attributes and sets up global config
 */

import { initScholarConfig } from '../ts/scholar-config.js';

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
  const configElement = document.getElementById('scholar-config-data');

  if (!configElement) {
    console.warn('[Scholar] Config data element not found');
    return;
  }

  try {
    // Parse configuration from data attributes
    const config = {
      urls: {
        bibtexUpload: configElement.dataset.bibtexUploadUrl || '',
        resourceStatus: configElement.dataset.resourceStatusUrl || '',
        scitexSearch: configElement.dataset.scitexSearchUrl || '',
        scitexCapabilities: configElement.dataset.scitexCapabilitiesUrl || ''
      },
      user: {
        isAuthenticated: configElement.dataset.userAuthenticated === 'true'
      },
      userProjects: JSON.parse(configElement.dataset.userProjects || '[]'),
      currentProject: JSON.parse(configElement.dataset.currentProject || 'null')
    };

    // Add search results if present
    if (configElement.dataset.searchResults) {
      config.searchResults = JSON.parse(configElement.dataset.searchResults);
    }

    // Initialize configuration
    initScholarConfig(config);

    console.log('[Scholar] Configuration initialized', {
      authenticated: config.user.isAuthenticated,
      projectCount: config.userProjects.length,
      hasCurrentProject: !!config.currentProject,
      hasSearchResults: !!config.searchResults
    });
  } catch (error) {
    console.error('[Scholar] Failed to initialize configuration:', error);
  }
});
