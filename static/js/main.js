/**
 * KING GREATMAN SPIRIT — Portfolio Enhancements
 * Scroll progress, preloader, particles, typed roles, counters,
 * skill bars, isotope, glightbox, swiper, scrollspy.
 */
(function () {
  "use strict";

  /* ---------- Preloader ---------- */
  const preloader = document.querySelector("#preloader");
  if (preloader) {
    const TAGLINES = [
      "Building digital experiences",
      "Crafting brilliance…",
      "Turning ideas into reality",
      "Preparing your journey…",
      "Almost there — stay tuned",
      "Loading the magic",
    ];
    const taglineEl = document.getElementById("preloader-tagline");
    let tagIdx = 0;
    const rotateTagline = () => {
      if (!taglineEl) return;
      taglineEl.classList.add("switching");
      setTimeout(() => {
        tagIdx = (tagIdx + 1) % TAGLINES.length;
        taglineEl.textContent = TAGLINES[tagIdx];
        taglineEl.classList.remove("switching");
      }, 450);
    };
    const tagTimer = setInterval(rotateTagline, 1800);

    window.addEventListener("load", () => {
      clearInterval(tagTimer);
      preloader.style.opacity = "0";
      preloader.style.visibility = "hidden";
      setTimeout(() => preloader.remove(), 600);
    });
  }

  /* ---------- Scroll progress bar ---------- */
  const progressBar = document.querySelector(".scroll-progress");
  if (progressBar) {
    const updateProgress = () => {
      const scrollable = document.documentElement.scrollHeight - window.innerHeight;
      const pct = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
      progressBar.style.width = pct + "%";
    };
    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("load", updateProgress);
  }

  /* ---------- Header toggle (mobile sidebar) ---------- */
  const headerToggleBtn = document.querySelector(".header-toggle");
  if (headerToggleBtn) {
    const header = document.querySelector("#header");
    headerToggleBtn.addEventListener("click", () => {
      header.classList.toggle("header-show");
      headerToggleBtn.classList.toggle("bi-list");
      headerToggleBtn.classList.toggle("bi-x");
    });

    document.querySelectorAll("#navmenu a").forEach((link) => {
      link.addEventListener("click", () => {
        if (header.classList.contains("header-show")) {
          header.classList.remove("header-show");
          headerToggleBtn.classList.add("bi-list");
          headerToggleBtn.classList.remove("bi-x");
        }
      });
    });
  }

  /* ---------- Scroll top button ---------- */
  const scrollTop = document.querySelector(".scroll-top");
  if (scrollTop) {
    const toggleScrollTop = () => {
      window.scrollY > 100
        ? scrollTop.classList.add("active")
        : scrollTop.classList.remove("active");
    };
    window.addEventListener("load", toggleScrollTop);
    window.addEventListener("scroll", toggleScrollTop, { passive: true });
    scrollTop.addEventListener("click", (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ---------- AOS init ---------- */
  const aosInit = () => {
    AOS.init({ duration: 800, easing: "ease-in-out", once: true, mirror: false, offset: 60 });
  };
  window.addEventListener("load", aosInit);

  /* ---------- Typed.js ---------- */
  const selectTyped = document.querySelector(".typed");
  if (selectTyped) {
    const typedStrings = selectTyped
      .getAttribute("data-typed-items")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    if (typeof Typed !== "undefined") {
      new Typed(".typed", {
        strings: typedStrings,
        loop: true,
        typeSpeed: 70,
        backSpeed: 35,
        backDelay: 1800,
        startDelay: 400,
      });
    }
  }

  /* ---------- Pure Counter (scroll-triggered) ---------- */
  document.querySelectorAll(".purecounter").forEach((el) => {
    const target = parseInt(el.getAttribute("data-purecounter-end"), 10) || 0;
    const duration = (parseFloat(el.getAttribute("data-purecounter-duration")) || 1.5) * 1000;
    const start = performance.now();
    const step = (now) => {
      const pct = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - pct, 3);
      el.textContent = Math.round(target * eased).toLocaleString();
      if (pct < 1) requestAnimationFrame(step);
    };
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              requestAnimationFrame(step);
              io.disconnect();
            }
          });
        },
        { threshold: 0.35 }
      );
      io.observe(el);
    } else {
      requestAnimationFrame(step);
    }
  });

  /* ---------- Skill bars ---------- */
  document.querySelectorAll(".skills-animation").forEach((item) => {
    if (typeof Waypoint !== "undefined") {
      new Waypoint({
        element: item,
        offset: "85%",
        handler: () => {
          item.querySelectorAll(".progress-bar").forEach((el) => {
            el.style.width = el.getAttribute("aria-valuenow") + "%";
          });
        },
      });
    } else {
      item.querySelectorAll(".progress-bar").forEach((el) => {
        el.style.width = el.getAttribute("aria-valuenow") + "%";
      });
    }
  });

  /* ---------- GLightbox ---------- */
  if (typeof GLightbox !== "undefined") {
    GLightbox({ selector: ".glightbox", touchNavigation: true, loop: true });
  }

  /* ---------- Isotope layout + filters ---------- */
  document.querySelectorAll(".isotope-layout").forEach((isotopeItem) => {
    const layout = isotopeItem.getAttribute("data-layout") || "masonry";
    const filter = isotopeItem.getAttribute("data-default-filter") || "*";
    const sort = isotopeItem.getAttribute("data-sort") || "original-order";

    let initIsotope;
    if (typeof imagesLoaded !== "undefined" && typeof Isotope !== "undefined") {
      imagesLoaded(isotopeItem.querySelector(".isotope-container"), () => {
        initIsotope = new Isotope(isotopeItem.querySelector(".isotope-container"), {
          itemSelector: ".isotope-item",
          layoutMode: layout,
          filter: filter,
          sortBy: sort,
        });
      });

      isotopeItem.querySelectorAll(".isotope-filters li").forEach((filters) => {
        filters.addEventListener("click", function () {
          isotopeItem
            .querySelector(".isotope-filters .filter-active")
            .classList.remove("filter-active");
          this.classList.add("filter-active");
          initIsotope.arrange({ filter: this.getAttribute("data-filter") });
          if (typeof aosInit === "function") aosInit();
        });
      });
    }
  });

  /* ---------- Swiper ---------- */
  const initSwiper = () => {
    document.querySelectorAll(".init-swiper").forEach((swiperElement) => {
      const config = JSON.parse(
        swiperElement.querySelector(".swiper-config").innerHTML.trim()
      );
      if (typeof Swiper !== "undefined") new Swiper(swiperElement, config);
    });
  };
  window.addEventListener("load", initSwiper);

  /* ---------- Navmenu scrollspy ---------- */
  const navmenulinks = document.querySelectorAll(".navmenu a");
  const navmenuScrollspy = () => {
    navmenulinks.forEach((navmenulink) => {
      if (!navmenulink.hash) return;
      const section = document.querySelector(navmenulink.hash);
      if (!section) return;
      const position = window.scrollY + 220;
      if (position >= section.offsetTop && position <= section.offsetTop + section.offsetHeight) {
        document.querySelectorAll(".navmenu a.active").forEach((l) => l.classList.remove("active"));
        navmenulink.classList.add("active");
      }
    });
  };
  window.addEventListener("load", navmenuScrollspy);
  window.addEventListener("scroll", navmenuScrollspy, { passive: true });

  /* ---------- Hero particles ---------- */
  const hero = document.querySelector(".hero");
  if (hero) {
    const canvas = document.createElement("canvas");
    canvas.className = "hero-canvas";
    canvas.style.cssText =
      "position:absolute;inset:0;z-index:1;pointer-events:none;width:100%;height:100%;";
    hero.appendChild(canvas);
    const ctx = canvas.getContext("2d");
    let particles = [];
    let running = true;

    const resize = () => {
      canvas.width = hero.offsetWidth;
      canvas.height = hero.offsetHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const createParticle = (initial) => ({
      x: Math.random() * canvas.width,
      y: initial ? Math.random() * canvas.height : canvas.height + 10,
      r: 1 + Math.random() * 2.2,
      speed: 0.25 + Math.random() * 0.7,
      drift: (Math.random() - 0.5) * 0.35,
      gold: Math.random() > 0.35,
      alpha: 0.25 + Math.random() * 0.5,
    });

    for (let i = 0; i < 46; i++) particles.push(createParticle(true));

    const draw = () => {
      if (!running) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach((p) => {
        p.y -= p.speed;
        p.x += p.drift + Math.sin(p.y * 0.01) * 0.15;
        if (p.y < -10) {
          Object.assign(p, createParticle(false), { y: canvas.height + 10 });
        }
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.gold
          ? "rgba(255,216,1," + p.alpha * 0.5 + ")"
          : "rgba(45,212,191," + p.alpha * 0.45 + ")";
        ctx.fill();
      });
      requestAnimationFrame(draw);
    };
    draw();

    /* Hero profile 3D tilt */
    const profile = hero.querySelector(".hero-profile");
    if (profile) {
      hero.addEventListener("mousemove", (e) => {
        const rect = profile.getBoundingClientRect();
        const x = (e.clientX - rect.left - rect.width / 2) / rect.width;
        const y = (e.clientY - rect.top - rect.height / 2) / rect.height;
        profile.style.transition = "transform 0.15s ease-out";
        profile.style.transform =
          "perspective(900px) rotateY(" + x * 8 + "deg) rotateX(" + -y * 8 + "deg)";
      });
      hero.addEventListener("mouseleave", () => {
        profile.style.transition = "transform 0.7s ease";
        profile.style.transform = "perspective(900px) rotateY(0deg) rotateX(0deg)";
      });
    }
  }

  /* ---------- Smooth anchor scrolling ---------- */
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (e) => {
      const targetId = anchor.getAttribute("href");
      if (targetId.length < 2) return;
      const target = document.querySelector(targetId);
      if (!target) return;
      e.preventDefault();
      const offset = target.getBoundingClientRect().top + window.scrollY - 16;
      window.scrollTo({ top: offset, behavior: "smooth" });
      history.replaceState(null, "", targetId);
    });
  });

  /* =========================================================
     STRICT FORM VALIDATION + AUTO-CORRECT
     Mirrors contact/validation.py on the client side.
     ========================================================= */
  const NAME_RE = /^[A-Za-z\u00C0-\u00FF' .-]{2,60}$/;
  const EMAIL_RE = /^[A-Za-z0-9._%+\-]{2,64}@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/;
  const PHONE_RE = /^\+?[0-9]{7,15}$/;
  const REPEAT_RE = /(.)\1{2,}/;
  const REPEAT_WORD_RE = /\b(\w{2,})\b\s+\1\b/i;
  const KEYBOARD_RE = /(asdf|qwerty|zxcv|tyui|fghj|hjkl|poiu|lkj|mnbvc|xswq|zaq1)/i;
  const VOWEL_RE = /[aeiouy]/i;
  const PUNCT_RE = /[!?.]{5,}/;
  const URL_RE = /https?:\/\/|www\./i;
  const SPAM_WORDS = [
    "viagra", "casino", "lottery", "winner", "free bitcoin", "bitcoin giveaway", "crypto bonus",
    "double your money", "make money fast", "earn money", "payday", "seo backlinks",
    "buy followers", "cheap pills", "pharmacy", "cialis", "penis", "mortgage", "loan offer",
    "urgent loan", "inheritance", "bank transfer fee", "prince", "diamond offer", "gold bars",
    "western union", "moneygram", "work from home", "click here", "act now",
    "100% guaranteed", "limited offer", "investment opportunity", "forex signal", "escort", "hacker",
  ];

  const hasSpam = (t) => {
    const low = " " + t.toLowerCase() + " ";
    return SPAM_WORDS.some((w) => low.indexOf(w) !== -1);
  };
  const isGibberish = (t) => {
    const c = t.replace(/[^A-Za-z]/g, "");
    if (!c) return false;
    if (REPEAT_RE.test(c)) return true;
    if (KEYBOARD_RE.test(c)) return true;
    return c.length >= 12 && !VOWEL_RE.test(c);
  };
  const isShouting = (t) => {
    const letters = t.split("").filter((ch) => /[A-Za-z]/.test(ch));
    if (letters.length < 12) return false;
    const upper = letters.filter((ch) => ch === ch.toUpperCase()).length;
    return upper / letters.length > 0.7;
  };

  /* ---- Autocorrect ---- */
  const autoCorrect = (el) => {
    if (!el) return;
    const kind = el.dataset.autocorrect;
    let v = el.value;
    if (!v) return;
    if (kind === "name") {
      v = v.replace(/\s+/g, " ").trim();
      v = v.split(" ").map((w) => (w ? w[0].toUpperCase() + w.slice(1) : w)).join(" ");
      el.value = v;
    } else if (kind === "email") {
      el.value = v.replace(/\s+/g, "").trim().toLowerCase();
    } else if (kind === "phone") {
      el.value = v.replace(/[^+0-9]/g, "");
    } else if (kind === "message") {
      v = v.replace(/[ \t]+/g, " ").trim();
      v = v.replace(/\bi\b/g, "I").replace(/\bi'm\b/gi, "I'm");
      el.value = v;
    }
  };

  /* ---- Per-field errors (mirrors server messages) ---- */
  const fieldErrors = {
    full_name: (v) => {
      if (!v) return "Please enter your full name.";
      if (!NAME_RE.test(v)) return "Names can't contain numbers or symbols — letters only.";
      if (/\d/.test(v)) return "Names can't contain numbers — please enter your real name.";
      if (v.indexOf("@") !== -1) return "Please enter your name, not an email address.";
      if (isGibberish(v) || hasSpam(v)) return "That name looks like spam or gibberish.";
      return "";
    },
    email: (v) => {
      if (!v) return "Please enter your email address.";
      if (!EMAIL_RE.test(v)) return "That email address doesn't look valid — e.g. name@example.com.";
      const local = v.split("@")[0] || "";
      if (isGibberish(local) || hasSpam(v)) return "That email address looks suspicious.";
      return "";
    },
    phone_number: (v) => {
      if (!v) return "";
      if (!PHONE_RE.test(v)) return "Please enter a valid phone number — 7 to 15 digits.";
      return "";
    },
    message: (v) => {
      if (!v) return "Please write a short message about your request.";
      if (v.length < 10) return "Your message is too short — at least 10 characters.";
      if (v.length > 500) return "Please keep your message under 500 characters.";
      if (isGibberish(v)) return "That message looks like gibberish — use real words.";
      if (hasSpam(v)) return "Your message was flagged as spam.";
      if (REPEAT_WORD_RE.test(v)) return "Please remove duplicated words.";
      if (PUNCT_RE.test(v)) return "Please don't use excessive punctuation.";
      if (isShouting(v)) return "Please write in normal case — no shouting.";
      if (/^https?:\/\/\S+$/i.test(v.trim())) return "Please add a short description with any links.";
      return "";
    },
  };

  const setFieldState = (el, error) => {
    if (!el) return;
    if (error) {
      el.classList.add("is-invalid");
      el.classList.remove("is-valid");
      el.setAttribute("aria-invalid", "true");
      el.title = error;
    } else {
      el.classList.remove("is-invalid");
      el.setAttribute("aria-invalid", "false");
      el.title = "";
    }
  };

  const validateField = (el) => {
    const fn = fieldErrors[el.name];
    const error = fn ? fn(el.value) : "";
    setFieldState(el, error);
    return !error;
  };

  /* ---- Contact form ---- */
  const contactForm = document.querySelector(".contactform");
  if (contactForm) {
    ["full_name", "email", "phone_number", "message"].forEach((name) => {
      const el = contactForm.querySelector('[name="' + name + '"]');
      if (!el) return;
      el.addEventListener("blur", () => {
        autoCorrect(el);
        validateField(el);
      });
      el.addEventListener("input", () => {
        if (el.classList.contains("is-invalid")) validateField(el);
      });
    });

    const msgEl = contactForm.querySelector("#message-field");
    const msgCount = document.getElementById("msg-count");
    if (msgEl && msgCount) {
      const update = () => { msgCount.textContent = msgEl.value.length; };
      msgEl.addEventListener("input", update);
      update();
    }

    contactForm.addEventListener("submit", (e) => {
      let firstInvalid = null;
      ["full_name", "email", "phone_number", "message"].forEach((name) => {
        const el = contactForm.querySelector('[name="' + name + '"]');
        autoCorrect(el);
        if (!validateField(el) && !firstInvalid) firstInvalid = el;
      });
      if (firstInvalid) {
        e.preventDefault();
        firstInvalid.focus();
        firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    });
  }

  /* ---- Newsletter form ---- */
  const nlForm = document.querySelector(".newsletter-form");
  if (nlForm) {
    const nlEmail = nlForm.querySelector('input[type="email"]');
    const nlError = nlForm.querySelector(".newsletter-error");
    if (nlEmail) {
      nlEmail.addEventListener("blur", () => autoCorrect(nlEmail));
      nlForm.addEventListener("submit", (e) => {
        autoCorrect(nlEmail);
        const err = fieldErrors.email(nlEmail.value);
        if (err) {
          e.preventDefault();
          if (nlError) {
            nlError.textContent = err;
            nlError.style.display = "block";
          }
          nlEmail.classList.add("is-invalid");
          nlEmail.focus();
        } else if (nlError) {
          nlError.style.display = "none";
        }
      });
    }
  }

  /* ---------- Payment currency ↔ gateway compatibility hint ---------- */
  const payCurrency = document.getElementById("pay-currency");
  const payHint = document.getElementById("pay-hint");
  const payMethods = document.querySelectorAll("input[name='method']");
  if (payCurrency && payMethods.length) {
    const PAYSTACK_OK = ["NGN", "USD", "GHS", "KES", "ZAR"];
    const FLW_OK = ["NGN", "USD", "GBP", "EUR", "JPY", "CAD", "AUD", "GHS", "KES", "ZAR"];
    const updateHint = () => {
      if (!payHint) return;
      const cur = payCurrency.value;
      const method = document.querySelector("input[name='method']:checked");
      const m = method ? method.value : "flutterwave";
      let note = "Payments are encrypted and verified by the gateway. All major world currencies supported.";
      if (m === "paystack" && !PAYSTACK_OK.includes(cur)) {
        note = "Paystack supports NGN, USD, GHS, KES & ZAR only — switch to Flutterwave for " + cur + ".";
      } else if (m === "binance") {
        note = "Binance Pay settles in USDT (crypto) — the amount is converted at checkout.";
      } else if (m === "flutterwave" && !FLW_OK.includes(cur)) {
        note = "That currency may need Flutterwave manual settlement — the gateway will confirm at checkout.";
      }
      payHint.textContent = note;
    };
    payCurrency.addEventListener("change", updateHint);
    payMethods.forEach((r) => r.addEventListener("change", updateHint));
  }

  /* ---------- Footer year ---------- */
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---------- Service detail terminal typing loop ---------- */
  const heroTerm = document.querySelector(".service-hero-term");
  if (heroTerm) {
    const lines = Array.from(heroTerm.querySelectorAll("[data-term]"));
    let lineIdx = 0;
    const typeLine = (el, text, done) => {
      let i = 0;
      el.textContent = "";
      const tick = () => {
        if (i <= text.length) {
          el.textContent = text.slice(0, i);
          i += 1;
          setTimeout(tick, 34);
        } else {
          setTimeout(done, 950);
        }
      };
      tick();
    };
    const cycle = () => {
      const el = lines[lineIdx];
      lines.forEach((l) => { if (l !== el) l.textContent = l.dataset.term; });
      typeLine(el, el.dataset.term, () => {
        lineIdx = (lineIdx + 1) % lines.length;
        setTimeout(cycle, 350);
      });
    };
    lines.forEach((l) => { l.textContent = ""; });
    if (lines.length) setTimeout(cycle, 600);
  }

  /* =========================================================
     REFERRAL SYSTEM
     - Reads ?ref= from URL, stores it, injects into contact form
     - Share buttons build referral links with the referrer's name
     - Toast notifications
     ========================================================= */
  const refParamInit = new URLSearchParams(window.location.search).get("ref");
  let refParam = null;
  let referralName = "";

  /* Persist referral (sessionStorage) so it survives page-to-page
     navigation, e.g. landing on /portfolio then visiting the contact form. */
  const persistRef = () => {
    try {
      if (refParamInit) {
        refParam = refParamInit;
        sessionStorage.setItem("kgs_ref", refParamInit);
      } else if (sessionStorage.getItem("kgs_ref")) {
        refParam = sessionStorage.getItem("kgs_ref");
      }
    } catch (e) { /* storage unavailable */ }
  };
  persistRef();

  /* Inject referral into the contact form's hidden field */
  const injectReferral = () => {
    const hidden = document.getElementById("referral-field");
    if (!hidden) return;
    if (refParam) {
      hidden.value = refParam;
    } else if (referralName) {
      hidden.value = referralName;
    }
  };
  injectReferral();

  /* ---------- Toast ---------- */
  const toast = document.getElementById("referralToast");
  let toastTimer = null;
  const showToast = (title, text) => {
    if (!toast) return;
    const titleEl = document.getElementById("referralToastTitle");
    const textEl = document.getElementById("referralToastText");
    if (titleEl) titleEl.textContent = title;
    if (textEl) textEl.textContent = text;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 4200);
  };
  const toastClose = document.querySelector(".referral-toast-close");
  if (toastClose) {
    toastClose.addEventListener("click", () => toast.classList.remove("show"));
  }

  /* Build the share URL with ?ref=Name */
  const shareUrl = () => {
    const base = window.location.origin + window.location.pathname;
    const ref = refParam || referralName;
    return ref ? base + "?ref=" + encodeURIComponent(ref) : base;
  };

  /* Live preview of the referral link as the visitor types their name */
  const nameInput = document.getElementById("referral-name");
  const linkPreview = document.getElementById("referral-link-preview");
  if (nameInput && linkPreview) {
    const updatePreview = () => {
      const v = nameInput.value.trim();
      linkPreview.textContent = v
        ? (window.location.origin + window.location.pathname) + "?ref=" + encodeURIComponent(v)
        : "https://kinggreatmanspirit.com/?ref=YourName";
    };
    nameInput.addEventListener("input", updatePreview);
  }

  /* Require a name before sharing */
  const requireName = () => {
    const name = (document.getElementById("referral-name") || {}).value || "";
    if (!name.trim()) {
      showToast("Type your name first 👆", "Then tap any share button — it takes 5 seconds.");
      const input = document.getElementById("referral-name");
      const box = document.getElementById("refer-share-actions");
      if (input) input.focus();
      if (box) {
        box.classList.add("refer-shake");
        setTimeout(() => box.classList.remove("refer-shake"), 500);
      }
      return null;
    }
    return name;
  };

  const doShare = (network) => {
    const url = encodeURIComponent(shareUrl());
    const text = encodeURIComponent(
      "Work with King Greatman Spirit — Software Engineer & AI Specialist. " + shareUrl()
    );
    let target = "";
    if (network === "whatsapp") {
      target = "https://wa.me/?text=" + text;
    } else if (network === "facebook") {
      target = "https://www.facebook.com/sharer/sharer.php?u=" + url;
    } else if (network === "twitter") {
      target = "https://twitter.com/intent/tweet?text=" + text;
    } else if (network === "linkedin") {
      target = "https://www.linkedin.com/sharing/share-offsite/?url=" + url;
    }
    if (target) window.open(target, "_blank", "noopener,noreferrer,width=640,height=520");
  };

  const doCopy = () => {
    const url = shareUrl();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(
        () => showToast("Referral Link Copied!", "Share it and earn a reward for every project closed."),
        () => fallbackCopy(url)
      );
    } else {
      fallbackCopy(url);
    }
  };

  const fallbackCopy = (url) => {
    const ta = document.createElement("textarea");
    ta.value = url;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); showToast("Referral Link Copied!", "Share it and earn a reward for every project closed."); }
    catch (e) { showToast("Copy manually", url); }
    document.body.removeChild(ta);
  };

  /* Wire up share buttons */
  document.querySelectorAll(".share-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      referralName = (document.getElementById("referral-name") || {}).value || "";
      if (!requireName()) return;
      injectReferral();
      if (btn.classList.contains("whatsapp-share")) doShare("whatsapp");
      else if (btn.classList.contains("facebook-share")) doShare("facebook");
      else if (btn.classList.contains("twitter-share")) doShare("twitter");
      else if (btn.classList.contains("linkedin-share")) doShare("linkedin");
      else if (btn.classList.contains("copy-link")) doCopy();
    });
  });

  /* ========================================================
     CONVERSION TRACKING — every click counts
     Fires GA4 events when GA is installed; silently no-ops
     otherwise, so the site never breaks.
     ======================================================== */
  window.trackKGS = function (eventName, params) {
    params = params || {};
    try {
      if (typeof gtag === "function") {
        gtag("event", eventName, params);
      } else if (window.dataLayer) {
        window.dataLayer.push({ event: eventName, ...params });
      }
    } catch (e) {}
  };

  document.addEventListener("click", (e) => {
    const el = e.target.closest("[data-track]");
    if (!el) return;
    const label = el.getAttribute("data-track");
    const value = el.getAttribute("data-track-value") || "";
    window.trackKGS(label, {
      event_category: "CTA",
      event_label: value || (el.textContent || "").trim().slice(0, 60),
      location: window.location.pathname,
    });
  });

  document.addEventListener("submit", (e) => {
    const form = e.target;
    if (form.id === "contact-form" || form.classList.contains("php-email-form")) {
      window.trackKGS("contact_form_submit", { location: window.location.pathname });
    }
    if (form.id === "newsletter-form") {
      window.trackKGS("newsletter_subscribe", { location: window.location.pathname });
    }
  });

  document.addEventListener("kgs:chat-open", () => {
    window.trackKGS("chatbot_open", { location: window.location.pathname });
  });
  document.addEventListener("kgs:ticket-sent", () => {
    window.trackKGS("support_ticket_sent", { location: window.location.pathname });
  });
  document.addEventListener("kgs:payment-start", () => {
    window.trackKGS("payment_started", { location: window.location.pathname });
  });
})();
