function setVersionExpanded(button, expanded) {
  const line = button.nextElementSibling;
  const versionItems = line?.querySelector(".version-items");
  if (!line || !versionItems) return;

  button.classList.toggle("active_version", expanded);
  versionItems.inert = !expanded;
}

function resetExpandedContents() {
  document.querySelectorAll(".item-button").forEach((button) => {
    const content = button.nextElementSibling;

    button.classList.remove("active_content");
    if (!content) return;

    content.style.maxHeight = "0px";
    content.style.borderTop = "solid 1px #e9e9e9";
    content.style.borderBottom = "none";
    content.style.marginBottom = "-1px";
  });
}

function closeVersionContent(button) {
  const content = button?.nextElementSibling;
  if (!button || !content) return;

  button.classList.remove("active_content");
  content.style.maxHeight = "0px";
  content.style.borderTop = "solid 1px #e9e9e9";
  content.style.borderBottom = "none";
  content.style.marginBottom = "-1px";
}

function openVersionContent(button) {
  const content = button.nextElementSibling;
  if (!content) return;

  button.classList.add("active_content");
  content.style.borderTop = "none";
  content.style.borderBottom = "solid 1px #D8FDD1";
  content.style.marginBottom = "0px";
  content.style.maxHeight = `${content.scrollHeight}px`;
}

// 대단위 version toggle
function outside(element) {
  const shouldExpand = !element.classList.contains("active_version");

  resetExpandedContents();

  document.querySelectorAll(".version-button.active_version").forEach((button) => {
    setVersionExpanded(button, false);
  });

  if (shouldExpand) {
    setVersionExpanded(element, true);
  }
}

// 소단위 version toggle
function collapse(element) {
  const previous = document.querySelector(".item-button.active_content");

  if (previous === element) {
    closeVersionContent(element);
  } else {
    if (previous) closeVersionContent(previous);
    openVersionContent(element);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  resetExpandedContents();
  document.querySelectorAll('.version-button[onclick]').forEach((button) => {
    setVersionExpanded(button, false);
  });
});
window.addEventListener("resize", () => {
  const content = document.querySelector(".item-button.active_content + .content");
  if (content) {
    content.style.maxHeight = "none";
    content.style.maxHeight = `${content.scrollHeight}px`;
  }
});
