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

const serviceSelect = document.querySelector("#service");

if (serviceSelect) {
  const requestedService = new URLSearchParams(window.location.search).get("service");
  const matchingOption = Array.from(serviceSelect.options).find(
    (option) => option.textContent.trim() === requestedService
  );

  if (matchingOption) {
    serviceSelect.value = matchingOption.value;
  }
}

(() => {
  const consentKey = "arij_maths_analytics_consent";
  const analyticsId = "G-8D2Z5HRSR5";
  const analyticsDisableKey = "ga-disable-" + analyticsId;
  const leadEventKey = "arij_maths_lead_recorded";
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

  const removeAnalyticsCookies = () => {
    const cookieNames = document.cookie
      .split(";")
      .map((cookie) => cookie.split("=")[0].trim())
      .filter((name) => name === "_ga" || name.startsWith("_ga_"));

    cookieNames.forEach((name) => {
      const expiry = name + "=; Max-Age=0; path=/; SameSite=Lax";
      document.cookie = expiry;
      document.cookie = expiry + "; domain=maths.arijasad.com";
      document.cookie = expiry + "; domain=.arijasad.com";
    });
  };

  const recordLeadConversion = () => {
    if (!document.body?.hasAttribute("data-enquiry-confirmation") || typeof window.gtag !== "function") {
      return;
    }

    try {
      if (window.sessionStorage.getItem(leadEventKey) === "true") {
        return;
      }
      window.sessionStorage.setItem(leadEventKey, "true");
    } catch (error) {
      // Continue without duplicate protection if session storage is unavailable.
    }

    window.gtag("event", "generate_lead", {
      method: "website_form",
      page_path: window.location.pathname,
      transport_type: "beacon"
    });
  };

  const disableAnalytics = () => {
    window[analyticsDisableKey] = true;

    if (typeof window.gtag === "function") {
      window.gtag("consent", "update", {
        analytics_storage: "denied",
        ad_storage: "denied",
        ad_user_data: "denied",
        ad_personalization: "denied"
      });
    }

    document.querySelector("script[data-arij-analytics]")?.remove();
    analyticsLoaded = false;
    removeAnalyticsCookies();
  };

  const loadAnalytics = () => {
    if (analyticsLoaded || document.querySelector("script[data-arij-analytics]")) {
      return;
    }

    window[analyticsDisableKey] = false;
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
    recordLeadConversion();

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
    banner.setAttribute("aria-labelledby", "cookie-banner-title");
    banner.innerHTML = `
      <div class="cookie-banner__copy">
        <strong id="cookie-banner-title" tabindex="-1">Choose your cookie settings</strong>
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
      disableAnalytics();
      closeBanner();
    });

    document.body.appendChild(banner);
    banner.querySelector("#cookie-banner-title").focus();
  };

  document.querySelectorAll("[data-cookie-settings]").forEach((button) => {
    button.addEventListener("click", showBanner);
  });

  const consent = getConsent();
  if (consent === "accepted") {
    loadAnalytics();
  } else if (consent === "rejected") {
    disableAnalytics();
  } else {
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
