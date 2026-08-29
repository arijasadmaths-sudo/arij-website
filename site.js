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

const copyButton = document.querySelector("#copy-email");
const copyStatus = document.querySelector("#copy-status");

if (copyButton && copyStatus) {
  copyButton.addEventListener("click", async () => {
    const emailAddress = "arijasadmaths@gmail.com";

    try {
      await navigator.clipboard.writeText(emailAddress);
      copyStatus.textContent = "Email address copied.";
    } catch (error) {
      copyStatus.textContent = "Please copy manually: " + emailAddress;
    }
  });
}

(() => {
  const consentKey = "arij_maths_analytics_consent";
  const analyticsId = "G-8D2Z5HRSR5";
  let analyticsLoaded = false;

  const getConsent = () => {
    try {
      return window.localStorage.getItem(consentKey);
    } catch (error) {
      return null;
    }
  };

  const saveConsent = (value) => {
    try {
      window.localStorage.setItem(consentKey, value);
    } catch (error) {
      // The choice will apply for this page view if storage is unavailable.
    }
  };

  const loadAnalytics = () => {
    if (analyticsLoaded || document.querySelector("script[data-arij-analytics]")) {
      return;
    }

    analyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () {
      window.dataLayer.push(arguments);
    };

    window.gtag("consent", "default", {
      analytics_storage: "granted",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied"
    });
    window.gtag("js", new Date());
    window.gtag("config", analyticsId);

    const script = document.createElement("script");
    script.async = true;
    script.dataset.arijAnalytics = "true";
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(analyticsId);
    document.head.appendChild(script);
  };

  const closeBanner = () => {
    document.querySelector(".cookie-banner")?.remove();
  };

  const showBanner = () => {
    closeBanner();

    const banner = document.createElement("section");
    banner.className = "cookie-banner";
    banner.setAttribute("role", "region");
    banner.setAttribute("aria-label", "Cookie choices");
    banner.innerHTML = `
      <div class="cookie-banner__copy">
        <strong>Choose your cookie settings</strong>
        <p>This site uses essential browser storage and, only with your permission, Google Analytics to understand which pages are useful. <a href="privacy.html">Read the privacy notice</a>.</p>
      </div>
      <div class="cookie-banner__actions">
        <button class="cookie-button cookie-button--secondary" type="button" data-cookie-reject>Reject analytics</button>
        <button class="cookie-button cookie-button--primary" type="button" data-cookie-accept>Accept analytics</button>
      </div>
    `;

    banner.querySelector("[data-cookie-accept]").addEventListener("click", () => {
      saveConsent("accepted");
      loadAnalytics();
      closeBanner();
    });

    banner.querySelector("[data-cookie-reject]").addEventListener("click", () => {
      saveConsent("rejected");
      closeBanner();
    });

    document.body.appendChild(banner);
    banner.querySelector("[data-cookie-accept]").focus();
  };

  document.querySelectorAll("[data-cookie-settings]").forEach((button) => {
    button.addEventListener("click", showBanner);
  });

  const consent = getConsent();
  if (consent === "accepted") {
    loadAnalytics();
  } else if (consent !== "rejected") {
    showBanner();
  }

  document.querySelectorAll('a[href^="mailto:"]').forEach((link) => {
    link.addEventListener("click", () => {
      if (typeof window.gtag === "function") {
        window.gtag("event", "contact_click", {
          link_url: link.href,
          page_path: window.location.pathname,
          transport_type: "beacon"
        });
      }
    });
  });
})();
