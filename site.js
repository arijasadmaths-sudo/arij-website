const menuButton = document.querySelector(".menu-button");
const navigation = document.querySelector(".nav-links");

if (menuButton && navigation) {
  menuButton.addEventListener("click", () => {
    const isOpen = navigation.classList.toggle("open");
    menuButton.setAttribute("aria-expanded", String(isOpen));
  });

  navigation.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      navigation.classList.remove("open");
      menuButton.setAttribute("aria-expanded", "false");
    });
  });
}

document.querySelectorAll('a[href^="mailto:"]').forEach((link) => {
  link.addEventListener("click", () => {
    if (typeof gtag === "function") {
      gtag("event", "contact_click", {
        link_url: link.href,
        page_path: window.location.pathname,
        transport_type: "beacon"
      });
    }
  });
});
