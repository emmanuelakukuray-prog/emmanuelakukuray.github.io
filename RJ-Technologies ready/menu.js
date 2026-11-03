const menuToggle = document.querySelector(".menu-toggle");
const mainNavigation = document.querySelector("#primary-navigation");
const siteHeader = menuToggle?.closest("header");

if (!menuToggle || !mainNavigation || !siteHeader) {
  console.error("Responsive navigation could not be initialized: required menu elements are missing.");
} else {
  const mobileViewport = window.matchMedia("(max-width: 700px)");

  const setMenuOpen = (isOpen) => {
    siteHeader.classList.toggle("nav-open", isOpen);
    menuToggle.setAttribute("aria-expanded", String(isOpen));
    menuToggle.setAttribute(
      "aria-label",
      isOpen ? "Close navigation menu" : "Open navigation menu",
    );
  };

  siteHeader.classList.add("menu-enhanced");

  menuToggle.addEventListener("click", () => {
    setMenuOpen(menuToggle.getAttribute("aria-expanded") !== "true");
  });

  mainNavigation.addEventListener("click", (event) => {
    if (event.target instanceof Element && event.target.closest("a")) {
      setMenuOpen(false);
    }
  });

  siteHeader.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menuToggle.getAttribute("aria-expanded") === "true") {
      setMenuOpen(false);
      menuToggle.focus();
    }
  });

  mobileViewport.addEventListener("change", (event) => {
    if (!event.matches) {
      setMenuOpen(false);
    }
  });
}
