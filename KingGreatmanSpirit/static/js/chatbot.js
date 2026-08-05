/**
 * KGS AI CHATBOT — King Greatman Spirit's digital assistant.
 * Intent-matching engine with live replies, typing indicator,
 * context memory, quick questions and sales nudges.
 */
(function () {
  "use strict";

  const init = () => {

  const widget = document.getElementById("kgs-chatbot");
  if (!widget) return;

  const launcher = document.getElementById("kgs-chat-launcher");
  const panel = document.getElementById("kgs-chat-panel");
  const messagesEl = document.getElementById("kgs-chat-messages");
  const chipsEl = document.getElementById("kgs-chat-chips");
  const inputEl = document.getElementById("kgs-chat-input");
  const sendBtn = document.getElementById("kgs-chat-send");
  const closeBtn = document.getElementById("kgs-chat-close");
  const badge = document.getElementById("kgs-chat-badge");
  const teaser = document.getElementById("kgs-chat-teaser");
  const teaserClose = document.getElementById("kgs-teaser-close");

  const LINKS = {
    whatsapp: "https://wa.me/2349014155705",
    email: "mailto:hello@kinggreatmanspirit.com",
    pay: "/payment/",
    portfolio: "/#portfolio",
    contact: "/#contact",
    linktree: "https://linktr.ee/greatestmaneva",
    cv: "/media/resume/Greatman_Justus_Unye-Awaji_Software_Engineer_Resume.pdf",
  };

  const state = {
    open: false,
    name: "",
    topic: "",
    askedName: false,
    askedBudget: false,
    exchanges: 0,
    nudgeDone: false,
    budgetAskedCount: 0,
    budget: "",
  };

  try {
    const saved = localStorage.getItem("kgs_name");
    if (saved) state.name = saved;
  } catch (e) {}

  /* ========================================================
     UI helpers
     ======================================================== */
  const esc = (s) =>
    String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  const linkify = (s) =>
    esc(s).replace(
      /&lt;a href=['"]([^'"]+)['"](?: target=['"]_blank['"])?&gt;(.*?)&lt;\/a&gt;/g,
      (m, href, text) => {
        const safe = /^(https?:\/\/|mailto:|tel:|\/|#)/i.test(href);
        return safe
          ? `<a href="${href}" target="_blank" rel="noopener noreferrer">${text}</a>`
          : esc(`<a href="${href}">${text}</a>`);
      }
    );
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
  const strip = (s) =>
    String(s).toLowerCase().replace(/[^a-z0-9\s]/g, " ").replace(/\s+/g, " ").trim();

  const scrollBottom = () => {
    messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: "smooth" });
  };

  const showTyping = () => {
    const t = document.createElement("div");
    t.className = "kgs-msg kgs-bot kgs-typing";
    t.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    t.id = "kgs-typing";
    messagesEl.appendChild(t);
    scrollBottom();
  };
  const hideTyping = () => {
    const t = document.getElementById("kgs-typing");
    if (t) t.remove();
  };

  const addUser = (text) => {
    const d = document.createElement("div");
    d.className = "kgs-msg kgs-user";
    d.innerHTML = esc(text);
    messagesEl.appendChild(d);
    scrollBottom();
  };

  const renderChips = (chips) => {
    chipsEl.innerHTML = "";
    (chips || []).forEach((c) => {
      const label = typeof c === "object" ? c.label : c;
      const b = document.createElement("button");
      b.type = "button";
      b.className = "kgs-chip";
      b.textContent = label;
      b.addEventListener("click", () => {
        if (typeof c === "object" && c.action) {
          handleChipAction(c.action, label);
          return;
        }
        if (/\bpay\b|pay now/i.test(label)) {
          document.dispatchEvent(new CustomEvent("kgs:payment-start"));
        }
        sendMessage(label);
      });
      chipsEl.appendChild(b);
    });
  };

  const handleChipAction = (action, label) => {
    if (action === "ticket") openTicketForm();
    else if (action === "close") closeChat();
    else if (action === "wa") window.open(LINKS.whatsapp, "_blank", "noopener,noreferrer");
    else sendMessage(label);
  };

  const addBot = async (texts, { chips = [], delayBase = 650 } = {}) => {
    showTyping();
    const chunks = Array.isArray(texts) ? texts : [texts];
    const totalChars = chunks.join(" ").length;
    const perChunk = Math.min(420, Math.max(160, delayBase + totalChars * 3));
    await sleep(Math.min(1800, perChunk));
    for (const chunk of chunks) {
      await sleep(300);
      hideTyping();
      const d = document.createElement("div");
      d.className = "kgs-msg kgs-bot";
      d.innerHTML = linkify(chunk).replace(/\n/g, "<br>");
      messagesEl.appendChild(d);
      scrollBottom();
      if (chunks.length > 1) showTyping();
    }
    hideTyping();
    renderChips(chips);
    if (badge) badge.style.display = "none";
  };

  const openChat = () => {
    state.open = true;
    panel.classList.add("open");
    launcher.setAttribute("aria-expanded", "true");
    if (badge) badge.style.display = "none";
    if (teaser) teaser.classList.remove("show");
    document.dispatchEvent(new CustomEvent("kgs:chat-open"));
    setTimeout(() => inputEl && inputEl.focus(), 400);
  };
  const closeChat = () => {
    state.open = false;
    panel.classList.remove("open");
    launcher.setAttribute("aria-expanded", "false");
  };

  launcher.addEventListener("click", () => {
    if (state.open) closeChat();
    else openChat();
  });
  if (closeBtn) closeBtn.addEventListener("click", closeChat);
  if (teaserClose) {
    teaserClose.addEventListener("click", () => {
      teaser.classList.remove("show");
      try { sessionStorage.setItem("kgs_teaser", "1"); } catch (e) {}
    });
  }

  const sendMessage = (raw) => {
    const text = (raw || "").trim();
    if (!text || state.typing) return;
    addUser(text);
    state.exchanges += 1;
    respond(text);
  };

  /* ========================================================
     LIVE SUPPORT TICKET — "Talk to King directly"
     Stores a ticket + alerts the owner via WhatsApp/SMS/email.
     ======================================================== */
  const ticketEl = document.getElementById("kgs-ticket");
  const ticketName = document.getElementById("kgs-ticket-name");
  const ticketContact = document.getElementById("kgs-ticket-contact");
  const ticketMessage = document.getElementById("kgs-ticket-message");
  const ticketError = document.getElementById("kgs-ticket-error");
  const ticketSend = document.getElementById("kgs-ticket-send");
  const ticketCancel = document.getElementById("kgs-ticket-cancel");
  const inputWrap = document.querySelector(".kgs-chat-input-wrap");

  const ticketBusy = (busy) => {
    if (ticketSend) {
      ticketSend.disabled = busy;
      ticketSend.textContent = busy ? "Sending…" : "Request Live Support";
    }
  };

  const openTicketForm = () => {
    if (!ticketEl) return;
    ticketError.textContent = "";
    ticketEl.hidden = false;
    if (inputWrap) inputWrap.style.display = "none";
    if (chipsEl) chipsEl.innerHTML = "";
    renderChips(["Chat on WhatsApp", "Back to chat"]);
    setTimeout(() => ticketName && ticketName.focus(), 100);
  };

  const closeTicketForm = () => {
    if (!ticketEl) return;
    ticketEl.hidden = true;
    if (inputWrap) inputWrap.style.display = "";
  };

  const submitTicket = async () => {
    if (!ticketEl) return;
    ticketError.textContent = "";
    const name = (ticketName.value || "").trim();
    const contact = (ticketContact.value || "").trim();
    const message = (ticketMessage.value || "").trim();

    if (name.length < 2) {
      ticketError.textContent = "Please tell us your name.";
      ticketName.focus();
      return;
    }
    if (contact.length < 5) {
      ticketError.textContent = "Add your email or phone number so King can reach you.";
      ticketContact.focus();
      return;
    }
    if (message.length < 10) {
      ticketError.textContent = "Please describe your request (at least 10 characters).";
      ticketMessage.focus();
      return;
    }

    const csrf = document.querySelector('#kgs-chatbot input[name="csrfmiddlewaretoken"]');
    const body = new FormData();
    body.append("csrfmiddlewaretoken", csrf ? csrf.value : "");
    body.append("full_name", name);
    body.append("contact", contact);
    body.append("message", message);
    body.append("topic", state.topic || "General");
    body.append("channel", "chatbot");

    ticketBusy(true);
    try {
      const res = await fetch(widget.getAttribute("data-ticket-url") || "/dashboard/ticket/create/", {
        method: "POST",
        body,
        headers: { "X-Requested-With": "XMLHttpRequest" },
        credentials: "same-origin",
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.ok) {
        document.dispatchEvent(new CustomEvent("kgs:ticket-sent"));
        closeTicketForm();
        ticketName.value = "";
        ticketContact.value = "";
        ticketMessage.value = "";
        if (!state.name && NAME_RE.test(name)) {
          state.name = name.split(" ").map((w) => w[0].toUpperCase() + w.slice(1)).join(" ");
        }
        await addBot(
          [
            `Done, ${state.name || name}! 🎧 King just got an instant alert about your request — he'll message you very shortly (usually within minutes).`,
            "Want to reach him even faster? Tap WhatsApp below — that's his fastest channel.",
          ],
          { chips: [{ label: "💬 Chat on WhatsApp", action: "wa" }, { label: "How much does a website cost?" }] }
        );
        return;
      }
      ticketError.textContent = data.error || "Something went wrong — please try again.";
    } catch (e) {
      ticketError.textContent = "Connection failed — please try again or use WhatsApp.";
    } finally {
      ticketBusy(false);
    }
  };

  if (ticketSend) ticketSend.addEventListener("click", submitTicket);
  if (ticketCancel) ticketCancel.addEventListener("click", closeTicketForm);
  ticketContact && ticketContact.addEventListener("keydown", (e) => {
    if (e.key === "Enter") submitTicket();
  });

  const onSend = () => {
    const text = inputEl.value.trim();
    if (!text) return;
    inputEl.value = "";
    sendMessage(text);
  };
  sendBtn.addEventListener("click", onSend);
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") onSend();
  });

  /* ========================================================
     INTENT ENGINE
     ======================================================== */
  const NAME_RE = /^[A-Za-z\u00C0-\u00FF' .-]{2,40}$/;
  const BUDGET_RE = /(\d[\d,.]*\s?(k|m|k|million|billion|naira|ngn|usd|dollars|\$|₦|€|£)?)|(₦|£|\$)\s?\d[\d,.]*/i;
  const NAME_PATTERN = /(?:my name is|my names|my name's|name is|call me|(?<![a-z\u00C0-\u00FF])i am|(?<![a-z\u00C0-\u00FF])i'm|(?<![a-z\u00C0-\u00FF])im)\s+([a-z\u00C0-\u00FF]+)/i;
  const NAME_STOPWORDS = new Set(["a", "an", "the", "i", "we", "they", "he", "she", "it", "you", "on", "at", "via", "with", "in", "to", "for", "from", "of", "back", "later", "now", "here", "there", "just", "very", "really", "so", "too", "new", "ready", "happy", "glad", "sure", "good", "fine", "great", "looking", "asking", "trying", "wondering", "interested", "considering", "planning", "starting", "making", "getting", "coming", "going", "thinking", "hoping", "searching", "checking", "finding", "writing", "calling", "contacting", "telling", "saying", "wanting", "willing", "keen", "free", "available", "online", "busy", "not", "no", "yes", "based", "stuck"]);

  const KB = [
    /* ---------- GREETING ---------- */
    {
      id: "greeting",
      match: ["hello", "hi ", " hi", "hey", "how far", "good morning", "good afternoon", "good evening", "good day", "yo", "salam", "sup", "hiya", "hii", "hello?", "how are you", "how do you do"],
      reply: () => {
        const name = state.name ? `, ${state.name}` : "";
        return [
          `Hello${name}! 👋 I'm King Greatman Spirit's AI assistant — his digital twin, if you like.`,
          `I can tell you about our ${"software development"}, ${"mobile apps"}, ${"AI & ML solutions"}, ${"data analytics"}, pricing, payments and more. What would you like to know?`,
        ];
      },
      chips: ["What services do you offer?", "How much does a website cost?", "Is it safe to pay?", "How do I pay?"],
    },

    /* ---------- SERVICES ---------- */
    {
      id: "services",
      match: ["services", "what do you do", "what do we do", "offer", "capabilities", "can you help", "what can you", "what are your services", "what do you offer", "help me with", "list of services"],
      reply: () => {
        if (!state.name && !state.askedName) {
          state.askedName = true;
          return [
            "Great question! Before I dive in — what should I call you? 😊",
            "Meanwhile, here's what we do:",
            "🚀 1. Software & Web Development — websites, web apps, dashboards, e-commerce\n🤖 2. AI & Machine Learning — chatbots, automation, predictive models\n📊 3. Data Analysis & BI — Power BI dashboards, insights, reports\n🎯 4. Digital Strategy & Consulting — marketing, social media, growth\n🎨 5. Digital Design — branding, UI/UX, graphics\n🎓 6. Tech Training & Prompt Engineering — courses & mentoring",
            "We serve every sector — fintech, health, education, e-commerce, real estate, agriculture, logistics and more. Which one interests you most?",
          ];
        }
        return [
          "Here's everything we do 👇",
          "🚀 1. Software & Web Development — websites, web apps, dashboards, e-commerce\n🤖 2. AI & Machine Learning — chatbots, automation, predictive models\n📊 3. Data Analysis & BI — Power BI dashboards, insights, reports\n🎯 4. Digital Strategy & Consulting — marketing, social media, growth\n🎨 5. Digital Design — branding, UI/UX, graphics\n🎓 6. Tech Training & Prompt Engineering — courses & mentoring",
          "We serve every sector — fintech, health, education, e-commerce, real estate, agriculture, logistics and more. Which one interests you most?",
        ];
      },
      chips: ["Website development", "Mobile apps", "AI & Machine Learning", "Data analytics"],
    },

    /* ---------- TRUST / SAFETY ---------- */
    {
      id: "trust",
      match: ["safe", "legit", "scam", "trust you", "can i trust", "is this real", "verify", "genuine", "reliable", "authentic", "dodgy", "bogus", "fake", "fraud", "trusted"],
      reply: () => {
        return [
          "Totally fair question — you should always be careful online! 🔒",
          "Here's why you can trust us:\n✅ Payments run through Flutterwave & Paystack — the same gateways big banks and businesses use\n✅ You pay in stages: a small deposit to start, the rest as we deliver milestones\n✅ Real portfolio, real clients, real results — see them 👉 <a href='/#portfolio' target='_blank'>portfolio</a> and <a href='/#testimonials' target='_blank'>client reviews</a>",
          "And you can always talk to King directly first — no middlemen, no pressure. He'll happily share references on WhatsApp. 😊",
        ];
      },
      chips: [{ label: "🎧 Ask King for references", action: "ticket" }, "View testimonials", "Can I pay in installments?", "Chat on WhatsApp"],
    },

    /* ---------- GUARANTEE / RISK REVERSAL ---------- */
    {
      id: "guarantee",
      match: ["guarantee", "refund", "money back", "what if i dont like", "not happy", "what if something goes wrong", "goes wrong", "what if you fail", "what if you dont deliver", "dont deliver", "cancel", "cancellation", "assurance", "warranty"],
      reply: () => {
        return [
          "I get it — you want to be sure. Here's my promise 🤝",
          "🔒 The risk is on me, not you:\n• You only pay as I deliver — deposit to start, balance on milestones\n• You get revision rounds on every project until you're happy\n• Every launch comes with free 30-day support — if anything breaks, I fix it fast",
          "In short: you never pay full price upfront for unfinished work. That's how confident I am. Ready to lock in your slot? 🚀",
        ];
      },
      chips: ["How do I pay?", "Pay now securely", "What happens after launch?", "Get a free quote"],
    },

    /* ---------- WHY US ---------- */
    {
      id: "whyus",
      match: ["why you", "why should i choose", "why choose", "why king", "why not you", "why you and not", "vs agencies", "vs freelancers", "compare", "better than", "other developers", "other freelancers", "big agency", "why should i hire", "what makes you different", "what makes you special", "convince me"],
      reply: () => {
        return [
          "Honest answer? You get big-agency quality without the big-agency price tag 🏆",
          "💎 When you work with King directly:\n• You talk to the actual engineer — not a sales team\n• Fixed quotes, honest pricing, no hidden fees\n• One specialist across code, design, data AND strategy — no hand-offs, no lost context\n• 125+ projects shipped, 5+ years, clients worldwide",
          "That's why clients stay and refer others. Want to see what he'd build for you? The first quote is free. 😉",
        ];
      },
      chips: ["View my portfolio", "See testimonials", "Get a free quote", "How much does a website cost?"],
    },

    /* ---------- DEPOSIT / INSTALLMENTS ---------- */
    {
      id: "deposit",
      match: ["deposit", "installment", "installments", "part payment", "pay half", "pay in parts", "split payment", "pay in stages", "pay later", "pay as we go", "milestone", "pay monthly", "pay in bits", "deferred", "flexible payment"],
      reply: () => {
        return [
          "Yes — we make it easy to start! 💳",
          "Most projects work like this:\n1️⃣ Small deposit to secure your slot and begin\n2️⃣ Balance paid in milestones as work is delivered\n3️⃣ Final payment after you approve the finished product",
          "So you're never fully exposed — you pay for what you see. Tell me your budget and I'll tailor a plan that fits your cash flow. 😊",
        ];
      },
      chips: ["How do I pay?", "Get a free quote", "Start a project", "Chat on WhatsApp"],
    },

    /* ---------- FREE / CONSULTATION ---------- */
    {
      id: "free",
      match: ["free quote", "free consultation", "free support", "no cost", "no charge", "at no cost", "is it free", "free advice", "free call", "free session", "no obligation", "complimentary", "for free"],
      reply: () => {
        return [
          "Here's what's always FREE with us 🎁",
          "✅ Free consultation — we discuss your idea and goals\n✅ Free tailored quote — a fixed price, no surprises\n✅ Free 30-day support after launch\n✅ Free advice, even if you don't hire us yet",
          "Zero risk, zero pressure. Want to claim your free consultation? It takes 2 minutes. 👉 <a href='/#contact' target='_blank'>Tell me your idea</a>",
        ];
      },
      chips: ["Tell me your idea", "Get a free quote", "How do I pay?"],
    },

    /* ---------- MAINTENANCE / AFTER LAUNCH ---------- */
    {
      id: "maintenance",
      match: ["maintenance", "support", "after launch", "what happens after", "updates", "update", "upkeep", "hosting", "domain", "who will host", "host my site", "buy a domain", "fix bugs", "broken", "recover", "rebuild", "backup", "security"],
      reply: () => {
        return [
          "Every project ships with a safety net 🛡️",
          "• 30 days of FREE support after launch — bugs fixed, tweaks made\n• Optional maintenance plans from ₦25,000/month: updates, backups, security, monitoring\n• Need hosting or a domain? We set it up and walk you through it",
          "You're never left stranded — that's the standard here. What would you like covered?",
        ];
      },
      chips: ["Get a free quote", "How much does a website cost?", "Start a project"],
    },

    /* ---------- INTERNATIONAL / REMOTE ---------- */
    {
      id: "intl",
      match: ["international", "abroad", "outside nigeria", "foreign", "remote", "overseas", "diaspora", "usa", "united states", "america", "canada", "uk", "europe", "germany", "dubai", "usd", "dollars", "timezone", "worldwide", "global", "japan", "australia"],
      reply: () => {
        return [
          "We work with clients around the world 🌍✈️",
          "• Remote-first — connect on WhatsApp, email, or video calls\n• Pay in USD via card or crypto (USDT) — super easy\n• We work across time zones with clear weekly updates",
          "Nigerian clients pay in ₦; international clients in USD. Where are you based? I'll confirm exactly how it'll work for you.",
        ];
      },
      chips: ["How do I pay?", "Get a free quote", "Chat on WhatsApp"],
    },

    /* ---------- EXPRESS / FAST-TRACK ---------- */
    {
      id: "express",
      match: ["urgent", "emergency", "asap", "fast", "quick", "fast track", "express", "same day", "very soon", "quickly", "as soon as", "right away", "immediately", "need it now", "rushed", "hurry", "quick turnaround"],
      reply: () => {
        return [
          "Need it fast? We have an express lane ⚡",
          "• Landing page: as fast as 48–72 hours\n• Business website: from 1 week\n• Urgent fixes & recoveries: same-day where possible",
          "Express slots are limited each month — tell me your deadline and I'll tell you honestly what's possible. 👉",
        ];
      },
      chips: ["I want to start now", "Get a free quote", "Chat on WhatsApp"],
    },

    /* ---------- PRIVACY / NDA ---------- */
    {
      id: "privacy",
      match: ["privacy", "confidential", "confidentiality", "nda", "non disclosure", "secret", "keep it private", "sensitive", "my data", "data protection", "private", "anonymity"],
      reply: () => {
        return [
          "Your ideas are safe with us 🤐🔒",
          "• We can sign an NDA before we even discuss details\n• Your code, data and business information stay 100% yours\n• Chat here is private — nothing is shared or sold",
          "If you need an NDA signed first, just ask via the form below and King will sort it within hours. 😊",
        ];
      },
      chips: [{ label: "🎧 Request an NDA", action: "ticket" }, "Get a free quote", "Start a project"],
    },

    /* ---------- MEETING / CALL ---------- */
    {
      id: "call",
      match: ["meeting", "call", "zoom", "google meet", "video call", "discuss", "schedule", "book a call", "strategy session", "discovery call", "book a meeting", "talk it through"],
      reply: () => {
        return [
          "Happy to set that up! 📅 The first consultation is free.",
          "Choose your channel:\n💬 WhatsApp: <a href='https://wa.me/2349014155705' target='_blank'>wa.me/2349014155705</a>\n✉️ Email: hello@kinggreatmanspirit.com\n🖥️ Zoom / Google Meet — King sends the link",
          "Tell him your best time and he'll confirm within 24 hours. What would you like to talk about?",
        ];
      },
      chips: [{ label: "🎧 Request a call back", action: "ticket" }, "Chat on WhatsApp", "Get a free quote"],
    },

    /* ---------- MARKETPLACES ---------- */
    {
      id: "marketplace",
      match: ["fiverr", "upwork", "freelancer", "freelance", "freelancing", "marketplaces", "gigs", "freelance sites", "peopleperhour", "toptal"],
      reply: () => {
        return [
          "Great question! We work directly with clients AND on marketplaces 🧑‍💻",
          "Working directly (this site) is cheaper and faster for you — no platform fees. But King is also on Upwork & Fiverr for those who prefer the marketplace route.",
          "Want his profile links? Message him on WhatsApp — he'll share them right away. 😊",
        ];
      },
      chips: ["Chat on WhatsApp", "Get a free quote", "How do I pay?"],
    },

    /* ---------- META / ABOUT THE BOT ---------- */
    {
      id: "meta",
      match: ["are you real", "are you ai", "are you a bot", "is this a bot", "robot", "did you build this website", "who made this website", "who built this site", "who built this website", "who made this site", "who created this", "what are you", "are you human", "try me", "show me what you can do", "impress me"],
      reply: () => {
        return [
          "I'm as real as it gets — a digital twin of King Greatman Spirit 🤖👑",
          "Fun fact: King built this very website himself — Django, the works — and he built ME to answer for him at any hour.",
          "So behind every answer is a real engineer who's shipped 125+ projects. And he's only one tap away if you want the human touch. 😉",
        ];
      },
      chips: [{ label: "🎧 Talk to King directly", action: "ticket" }, "What services do you offer?", "View my portfolio"],
    },

    /* ---------- OPPORTUNITIES / COLLABORATION ---------- */
    {
      id: "opportunity",
      match: ["job", "internship", "vacancy", "hiring", "recruit", "work for you", "join your team", "partnership", "partner", "collaborate", "collaboration", "business proposal", "sponsor", "investor", "apprenticeship", "volunteer"],
      reply: () => {
        return [
          "Love the ambition! 🚀 We're always open to great collaborations.",
          "• Internships / apprenticeships: send your CV via the contact form\n• Partnerships: agencies, marketers, developers — let's talk referrals\n• Investments / business proposals: King loves a bold idea",
          "Send a message below with 'Partnership' or 'Opportunity' in it, and King will personally reply within 24 hours. 💼",
        ];
      },
      chips: [{ label: "🎧 Send an opportunity", action: "ticket" }, "Contact form", "Chat on WhatsApp"],
    },

    /* ---------- OBJECTION / NOT READY YET ---------- */
    {
      id: "objection",
      match: ["maybe", "think about it", "let me think", "not sure", "not ready", "just looking", "just browsing", "exploring", "give me time", "come back later", "decide later", "compare options", "shopping around", "not now", "no rush"],
      reply: () => {
        return [
          "No pressure at all — smart people take their time 🧠✨",
          "Just so you know: your free quote has no expiry, and you can always message me later on WhatsApp.",
          "One thing though — rates and slots can change with demand. If you're even 70% serious, grab the free consultation now and decide later. Zero obligation. 😊",
        ];
      },
      chips: ["Get a free quote", "Pay now securely", "Chat on WhatsApp"],
    },

    /* ---------- WEBSITE / WEB DEV ---------- */
    {
      id: "website",
      match: ["website", "web dev", "web design", "landing page", "ecommerce", "e-commerce", "online store", "shop", "django", "react", "web app", "web application", "blog site", "school website", "business website", "portfolio site", "lms", "crm"],
      reply: () => {
        state.topic = "website";
        return [
          "Yes! Websites are our bread and butter 🍞💻 — from sleek landing pages to full e-commerce stores and custom web apps.",
          "💡 Typical pricing:\n• Landing page: from ₦150,000 / $150\n• Business website: ₦350,000 – ₦700,000\n• E-commerce store: from ₦600,000\n• Custom web app / portal: from ₦1,000,000 / $1,000",
          "We build with Django, React, Node.js, PHP/Laravel — fast, secure, SEO-ready, and mobile-friendly. Want a free quote? Tell me about your business and what you need it to do!",
        ];
      },
      chips: ["Get a free quote", "E-commerce for my shop", "How long does it take?", "How do I pay?"],
    },

    /* ---------- MOBILE APPS ---------- */
    {
      id: "mobile",
      match: ["mobile app", "mobile application", "android app", "ios app", "iphone app", "flutter", "react native", "play store", "app store", "build an app", "make an app", "app development"],
      reply: () => {
        state.topic = "mobile";
        return [
          "Absolutely — we build mobile apps for Android, iOS, and both at once (cross-platform) 📱✨",
          "💡 Typical pricing:\n• Simple app: from $1,500 / ₦1,500,000\n• Mid-range app (APIs, payments, chat): $3,000 – $8,000\n• Enterprise / complex apps: $8,000+",
          "We handle the full journey: idea → UI/UX design → development → Play Store / App Store launch. Payment apps, delivery apps, booking apps, learning apps — we've got you. What kind of app do you have in mind?",
        ];
      },
      chips: ["How much for an app?", "How long does an app take?", "Get a free quote", "How do I pay?"],
    },

    /* ---------- AI / ML ---------- */
    {
      id: "ai",
      match: ["ai ", " ai", "artificial intelligence", "machine learning", "ml", "chatbot", "chat bot", "chatgpt", "gpt", "automation", "bot", "predictive", "model", "tensorflow", "pytorch", "llm", "openai", "vision", "ocr", "recommendation", "sentiment", "automate", "ai agent", "copilot", "ai tool", "ai tools", "virtual assistant", "intelligent", "gpt bot"],
      reply: () => {
        state.topic = "ai";
        return [
          "Now we're talking! 🤖 AI & Machine Learning is my speciality:",
          "• Custom AI chatbots (like me!) & GPT-powered assistants\n• Business automation — workflows that work while you sleep\n• Predictive models, forecasting & recommendation systems\n• Computer vision, OCR, sentiment analysis\n• Data pipelines & model deployment",
          "💡 Typical pricing: AI chatbots from ₦400,000 / $500; full ML systems from $1,500.\n\nTell me what you want to automate or predict — I'll point you to the best solution!",
        ];
      },
      chips: ["Build me an AI chatbot", "Automate my business", "How much for AI?", "Get a free quote"],
    },

    /* ---------- DATA ---------- */
    {
      id: "data",
      match: ["data", "analytics", "analysis", "dashboard", "power bi", "powerbi", "excel", "sql", "bi", "insight", "report", "kpi", "visualization", "statistics"],
      reply: () => {
        state.topic = "data";
        return [
          "Data is gold — and I'm a data analyst at heart 📊✨",
          "• Interactive Power BI dashboards\n• Business intelligence & KPI tracking\n• Data cleaning, analysis & storytelling reports\n• SQL / Python analysis for better decisions",
          "💡 Dashboards start from ₦250,000 / $250.\n\nBring your data, and I'll turn it into decisions that grow revenue. What kind of data do you work with?",
        ];
      },
      chips: ["I need a dashboard", "How much for data analysis?", "Get a free quote"],
    },

    /* ---------- SOCIAL MEDIA / MARKETING ---------- */
    {
      id: "social",
      match: ["social media", "marketing", "content", "instagram", "facebook page", "tiktok", "growth", "brand", "ads", "strategy", "influencer", "seo", "digital marketing", "youtube"],
      reply: () => {
        state.topic = "social";
        return [
          "Social media is where brands win 🚀📈",
          "• Complete social media management & content\n• Brand strategy, ad campaigns & growth\n• SEO so clients find YOU on Google\n• Full digital marketing funnels",
          "💡 Management retainers start from ₦100,000/month.\n\nWant me to grow your brand? Tell me which platform you're strongest on!",
        ];
      },
      chips: ["Manage my social media", "SEO for my business", "Get a free quote"],
    },

    /* ---------- TRAINING ---------- */
    {
      id: "training",
      match: ["training", "learn", "learn python", "course", "mentor", "tutor", "teach", "coach", "classes", "workshop", "prompt engineering", "curriculum", "students"],
      reply: () => {
        state.topic = "training";
        return [
          "Knowledge is power — let's level you up 🎓🔥",
          "• Python & web development (Django, React)\n• Data analysis & Power BI\n• AI tools, ChatGPT & prompt engineering\n• One-on-one mentoring or team training",
          "💡 Training starts from ₦150,000 per cohort — group discounts available.\n\nWhat skill do you (or your team) want to master?",
        ];
      },
      chips: ["I want to learn Python", "Train my team", "How much is training?", "Get a free quote"],
    },

    /* ---------- PRICING / COSTS ---------- */
    {
      id: "pricing",
      match: ["how much", "price", "pricing", "cost", "rate", "fee", "charge", "budget", "expensive", "quote", "quotation", "estimate", "afford", "package", "pay plan", "installment", "fees", "200k", "500k", "1m", "lower budget", "small budget", "tight budget"],
      reply: () => {
        if (state.askedBudget) {
          return [
            "Here's a quick price map 👇",
            "• Landing page: from ₦150,000 / $150\n• Business website: ₦350,000 – ₦700,000\n• E-commerce: from ₦600,000\n• Mobile app: from $1,500\n• AI chatbot: from ₦400,000 / $500\n• Dashboard: from ₦250,000\n• Training: from ₦150,000\n• Social media: from ₦100,000/month",
            "Every project is tailored — so let's lock your exact quote. What are you building, and what's your rough budget?",
          ];
        }
        state.askedBudget = true;
        return [
          "I'll give you honest ranges — no hidden surprises 💰👇",
          "• Landing page: from ₦150,000 / $150\n• Business website: ₦350,000 – ₦700,000\n• E-commerce: from ₦600,000\n• Mobile app: from $1,500\n• AI chatbot: from ₦400,000 / $500\n• Dashboard: from ₦250,000\n• Training: from ₦150,000\n• Social media: from ₦100,000/month",
          "What's your budget range? It helps me recommend the perfect package for you. 😊",
        ];
      },
      chips: ["₦200k or less", "₦500k – ₦1M", "More than ₦1M", "Get a free quote"],
    },

    /* ---------- PAYMENT ---------- */
    {
      id: "pay",
      match: ["pay", "payment", "flutterwave", "paystack", "binance", "crypto", "usdt", "transfer", "card", "bank", "how do i pay", "make payment", "deposit", "invoice", "receipt", "installment", "gateway"],
      reply: () => {
        state.topic = "pay";
        return [
          "Great news — paying is easy, fast, and super secure 🔒✨",
          "We accept:\n• Flutterwave — cards, bank transfer, USSD, mobile money\n• Paystack — cards, bank transfer, USSD\n• Binance Pay — crypto (USDT & more)",
          "You'll get an instant confirmation and a beautiful receipt in your email. 👉 <a href='/payment/' target='_blank'>Start a secure payment now</a>",
          "Prefer to ease in? You can start with a small deposit and split the balance across milestones — just say the word.",
          "Want to begin your project today? Let's get you started! 🚀",
        ];
      },
      chips: ["Pay now securely", "Can I pay in installments?", "I want to start a project", "Chat on WhatsApp"],
    },

    /* ---------- PORTFOLIO ---------- */
    {
      id: "portfolio",
      match: ["portfolio", "projects", "previous work", "past work", "examples", "show me", "your work", "samples", "case study", "what have you built", "project showcase", "best project"],
      reply: () => {
        return [
          "I'd love to show off! 🏆 We've delivered 125+ projects across software, AI, data and design — for clients in health, finance, e-commerce, education, real estate and more.",
          "Explore the full showcase here 👉 <a href='/#portfolio' target='_blank'>View my portfolio</a>",
          "My favourites: a Landmark AI Virtual Assistant, corporate websites, e-commerce platforms, and Power BI dashboards that changed how businesses decide. 😎",
        ];
      },
      chips: ["What services do you offer?", "How do I pay?", "Get a free quote"],
    },

    /* ---------- TESTIMONIALS ---------- */
    {
      id: "testimonials",
      match: ["testimonial", "reviews", "clients say", "client feedback", "rating", "referrals", "recommend", "trust", "credible", "proof", "people say", "reputation"],
      reply: () => {
        return [
          "Clients are the real review 📣✨",
          "Here's the kind of feedback I get:\n⭐ \"Exceptional quality and delivered ahead of schedule\"\n⭐ \"King's AI solutions transformed our workflow\"\n⭐ \"Professional, fast, and communicates clearly\"",
          "Read real client words here 👉 <a href='/#testimonials' target='_blank'>See testimonials</a>",
          "Ready to add your own success story to the list? 😉",
        ];
      },
      chips: ["Start a project", "How do I pay?", "View my portfolio"],
    },

    /* ---------- CONTACT ---------- */
    {
      id: "contact",
      match: ["contact", "reach you", "email", "whatsapp", "phone", "number", "call", "location", "where are you", "address", "port harcourt", "message you", "talk to", "human", "real person", "manager", "customer care", "support", "live agent", "agent", "speak to someone", "talk to someone", "help desk", "assistance", "attendant"],
      reply: () => {
        return [
          "You can reach King directly — he replies within 24 hours (often faster!) 💬",
          "💬 WhatsApp: <a href='https://wa.me/2349014155705' target='_blank'>Chat on WhatsApp</a>\n✉️ Email: hello@kinggreatmanspirit.com\n📍 Base: Nigeria — serving clients worldwide",
          "Or tap below to send him a LIVE alert right now — he gets an instant WhatsApp & SMS notification and messages you back immediately. 🎧",
        ];
      },
      chips: [{ label: "🎧 Talk to King directly", action: "ticket" }, "Chat on WhatsApp", "Send an email", "Contact form"],
    },

    /* ---------- AVAILABILITY / TIMELINE ---------- */
    {
      id: "availability",
      match: ["available", "availability", "free now", "slot", "when can you start", "start date", "timeline", "how long", "delivery time", "deadline", "urgent", "asap", "how soon", "timeframe", "how fast", "rush", "start now", "start today", "how quickly", "when do you start", "when can we start"],
      reply: () => {
        return [
          "Good news — we have limited project slots open right now and I'm available for new work 🚀",
          "⏱️ Typical timelines:\n• Landing page: 3–7 days\n• Business website: 1–3 weeks\n• E-commerce: 2–5 weeks\n• Mobile app: 4–10 weeks\n• AI system: 3–8 weeks",
          "Slots are filling fast — the best way to lock yours is to start now. Want to kick off today? 😊",
        ];
      },
      chips: ["I want to start now", "Pay securely", "Chat on WhatsApp"],
    },

    /* ---------- ABOUT / EXPERIENCE ---------- */
    {
      id: "about",
      match: ["about you", "who are you", "your experience", "years of experience", "background", "your skills", "resume", "cv", "qualifications", "certification", "what is your name", "your name", "tell me about yourself", "bio"],
      reply: () => {
        return [
          "I'm the digital twin of King Greatman Spirit 👑💻 — a Software Engineer, AI & ML Specialist, Data Analyst, Full-Stack Developer, and Cloud & Automation Expert.",
          "5+ years of building, 125+ projects delivered, clients in Nigeria and around the world. My toolkit: Python, Django, React, Node.js, TensorFlow, Power BI, Docker, Cloud & DevOps.",
          "Grab my full CV here 👉 <a href='/media/resume/Greatman_Justus_Unye-Awaji_Software_Engineer_Resume.pdf' target='_blank'>Download CV</a>",
          "Enough about me — what can we build for you? 😎",
        ];
      },
      chips: ["What services do you offer?", "How do I pay?", "Get a free quote"],
    },

    /* ---------- REFERRAL ---------- */
    {
      id: "referral",
      match: ["refer", "referral", "discount", "reward", "refer friend", "commission", "share link", "invite", "tell my friends", "my friends", "tell everyone", "word of mouth", "tell others", "friend"],
      reply: () => {
        return [
          "Love it — good people refer good people! 🤝✨",
          "Here's how it works:\n🎁 The friend you refer gets a 10% onboarding discount\n🎁 YOU get a reward when they start\n📣 One message is all it takes: share https://kinggreatmanspirit.com and tell them to mention your name",
          "That's exactly how this business grew — word of mouth from happy clients. Tell everyone you know! 😄",
        ];
      },
      chips: ["Start a project", "How do I pay?", "Chat on WhatsApp"],
    },

    /* ---------- PROCESS ---------- */
    {
      id: "process",
      match: ["process", "how it works", "how do we start", "steps", "get started", "begin", "kick off", "procedure", "onboarding", "what happens next", "next step", "tell me your idea", "i have an idea", "idea"],
      reply: () => {
        return [
          "Here's how we go from idea to launch 🚀",
          "1️⃣ You tell me your goal (form, WhatsApp, or email)\n2️⃣ I send a tailored plan + fixed quote within 24h\n3️⃣ You pay securely — Flutterwave, Paystack, or Binance\n4️⃣ I build with weekly updates\n5️⃣ We launch, train you, and support you",
          "Step 1 is free and takes 2 minutes — want to start now? 👉 <a href='/#contact' target='_blank'>Tell me your idea</a>",
        ];
      },
      chips: ["Tell me your idea", "How much?", "Pay securely"],
    },

    /* ---------- SECTORS ---------- */
    {
      id: "sectors",
      match: ["sector", "industry", "health", "healthcare", "hospital", "clinic", "finance", "fintech", "bank", "education", "school", "university", "ecommerce", "retail", "real estate", "property", "agriculture", "farming", "logistics", "delivery", "entertainment", "hotel", "restaurant", "church", "ngo", "startup", "small business", "government"],
      reply: () => {
        const sector = state.topic || "every industry";
        return [
          `We've built for virtually every sector — health, fintech, education, e-commerce, real estate, agriculture, logistics, entertainment, startups and more 🌍✨`,
          `Whatever your industry, the playbook is the same: the right digital product + smart data + a strategy that converts.`,
          `Tell me your sector and what you want to achieve — I'll tailor a solution that fits like a glove. 😊`,
        ];
      },
      chips: ["Get a free quote", "What services do you offer?", "How do I pay?"],
    },

    /* ---------- THANKS ---------- */
    {
      id: "thanks",
      match: ["thank", "thanks", "appreciate", "nice", "cool", "great info", "helpful", "awesome", "good bot", "love it"],
      reply: () => {
        return [
          `You're welcome${state.name ? ", " + state.name : ""}! 😊 Happy to help anytime.`,
          "If you know a friend or business that needs websites, apps or AI — telling them about me is the best thank-you ever. You both get rewarded too! 😉",
          "And when you're ready, I'd love to get you started. Just say the word! 🚀",
        ];
      },
      chips: ["Start a project", "How do I pay?", "Chat on WhatsApp"],
    },

    /* ---------- PAYMENT INTENT (direct) ---------- */
    {
      id: "hire",
      match: ["hire", "start a project", "i want to start", "let's begin", "lets start", "i want to pay", "buy", "patronize", "book", "reserve", "engage", "commission", "order", "purchase", "sign me up", "i'm ready", "im ready", "i am ready", "ready", "count me in", "let's work", "lets work", "kickoff", "kick off"],
      reply: () => {
        return [
          "YES! Let's make it happen 🎉 You're one step from greatness.",
          "Here's the fastest way to start:\n1️⃣ <a href='/#contact' target='_blank'>Send your project details</a>\n2️⃣ I reply with a plan + fixed quote within 24h\n3️⃣ Secure your slot with a deposit via <a href='/payment/' target='_blank'>Flutterwave, Paystack, or Binance</a>",
          "Slots are limited this month — the earlier you lock in, the sooner we ship. Ready when you are, chief! 🚀",
        ];
      },
      chips: ["Pay now securely", "Tell me your idea", "Chat on WhatsApp"],
    },

    /* ---------- BYE ---------- */
    {
      id: "bye",
      match: ["bye", "goodbye", "see you", "good night", "i'm done", "thats all", "that's all", "later", "gtg", "off now"],
      reply: () => {
        return [
          `It was great chatting, ${state.name || "friend"}! 👋 I'll be right here whenever you need me.`,
          "Don't forget — I build websites, apps and AI systems that make businesses unstoppable. The door is always open. 😊🚀",
        ];
      },
      chips: ["What services do you offer?", "Start a project"],
    },
  ];

  const escRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  const scoreIntent = (intent, msg) => {
    let score = 0;
    for (const kw of intent.match) {
      const word = kw.trim().replace(/[?.,!]/g, "");
      if (!word) continue;
      if (new RegExp("\\b" + escRe(word) + "s?\\b").test(msg)) score += word.length > 3 ? 2 : 1;
    }
    return score;
  };

  const pickIntent = (msg) => {
    let best = null;
    let bestScore = 0;
    for (const intent of KB) {
      const s = scoreIntent(intent, msg);
      if (s > bestScore) {
        bestScore = s;
        best = intent;
      }
    }
    return bestScore > 0 ? best : null;
  };

  /* ---------- name & budget capture ---------- */
  const tryCaptureName = (msg) => {
    if (state.askedName && !state.name && msg.length <= 40 && NAME_RE.test(msg.trim()) && !/\s{2,}/.test(msg)) {
      state.name = msg.trim().split(" ").map((w) => w[0].toUpperCase() + w.slice(1)).join(" ");
      try { localStorage.setItem("kgs_name", state.name); } catch (e) {}
      return true;
    }
    return false;
  };
  const tryCaptureBudget = (msg) => {
    if (state.askedBudget && !state.budget && BUDGET_RE.test(msg)) {
      state.budget = msg;
      return true;
    }
    return false;
  };
  const extractName = (raw) => {
    const m = NAME_PATTERN.exec(String(raw));
    if (!m) return "";
    const name = m[1].trim();
    if (name.length < 2 || /\d/.test(name)) return "";
    if (NAME_STOPWORDS.has(name.toLowerCase())) return "";
    return name;
  };

  /* ---------- sales nudge ---------- */
  const maybeNudge = async () => {
    if (state.nudgeDone || state.exchanges < 3) return;
    if (state.topic === "pay" || state.topic === "hire") return;
    state.nudgeDone = true;
    await sleep(900);
    await addBot(
      [
        "Quick heads-up 👀 — I still have a few project slots open this month, and early starters get the full onboarding discount.",
        "Want to lock yours? It takes 2 minutes. 😉",
      ],
      { chips: ["Pay now securely", "Get a free quote", "Chat on WhatsApp"] }
    );
  };

  /* ---------- fallback ---------- */
  const fallback = () => {
    return [
      "Hmm, I'm not 100% sure about that one 🤔 — but I'm pretty sure King can answer it!",
      "You can:\n🎧 Tap 'Talk to King directly' below for an instant live alert\n💬 <a href='https://wa.me/2349014155705' target='_blank'>Chat with King on WhatsApp</a>\n✉️ <a href='mailto:hello@kinggreatmanspirit.com'>Email him</a>",
      "Meanwhile — I can tell you about services, pricing, payments, or the portfolio. Try me! 😄",
    ];
  };

  /* ---------- responder ---------- */
  async function route(raw) {
    const msg = strip(raw);

    // capture replies to pending questions
    if (tryCaptureName(raw)) {
      state.askedName = false;
      state.topic = "intro";
      await addBot(
        [
          `${state.name}, that's a beautiful name! 😊`,
          "So — what can we build for you today? A website, a mobile app, an AI system, or something else entirely?",
        ],
        { chips: ["I need a website", "I need a mobile app", "I need AI", "I need data analytics", "Just exploring"] }
      );
      maybeNudge();
      return;
    }
    if (tryCaptureBudget(raw)) {
      state.askedBudget = false;
      state.budget = raw;
      await addBot(
        [
          `Perfect — noted: ${esc(raw)} 👌 That's a very workable range.`,
          "Next step is a free, no-obligation plan and exact quote. Send your idea via the <a href='/#contact' target='_blank'>contact form</a> or WhatsApp, and I'll respond within 24 hours!",
        ],
        { chips: ["Tell me your idea", "Pay securely", "How do I pay?"] }
      );
      maybeNudge();
      return;
    }

    const intent = pickIntent(msg);
    if (intent) {
      const result = intent.reply();
      const texts = Array.isArray(result) ? result : [result];
      state.topic = intent.id;
      await addBot(texts, { chips: intent.chips });
    } else {
      const texts = fallback();
      await addBot(texts, {
        chips: [{ label: "🎧 Talk to King directly", action: "ticket" }, "What services do you offer?", "How much does a website cost?", "How do I pay?"],
      });
    }
    maybeNudge();
  }

  async function respond(raw) {
    if (!state.name) {
      const extracted = extractName(raw);
      if (extracted) {
        state.name = extracted[0].toUpperCase() + extracted.slice(1);
        state.askedName = false;
        try { localStorage.setItem("kgs_name", state.name); } catch (e) {}
        const rest = strip(String(raw).replace(NAME_PATTERN, " "));
        if (rest) {
          await addBot([`Nice to meet you, ${state.name}! 😊 I'll remember that.`]);
          await route(rest);
        } else {
          await addBot(
            [
              `Nice to meet you, ${state.name}! 😊 I'll remember that.`,
              "So — what can we build for you today? A website, a mobile app, an AI system, or something else entirely?",
            ],
            { chips: ["I need a website", "I need a mobile app", "I need AI", "I need data analytics", "Just exploring"] }
          );
          maybeNudge();
        }
        return;
      }
    }
    await route(raw);
  }

  /* ========================================================
     Boot sequence
     ======================================================== */
  const boot = async () => {
    try {
      if (!sessionStorage.getItem("kgs_teaser")) {
        await sleep(2000);
        teaser.classList.add("show");
      }
    } catch (e) {}
    await sleep(2800);
    if (badge && !state.open) badge.style.display = "flex";
  };

  if (location.hash === "#chat") openChat();

  addBot(
    [
      state.name
        ? `Welcome back, ${state.name}! 👋 I'm the AI assistant of King Greatman Spirit — his digital twin, if you like. 🤖`
        : "Hi there! 👋 I'm the AI assistant of King Greatman Spirit — his digital twin, if you like. 🤖",
      "I can help you with websites, mobile apps, AI systems, data analytics, pricing, payments — anything! What brings you here today?",
    ],
    { chips: ["What services do you offer?", "How much does a website cost?", "Do you build mobile apps?", "How do I pay?", { label: "🎧 Talk to King directly", action: "ticket" }] }
  );
    boot();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
