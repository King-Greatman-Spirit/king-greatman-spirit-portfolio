"""
Strict input validation & autocorrect for the contact form and newsletter.

- Rejects gibberish, spam words, repeated characters, doubled words,
  all-caps shouting, link-only messages and bot patterns.
- Auto-corrects common sloppiness (trimming, casing, spacing).
"""
import re

# ---------------------------------------------------------------
# Regexes
# ---------------------------------------------------------------
NAME_RE = re.compile(r"^[A-Za-z\u00C0-\u00FF' .-]{2,60}$")            # letters, accents, apostrophe, dot, space, hyphen
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]{2,64}@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\+?[0-9]{7,15}$")
REPEAT_CHAR_RE = re.compile(r"(.)\1{2,}")                              # aaa, 111, ...
REPEAT_WORD_RE = re.compile(r"\b(\w{2,})\b\s+\1\b", re.IGNORECASE)     # "hello hello"
URL_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
EMAIL_SIGN_RE = re.compile(r"[@]")
ONLY_NUMERIC_RE = re.compile(r"^[0-9 .\-+()]+$")
NUMBER_RE = re.compile(r"\d")
VOWEL_RE = re.compile(r"[aeiouy]", re.IGNORECASE)
KEYBOARD_GIBBERISH_RE = re.compile(
    r"(asdf|qwerty|zxcv|tyui|fghj|hjkl|poiu|lkj|mnbvc|xswq|zaq1)", re.IGNORECASE
)
SPAM_REPEATED_PUNCT = re.compile(r"[!?.]{5,}")

# ---------------------------------------------------------------
# Spam / abuse vocabulary
# ---------------------------------------------------------------
SPAM_WORDS = (
    "viagra", "casino", "lottery", "winner", "prize claim", "free bitcoin", "bitcoin giveaway",
    "crypto bonus", "double your money", "make money fast", "earn money", "earn $", "payday",
    "seo backlinks", "buy followers", "cheap pills", "pharmacy", "cialis", "penis",
    "mortgage", "loan offer", "urgent loan", "quick loan", "inheritance", "bank transfer fee",
    "prince", "diamond offer", "gold bars", "western union", "moneygram", "work from home",
    "click here", "act now", "100% guaranteed", "limited offer", "urgent business proposal",
    "investment opportunity", "fx trade", "forex signal", "porn", "sex ", "nude", "escort",
    "dating site", "hack ", "hacker", "crack software", "keygen", "military pay", "irs",
)

# ---------------------------------------------------------------
# Autocorrect / normalisation
# ---------------------------------------------------------------
LOWERCASE_PARTICLES = {"de", "la", "le", "du", "van", "von", "der", "di", "da", "del", "el", "al", "bin", "ibn"}


def autocorrect_name(raw):
    """Trim, collapse spaces, fix casing. 'john  doe' -> 'John Doe', 'MAC donald' -> 'Mac Donald'."""
    if not raw:
        return ""
    value = re.sub(r"\s+", " ", raw.strip())
    words = value.split(" ")
    cleaned = []
    for word in words:
        word = word.strip(" .,")
        if not word:
            continue
        low = word.lower()
        if low in LOWERCASE_PARTICLES:
            cleaned.append(low)
        elif word.isupper() and len(word) > 3:
            cleaned.append(word.title())
        else:
            cleaned.append(word[:1].upper() + word[1:])
    return " ".join(cleaned)


def autocorrect_email(raw):
    """Trim + lowercase. Gmail addresses tolerate dots but we keep them verbatim."""
    if not raw:
        return ""
    return re.sub(r"\s+", "", raw.strip()).lower()


def autocorrect_message(raw):
    """Trim, collapse whitespace/newlines, fix lowercase 'i' and stray double spaces."""
    if not raw:
        return ""
    value = re.sub(r"[ \t]+", " ", raw.strip())
    value = re.sub(r"\n{3,}", "\n\n", value)
    value = re.sub(r"\bi\b", "I", value)
    value = re.sub(r"\bi'm\b", "I'm", value, flags=re.IGNORECASE)
    return value


def autocorrect_phone(raw):
    """Strip spaces, dashes and parentheses; keep + and digits."""
    if not raw:
        return ""
    return re.sub(r"[^+0-9]", "", raw.strip())


# ---------------------------------------------------------------
# Quality checks
# ---------------------------------------------------------------
def _is_gibberish(text):
    """Repeated chars, keyboard rows, or long vowel-less runs."""
    compact = re.sub(r"[^A-Za-z]", "", text)
    if not compact:
        return False
    if REPEAT_CHAR_RE.search(compact):
        return True
    if KEYBOARD_GIBBERISH_RE.search(compact):
        return True
    if len(compact) >= 12 and not VOWEL_RE.search(compact):
        return True
    return False


def _has_spam_words(text):
    low = " " + text.lower() + " "
    for word in SPAM_WORDS:
        if word in low:
            return True
    return False


def _is_shouting(text):
    letters = [ch for ch in text if ch.isalpha()]
    if len(letters) < 12:
        return False
    upper = sum(1 for ch in letters if ch.isupper())
    return upper / len(letters) > 0.7


def _is_link_only(text):
    compact = text.strip()
    if not compact:
        return False
    return bool(URL_RE.search(compact)) and not re.search(r"[A-Za-z]{3,}\s", compact)


# ---------------------------------------------------------------
# Public validators — return None or an error string
# ---------------------------------------------------------------
def validate_name(name):
    if not name:
        return "Please enter your full name."
    if len(name) > 60:
        return "Your name looks too long — please keep it under 60 characters."
    if not NAME_RE.match(name):
        return "That name doesn't look right. Please use letters only (no numbers or symbols)."
    if NUMBER_RE.search(name):
        return "Names can't contain numbers — please enter your real name."
    if EMAIL_SIGN_RE.search(name):
        return "Please enter your name, not an email address."
    if _is_gibberish(name):
        return "That name looks like gibberish — please enter your real name."
    if _has_spam_words(name):
        return "That input looks like spam — please enter your real name."
    return None


def validate_email(email):
    if not email:
        return "Please enter your email address."
    if not EMAIL_RE.match(email):
        return "That email address doesn't look valid — e.g. name@example.com."
    local, _, domain = email.partition("@")
    if _is_gibberish(local) or len(local) > 64:
        return "That email address looks suspicious — please use a real one."
    if _has_spam_words(local) or _has_spam_words(domain):
        return "That email address looks like spam."
    if not domain.count("."):
        return "That email address is missing a valid domain (e.g. .com)."
    return None


def validate_phone(phone):
    if not phone:
        return None
    if not PHONE_RE.match(phone):
        return "That phone number looks invalid — use 7–15 digits, optionally starting with +."
    return None


def validate_message(message):
    if not message:
        return "Please write a short message about your request."
    length = len(message)
    if length < 10:
        return "Your message is too short — tell me a little more (at least 10 characters)."
    if length > 500:
        return "Please keep your message under 500 characters."
    if _is_gibberish(message):
        return "That message looks like gibberish — please describe your request in real words."
    if _has_spam_words(message):
        return "Your message was flagged as spam. Please write a genuine message."
    if REPEAT_WORD_RE.search(message):
        return "Please remove duplicated words from your message."
    if SPAM_REPEATED_PUNCT.search(message):
        return "Please don't use excessive punctuation in your message."
    if _is_shouting(message):
        return "Please write your message in normal case — no shouting."
    if _is_link_only(message):
        return "Please add a short description along with any links."
    if message.count("http") > 3:
        return "Too many links in one message — please remove some."
    return None


def validate_contact_payload(full_name, email, phone, message):
    errors = []
    for err in (validate_name(full_name), validate_email(email), validate_phone(phone), validate_message(message)):
        if err:
            errors.append(err)
    return errors


def validate_subscribe_email(email):
    return validate_email(email)
