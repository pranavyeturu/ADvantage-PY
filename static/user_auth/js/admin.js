window.addEventListener("DOMContentLoaded", () => {
    const sb = document.getElementById("snackbar");
    if (sb && sb.textContent.trim()) {
      sb.classList.add("show");
      setTimeout(() => sb.classList.remove("show"), 3000);
    }
  });
  