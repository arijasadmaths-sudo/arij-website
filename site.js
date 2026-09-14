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
  const pendingKey = "arij_maths_pending_enquiry_v2";
  const resourceSourceKey = "arij_maths_enquiry_source";
  const returnParameter = "enquiry_return";
  const recordLifetime = 15 * 60 * 1000;
  const resourcePaths = new Set([
    "/resources.html", "/tmua-paper-archive.html", "/tmua-past-papers.html",
    "/mat-past-papers.html", "/step-past-papers.html", "/esat-paper-archive.html",
    "/jmc-past-papers.html", "/imc-past-papers.html", "/smc-past-papers.html",
    "/amc10-past-papers.html", "/amc12-past-papers.html", "/aime-past-papers.html",
    "/bmo-past-papers.html", "/edexcel-textbook-companions.html",
    "/edexcel-pure-year-1.html", "/edexcel-pure-year-2.html",
    "/edexcel-statistics-mechanics-year-1.html", "/edexcel-statistics-mechanics-year-2.html",
    "/edexcel-core-pure-1.html", "/edexcel-core-pure-2.html", "/maths-topic-practice.html",
    "/algebra-and-factorisation.html", "/modulus-and-graphs.html", "/counting-and-overlap.html",
    "/geometry-and-trigonometry.html", "/calculus-and-graph-sketches.html", "/sequences-and-series.html",
    "/tmua-study-plan.html", "/tmua-logic-proof.html", "/strong-step-solution.html",
    "/when-to-start-step.html", "/cambridge-maths-interview-guide.html",
    "/cambridge-interview-problems.html", "/algebra-to-tmua-diagnostic.html",
    "/teaching-practice-sequences.html"
  ]);
  let analyticsLoaded = false;
  let confirmedReturn = null;
  let consentChoice = null;

  const getConsent = () => {
    try { return window.localStorage.getItem(consentKey); }
    catch (error) { return null; }
  };
  const saveConsent = (value) => {
    try { window.localStorage.setItem(consentKey, value); }
    catch (error) { /* The choice still applies to this page. */ }
  };
  const removeRecord = (key) => {
    try { window.sessionStorage.removeItem(key); }
    catch (error) { /* Storage may be disabled. */ }
  };
  const readRecord = (key) => {
    try { return JSON.parse(window.sessionStorage.getItem(key)); }
    catch (error) { return null; }
  };
  const isFresh = (record) => Boolean(record && Number.isFinite(record.createdAt) &&
    Date.now() >= record.createdAt && Date.now() - record.createdAt < recordLifetime);
  const clearPendingMeasurement = () => {
    confirmedReturn = null;
    removeRecord(pendingKey);
    removeRecord(resourceSourceKey);
  };

  // Strip the random return reference before any analytics script can load.
  const cleanPageUrl = new URL(window.location.href);
  const returnToken = cleanPageUrl.searchParams.get(returnParameter);
  if (cleanPageUrl.searchParams.has(returnParameter)) {
    cleanPageUrl.searchParams.delete(returnParameter);
    try { window.history.replaceState(window.history.state, "", cleanPageUrl.href); }
    catch (error) { /* GA receives the clean URL explicitly below. */ }
  }
  consentChoice = getConsent();
  if (document.body?.hasAttribute("data-enquiry-confirmation")) {
    const pending = readRecord(pendingKey);
    // Fail closed if this browser cannot consume the record exactly once.
    let consumed = false;
    try {
      window.sessionStorage.removeItem(pendingKey);
      consumed = window.sessionStorage.getItem(pendingKey) === null;
    } catch (error) { /* A direct visit or unavailable storage is not a conversion. */ }
    if (consumed && /^[a-f0-9]{32}$/.test(returnToken || "") &&
        isFresh(pending) && pending.id === returnToken) {
      const heading = document.querySelector("[data-enquiry-heading]");
      const message = document.querySelector("[data-enquiry-message]");
      if (heading) heading.textContent = "Thank you — your enquiry has been submitted.";
      if (message) message.textContent = "I’ll review your details and reply as soon as I can.";
      if (pending.analyticsEligible === true && consentChoice !== "rejected") {
        confirmedReturn = pending;
      }
    }
  }

  const removeAnalyticsCookies = () => {
    document.cookie.split(";").map((cookie) => cookie.split("=")[0].trim())
      .filter((name) => name === "_ga" || name.startsWith("_ga_"))
      .forEach((name) => {
        const expiry = name + "=; Max-Age=0; path=/; SameSite=Lax";
        document.cookie = expiry;
        document.cookie = expiry + "; domain=maths.arijasad.com";
        document.cookie = expiry + "; domain=.arijasad.com";
      });
  };
  const canMeasure = () => consentChoice === "accepted" &&
    window[analyticsDisableKey] !== true && typeof window.gtag === "function";
  const recordLeadConversion = () => {
    if (!canMeasure() || !isFresh(confirmedReturn)) return;
    const record = confirmedReturn;
    confirmedReturn = null;
    const parameters = {
      method: "website_form",
      confirmation_type: "provider_return",
      page_path: window.location.pathname,
      transport_type: "beacon"
    };
    if (resourcePaths.has(record.resourceSource)) parameters.resource_source = record.resourceSource;
    window.gtag("event", "generate_lead", parameters);
  };
  const disableAnalytics = () => {
    clearPendingMeasurement();
    window[analyticsDisableKey] = true;
    if (typeof window.gtag === "function") {
      window.gtag("consent", "update", {
        analytics_storage: "denied", ad_storage: "denied",
        ad_user_data: "denied", ad_personalization: "denied"
      });
    }
    document.querySelector("script[data-arij-analytics]")?.remove();
    analyticsLoaded = false;
    removeAnalyticsCookies();
  };
  const loadAnalytics = () => {
    if (consentChoice !== "accepted") return;
    window[analyticsDisableKey] = false;
    window.dataLayer = window.dataLayer || [];
    if (typeof window.gtag !== "function") {
      window.gtag = function () { window.dataLayer.push(arguments); };
    }
    // An explicit update also restores collection after consent was withdrawn.
    window.gtag("consent", "update", {
      analytics_storage: "granted", ad_storage: "denied",
      ad_user_data: "denied", ad_personalization: "denied"
    });
    if (!analyticsLoaded && !document.querySelector("script[data-arij-analytics]")) {
      analyticsLoaded = true;
      window.gtag("js", new Date());
      window.gtag("config", analyticsId, { page_location: cleanPageUrl.href });
      const script = document.createElement("script");
      script.async = true;
      script.dataset.arijAnalytics = "true";
      script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(analyticsId);
      document.head.appendChild(script);
    }
    recordLeadConversion();
  };

  const enquiryForm = document.querySelector("#enquiry-form-fields");
  const nextInput = enquiryForm?.querySelector('[name="_next"]');
  if (enquiryForm && nextInput) {
    const originalNext = nextInput.value;
    // Listen at the end of bubbling so a form-level cancellation is respected.
    document.addEventListener("submit", (event) => {
      if (event.target !== enquiryForm) return;
      nextInput.value = originalNext;
      removeRecord(pendingKey);
      if (event.defaultPrevented || !enquiryForm.checkValidity() ||
          enquiryForm.querySelector('[name="_honey"]')?.value.trim()) return;
      try {
        const bytes = new Uint8Array(16);
        window.crypto.getRandomValues(bytes);
        const id = Array.from(bytes, (value) => value.toString(16).padStart(2, "0")).join("");
        const record = { id, createdAt: Date.now(), analyticsEligible: consentChoice !== "rejected" };
        const source = readRecord(resourceSourceKey);
        if (consentChoice === "accepted" && isFresh(source) && resourcePaths.has(source.path)) {
          record.resourceSource = source.path;
        }
        window.sessionStorage.setItem(pendingKey, JSON.stringify(record));
        const returnUrl = new URL(originalNext, window.location.href);
        returnUrl.searchParams.set(returnParameter, id);
        nextInput.value = returnUrl.href;
      } catch (error) {
        removeRecord(pendingKey);
        // Keep the provider's ordinary return address and native form submission.
      }
      removeRecord(resourceSourceKey);
    });
  }
  const closeBanner = () => {
    document.querySelector(".cookie-banner")?.remove();
  };

  const showBanner = () => {
    closeBanner();

    const isChinese = document.documentElement.lang.toLowerCase().startsWith("zh");
    const copy = isChinese ? {
      title: "选择 Cookie 设置",
      description: "本网站使用必要的浏览器存储功能，并且仅在获得您的同意后，使用 Google Analytics 了解哪些页面对访客有帮助。",
      privacy: "阅读隐私声明（英文）",
      reject: "拒绝分析 Cookie",
      accept: "接受分析 Cookie"
    } : {
      title: "Choose your cookie settings",
      description: "This site uses essential browser storage and, only with your permission, Google Analytics to understand which pages are useful.",
      privacy: "Read the privacy notice",
      reject: "Reject analytics",
      accept: "Accept analytics"
    };
    const banner = document.createElement("section");
    banner.className = "cookie-banner";
    banner.lang = isChinese ? "zh-CN" : "en-GB";
    banner.setAttribute("role", "region");
    banner.setAttribute("aria-labelledby", "cookie-banner-title");
    banner.innerHTML = `
      <div class="cookie-banner__copy">
        <strong id="cookie-banner-title" tabindex="-1">${copy.title}</strong>
        <p>${copy.description} <a href="privacy.html" hreflang="en">${copy.privacy}</a>${isChinese ? "。" : "."}</p>
      </div>
      <div class="cookie-banner__actions">
        <button class="cookie-button cookie-button--secondary" type="button" data-cookie-reject>${copy.reject}</button>
        <button class="cookie-button cookie-button--primary" type="button" data-cookie-accept>${copy.accept}</button>
      </div>
    `;

    banner.querySelector("[data-cookie-accept]").addEventListener("click", () => {
      consentChoice = "accepted";
      saveConsent(consentChoice);
      loadAnalytics();
      closeBanner();
    });

    banner.querySelector("[data-cookie-reject]").addEventListener("click", () => {
      consentChoice = "rejected";
      saveConsent(consentChoice);
      disableAnalytics();
      closeBanner();
    });

    document.body.appendChild(banner);
    banner.querySelector("#cookie-banner-title").focus();
  };

  document.querySelectorAll("[data-cookie-settings]").forEach((button) => {
    button.addEventListener("click", showBanner);
  });

  if (consentChoice === "accepted") {
    loadAnalytics();
  } else if (consentChoice === "rejected") {
    disableAnalytics();
  } else {
    showBanner();
  }

  window.addEventListener("storage", (event) => {
    if (event.key !== consentKey && event.key !== null) return;
    consentChoice = getConsent();
    if (consentChoice === "accepted") {
      loadAnalytics();
      closeBanner();
    } else {
      disableAnalytics();
      if (consentChoice === "rejected") closeBanner();
      else showBanner();
    }
  });

  document.querySelectorAll('a[href^="mailto:"]').forEach((link) => {
    link.addEventListener("click", () => {
      if (!canMeasure()) return;
      window.gtag("event", "contact_click", {
        link_url: link.href.split("?")[0],
        page_path: window.location.pathname,
        transport_type: "beacon"
      });
    });
  });

  if (resourcePaths.has(window.location.pathname)) {
    document.querySelectorAll("a[href]").forEach((link) => {
      let target;
      try { target = new URL(link.href, window.location.href); }
      catch (error) { return; }
      if (target.origin !== window.location.origin || target.pathname !== "/contact.html") return;
      link.addEventListener("click", () => {
        if (!canMeasure()) return;
        try {
          window.sessionStorage.setItem(resourceSourceKey,
            JSON.stringify({ path: window.location.pathname, createdAt: Date.now() }));
        } catch (error) { /* The click can be counted without retaining attribution. */ }
        window.gtag("event", "resource_enquiry_click", {
          resource_source: window.location.pathname,
          page_path: window.location.pathname,
          transport_type: "beacon"
        });
      });
    });
  }
})();
