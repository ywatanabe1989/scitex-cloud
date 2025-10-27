/**
 * Code Block Copy Button Handler
 * Adds copy-to-clipboard functionality to all code blocks
 */

document.addEventListener('DOMContentLoaded', function() {
  // Find all pre elements with code blocks
  const preElements = document.querySelectorAll('pre code');

  preElements.forEach(function(codeBlock) {
    const preElement = codeBlock.parentElement;

    // Skip if copy button already exists
    if (preElement.querySelector('.code-copy-button')) {
      return;
    }

    // Create copy button with SVG icon
    const copyButton = document.createElement('button');
    copyButton.className = 'code-copy-button';
    copyButton.setAttribute('aria-label', 'Copy code to clipboard');

    // SVG clipboard icon
    const copyIcon = `
      <svg class="copy-icon" viewBox="0 0 16 16" fill="currentColor">
        <path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"/>
        <path d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3z"/>
      </svg>
    `;

    const checkIcon = `
      <svg class="check-icon" viewBox="0 0 16 16" fill="currentColor">
        <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/>
      </svg>
    `;

    copyButton.innerHTML = copyIcon;

    // Add click handler
    copyButton.addEventListener('click', function(e) {
      e.preventDefault();

      // Get the code text
      const codeText = codeBlock.textContent;

      // Copy to clipboard
      navigator.clipboard.writeText(codeText).then(function() {
        // Show success state
        copyButton.classList.add('copied');
        copyButton.innerHTML = checkIcon;

        // Reset after 2 seconds
        setTimeout(function() {
          copyButton.classList.remove('copied');
          copyButton.innerHTML = copyIcon;
        }, 2000);
      }).catch(function(err) {
        console.error('Failed to copy code:', err);
        copyButton.classList.add('error');
        setTimeout(function() {
          copyButton.classList.remove('error');
          copyButton.innerHTML = copyIcon;
        }, 2000);
      });
    });

    // Insert button into the pre element
    preElement.insertBefore(copyButton, codeBlock);

    // Handle Ctrl+A to select only code content
    preElement.addEventListener('keydown', function(e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
        e.preventDefault();

        // Select only the code element's content
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(codeBlock);
        selection.removeAllRanges();
        selection.addRange(range);
      }
    });
  });
});
