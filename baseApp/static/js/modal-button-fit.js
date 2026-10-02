(() => {
  const MIN_FONT_SIZE = 10;
  const HORIZONTAL_SAFE_SPACE = 24;
  const VERTICAL_SAFE_SPACE = 8;

  function fitButtonLabel(button) {
    const label = button.querySelector('.qwan-button-label');
    if (!label || button.clientWidth === 0 || button.clientHeight === 0) return;

    label.style.fontSize = '';
    let fontSize = Number.parseFloat(window.getComputedStyle(label).fontSize);
    const availableWidth = Math.max(
      0,
      button.clientWidth - HORIZONTAL_SAFE_SPACE
    );
    const availableHeight = Math.max(
      0,
      button.clientHeight - VERTICAL_SAFE_SPACE
    );

    label.style.fontSize = `${fontSize}px`;
    while (
      fontSize > MIN_FONT_SIZE
      && (
        label.scrollWidth > availableWidth
        || label.scrollHeight > availableHeight
      )
    ) {
      fontSize -= 0.5;
      label.style.fontSize = `${fontSize}px`;
    }
  }

  function initializeModalButtons() {
    const buttons = document.querySelectorAll('.qwan_button');
    if (!buttons.length) return;

    const resizeObserver = new ResizeObserver((entries) => {
      entries.forEach(({ target }) => fitButtonLabel(target));
    });

    buttons.forEach((button) => {
      resizeObserver.observe(button);
      fitButtonLabel(button);
    });
    window.addEventListener('resize', () => {
      buttons.forEach(fitButtonLabel);
    });
  }

  document.addEventListener('DOMContentLoaded', initializeModalButtons);
})();
