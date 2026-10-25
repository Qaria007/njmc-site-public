#!/usr/bin/env python3
"""Build the "Free gifts" section of drqaria.njmcmedicsupp.com.

    python3 .automation/drqaria/gifts/build-gifts.py            # pages + PDFs
    python3 .automation/drqaria/gifts/build-gifts.py --no-pdf   # pages only

Writes drqaria/gifts/** (index in EN, AR, ZH; one folder per gift with EN, AR,
ZH pages), drqaria/assets/gifts.css and drqaria/gifts/pdf/*.pdf (one A4 page
each, printed with headless Google Chrome from a print layout that uses the
Mac's own fonts, because this Mac cannot reach Google Fonts).

All wording comes from the recording scripts in Drive (Dr Qaria Personal
Brand > 02 Videos > START HERE - Video N ...). Facts: brand-facts.md. Rules:
no em or en dashes, name "Dr. Qaria", no supplier or client names, no prices,
no country in brand lines, one matching service per gift, one plain sentence.
To add a gift: append to GIFTS and run this script again.
"""
import os, sys, subprocess, tempfile, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SITE = os.path.join(ROOT, "drqaria")
HOST = "https://drqaria.njmcmedicsupp.com"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# ---------------------------------------------------------------- languages
L = {
    "en": dict(code="en", dir="ltr", sub="", name="Dr. Qaria",
               title="Biomedical scientist, two PhDs",
               tagline="Science, made simple with AI.",
               fonts="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap",
               n_home="Home", n_writing="Writing", n_gifts="Free gifts", n_contact="Contact",
               writing_url="/writing.html", lang_label="Language",
               open_page="Open the page", download="Download the PDF (one page)",
               all_gifts="All gifts", more="More gifts come with the next videos.",
               from_video="From Video {n}", free_gift="Free gift",
               email="E-mail", whatsapp="WhatsApp", site_label="Website",
               copy_hint="Copy it. Fill the brackets. Send it.",
               og_locale="en_US"),
    "ar": dict(code="ar", dir="rtl", sub="ar/", name="د. قاريه",
               title="عالم في العلوم الطبية الحيوية، حاصل على درجتي دكتوراه",
               tagline="العلم، ببساطة، مع الذكاء الاصطناعي.",
               fonts="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&family=Amiri:wght@400;700&display=swap",
               n_home="الرئيسية", n_writing="مقالات", n_gifts="هدايا مجانية", n_contact="تواصل معي",
               writing_url="/writing-ar.html", lang_label="اللغة",
               open_page="افتح الصفحة", download="حمّل ملف PDF (صفحة واحدة)",
               all_gifts="كل الهدايا", more="هدايا أخرى تأتي مع الفيديوهات القادمة.",
               from_video="من الفيديو {n}", free_gift="هدية مجانية",
               email="البريد الإلكتروني", whatsapp="واتساب", site_label="الموقع",
               copy_hint="انسخها. املأ الأقواس. أرسلها.",
               og_locale="ar_AR"),
    "zh": dict(code="zh", dir="ltr", sub="zh/", name="Qaria 博士",
               title="生物医学科学家，双博士",
               tagline="科学，用 AI 变简单。",
               fonts="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
               n_home="首页", n_writing="文章", n_gifts="免费礼物", n_contact="联系",
               writing_url="/writing.html", lang_label="语言",
               open_page="打开页面", download="下载 PDF（一页）",
               all_gifts="全部礼物", more="更多礼物随下一期视频推出。",
               from_video="来自第 {n} 集", free_gift="免费礼物",
               email="邮箱", whatsapp="WhatsApp", site_label="网站",
               copy_hint="复制它。填好括号。发出去。",
               og_locale="zh_CN"),
}
LANG_NAMES = {"en": "English", "ar": "العربية", "zh": "中文"}

# ------------------------------------------------------------------ contacts
# Official addresses only (brand sites, 21 Oct 2026). Never contact@optelux.com.
BRANDS = [
    dict(name="NJMC Medical Supplies", site="njmcmedicsupp.com", url="https://njmcmedicsupp.com",
         email="sale@njmcmedicsupp.com", wa_num="+86 132 4453 6191", wa_url="https://wa.me/8613244536191"),
    dict(name="PharmaTrust", site="pharmatrust.tech", url="https://pharmatrust.tech",
         email="info@pharmatrust.tech", wa_num=None, wa_url=None),
    dict(name="AI Employees", site="phmnai.com", url="https://phmnai.com",
         email="contact@phmnai.com", wa_num="+86 188 6087 6679", wa_url="https://wa.me/message/SOT7YTN6PXCMK1"),
]

# -------------------------------------------------------------------- index
INDEX = {
    "en": dict(title="Free gifts from my videos | Dr. Qaria",
               desc="One short page per video, in English, Arabic and Chinese: the checklist or template from the video, free, to use today.",
               h1="Free gifts from my videos",
               standfirst="One short page per video. Something you can use today. Choose your language above, then pick your gift."),
    "ar": dict(title="هدايا مجانية من فيديوهاتي | د. قاريه",
               desc="صفحة قصيرة لكل فيديو، بالعربية والإنجليزية والصينية: القائمة أو النموذج من الفيديو، مجاناً، لتستخدمه اليوم.",
               h1="هدايا مجانية من فيديوهاتي",
               standfirst="صفحة قصيرة لكل فيديو. شيء تستخدمه اليوم. اختر لغتك في الأعلى، ثم اختر هديتك."),
    "zh": dict(title="我的视频免费礼物 | Qaria 博士",
               desc="每个视频一页，中文、英文、阿拉伯文：视频里的清单或模板，免费，今天就能用。",
               h1="我的视频免费礼物",
               standfirst="每个视频一页。今天就能用。先在上方选语言，再选你的礼物。"),
}

# -------------------------------------------------------------------- gifts
# Each gift: slug (folder), video number, pdf base name, and per language:
# title, desc, standfirst, items [(heading, line)], sections [(heading, [lines])],
# callout [lines], service (sentence, link text, url), card (short text for the index).
GIFTS = [
 dict(slug="website", video=4, pdf="5-things-every-business-website-needs", kind="list",
  en=dict(title="5 things every business website needs",
          desc="The five-point checklist from Video 4: contact on every page, one page per product, buyer questions answered, clear company facts, your buyers' languages.",
          standfirst="Check your website tonight. Five things it needs.",
          items=[("Contact on every page", "Phone and e-mail on every page."),
                 ("One page per product", "One page for each product."),
                 ("Buyer questions, answered", "The questions buyers ask, with your answers."),
                 ("Company facts, written clearly", "Clear facts about your company."),
                 ("Your buyers' languages", "The languages your buyers speak.")],
          sections=[("Three words you will hear",
                     ["SEO: Google finds your page.",
                      "AEO: the short answer on top comes from your page.",
                      "GEO: ChatGPT and Gemini name your company.",
                      "Three names. One goal. Buyers find you."])],
          callout=["Nobody can promise you page one. Not Google. Not ChatGPT. Not me.",
                   "AI can write your pages fast. But only you know your facts. So read every line before it goes online.",
                   "The AI writes. You decide."],
          service=("If you want help with your website or its pages, AI Employees does this work.", "phmnai.com", "https://phmnai.com/"),
          card="The five-point checklist from the video. Check your website tonight."),
  ar=dict(title="5 أشياء يحتاجها كل موقع شركة",
          desc="قائمة النقاط الخمس من الفيديو 4: التواصل في كل صفحة، صفحة لكل منتج، أسئلة المشترين مع الإجابات، معلومات الشركة بوضوح، لغات مشتريك.",
          standfirst="افحص موقعك الليلة. خمسة أشياء يحتاجها.",
          items=[("التواصل في كل صفحة", "الهاتف والبريد الإلكتروني في كل صفحة."),
                 ("صفحة لكل منتج", "صفحة واحدة لكل منتج."),
                 ("أسئلة المشترين مع الإجابات", "الأسئلة التي يطرحها المشترون، مع إجاباتك."),
                 ("معلومات الشركة مكتوبة بوضوح", "معلومات واضحة عن شركتك."),
                 ("لغات مشتريك", "اللغات التي يتكلمها مشتروك.")],
          sections=[("ثلاث كلمات ستسمعها",
                     ["SEO: جوجل يجد صفحتك.",
                      "AEO: الإجابة القصيرة في أعلى البحث تأتي من صفحتك.",
                      "GEO: ChatGPT وGemini يذكران شركتك.",
                      "ثلاثة أسماء. هدف واحد: أن يجدك المشترون."])],
          callout=["لا أحد يستطيع أن يعدك بالصفحة الأولى. لا جوجل، ولا ChatGPT، ولا أنا.",
                   "يمكن للذكاء الاصطناعي أن يكتب صفحاتك بسرعة. لكن أنت وحدك تعرف معلوماتك. فاقرأ كل سطر قبل أن يُنشر.",
                   "الذكاء الاصطناعي يكتب، وأنت تقرر."],
          service=("إن أردت مساعدة في موقعك أو صفحاته، فهذا عمل AI Employees.", "phmnai.com/ar", "https://phmnai.com/ar"),
          card="قائمة النقاط الخمس من الفيديو. افحص موقعك الليلة."),
  zh=dict(title="企业网站必备 5 点",
          desc="第 4 集的 5 点清单：每页都有联系方式，每个产品一个页面，买家常问的问题和答案，公司信息写清楚，用买家的语言。",
          standfirst="今晚检查你的网站。它需要这 5 点。",
          items=[("每页都有联系方式", "每一页都有电话和邮箱。"),
                 ("每个产品一个页面", "每个产品一个单独的页面。"),
                 ("买家常问的问题和答案", "买家常问的问题，和你的回答。"),
                 ("公司信息写清楚", "关于你公司的清楚信息。"),
                 ("用买家的语言", "买家使用的语言。")],
          sections=[("你会听到的三个词",
                     ["SEO：谷歌等搜索引擎找到你的网页。",
                      "AEO：搜索结果顶部的简短答案来自你的网页。",
                      "GEO：ChatGPT、Gemini 等 AI 助手提到你的公司。",
                      "三个名字，一个目标：让买家找到你。"])],
          callout=["没有人能保证排在第一页。谷歌不能，ChatGPT 不能，我也不能。",
                   "AI 能很快写出你的网页。但只有你清楚自己公司的真实情况。所以上线前，每一行都要读一遍。",
                   "AI 负责写，你来决定。"],
          service=("如果你需要网站或网页内容方面的帮助，AI Employees 可以做这件事。", "phmnai.com", "https://phmnai.com/"),
          card="视频里的 5 点清单。今晚就检查你的网站。"),
 ),
 dict(slug="first-message", video=6, pdf="your-first-message-to-a-new-buyer-5-lines", kind="template",
  en=dict(title="Your first message to a new buyer: 5 lines",
          desc="The five-line first message from Video 6: what you make and for whom, who you are, one fact that helps them, one question, your WhatsApp or WeChat.",
          standfirst="Here is a first message. Five lines. Copy it.",
          items=[("Hello [name], we make [product] for [kind of buyer].", "Line one: what you make, and who it is for."),
                 ("I am [you] from [company].", "Line two: who you are."),
                 ("[One fact that helps them.]", "Line three: one fact that helps them."),
                 ("[One question.]", "Line four: one question."),
                 ("WhatsApp or WeChat: [number]", "Line five: your WhatsApp or WeChat.")],
          sections=[("The basics we keep",
                     ["Start with your product. What you sell, in one line.",
                      "About 150 words. No long story.",
                      "Send it from your company's own e-mail.",
                      "Say what they should do next."]),
                    ("Two things we are changing now",
                     ["Check every address first.",
                      "Then write again, where buyers chat. WhatsApp. WeChat. Not only e-mail."])],
          callout=["Will this work? I do not know. We are testing it now.",
                   "AI can write the e-mail. You decide what is true, and what you send."],
          service=("If you want help writing to buyers and answering them on WhatsApp, AI Employees does this work.", "phmnai.com", "https://phmnai.com/"),
          card="The template from the video. Copy it, fill the brackets, send it."),
  ar=dict(title="رسالتك الأولى إلى مشترٍ جديد: 5 أسطر",
          desc="رسالة أولى من خمسة أسطر من الفيديو 6: ماذا تصنع ولمن، من أنت، معلومة تفيدهم، سؤال واحد، ورقم واتساب أو وي تشات.",
          standfirst="هذه رسالة أولى. خمسة أسطر. انسخها.",
          items=[("مرحباً [الاسم]، نصنع [المنتج] ونبيعه إلى [نوع المشتري].", "السطر الأول: ماذا تصنع، ولمن."),
                 ("أنا [اسمك] من [الشركة].", "السطر الثاني: من أنت."),
                 ("[معلومة واحدة تفيدهم.]", "السطر الثالث: معلومة واحدة تفيدهم."),
                 ("[سؤال واحد.]", "السطر الرابع: سؤال واحد."),
                 ("واتساب أو وي تشات: [الرقم]", "السطر الخامس: رقم واتساب أو وي تشات الخاص بك.")],
          sections=[("الأساسيات التي نحتفظ بها",
                     ["ابدأ بمنتجك. ما تبيعه، في سطر واحد.",
                      "نحو 150 كلمة. بلا قصة طويلة.",
                      "أرسلها من بريد شركتك.",
                      "قل لهم ما الخطوة التالية."]),
                    ("شيئان نغيّرهما الآن",
                     ["افحص كل عنوان بريد أولاً.",
                      "ثم اكتب مرة أخرى حيث يتكلم المشترون. واتساب. وي تشات. ليس البريد فقط."])],
          callout=["هل سينجح هذا؟ لا أعرف. نجربه الآن.",
                   "يمكن للذكاء الاصطناعي أن يكتب الرسالة. وأنت تقرر ما هو صحيح، وما ترسله."],
          service=("إن أردت مساعدة في الكتابة إلى المشترين والرد عليهم على واتساب، فهذا عمل AI Employees.", "phmnai.com/ar", "https://phmnai.com/ar"),
          card="النموذج من الفيديو. انسخه، واملأ الأقواس، وأرسله."),
  zh=dict(title="给新买家的第一条消息：5 行",
          desc="第 6 集的 5 行开发信模板：做什么产品、卖给谁，你是谁，一条有用信息，一个问题，你的 WhatsApp 或微信。",
          standfirst="这是一条首次联系买家的消息。五行。复制它。",
          items=[("您好[姓名]，我们为[买家类型]生产[产品]。", "第一行：你做什么，给谁。"),
                 ("我是[公司]的[你的名字]。", "第二行：你是谁。"),
                 ("[一条对他们有用的信息。]", "第三行：一条对他们有用的信息。"),
                 ("[一个问题。]", "第四行：一个问题。"),
                 ("WhatsApp 或微信：[号码]", "第五行：你的 WhatsApp 或微信。")],
          sections=[("我们保留的基本做法",
                     ["先说产品。你卖什么，一句话。",
                      "约 150 个英文单词。不讲长故事。",
                      "用公司自己的邮箱发。",
                      "告诉他们下一步做什么。"]),
                    ("我们现在改的两点",
                     ["先核对每一个邮箱地址。",
                      "然后在买家聊天的地方再写一次。WhatsApp。微信。不只是邮件。"])],
          callout=["这样有用吗？我不知道。我们正在测试。",
                   "AI 可以写邮件。什么是真的、发什么，你来决定。"],
          service=("如果你需要有人帮你写给买家、并在 WhatsApp 上回复，AI Employees 可以做这件事。", "phmnai.com", "https://phmnai.com/"),
          card="视频里的模板。复制，填好括号，发出去。"),
 ),
]

# ------------------------------------------------------------------ helpers
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def index_url(lang):   return "/gifts/" + L[lang]["sub"]
def gift_url(g, lang): return f"/gifts/{g['slug']}/" + L[lang]["sub"]
def pdf_url(g, lang):  return f"/gifts/pdf/{g['pdf']}-{lang}.pdf"

def hreflangs(urlf):
    out = [f'  <link rel="alternate" hreflang="{l}" href="{HOST}{urlf(l)}" />' for l in L]
    out.append(f'  <link rel="alternate" hreflang="x-default" href="{HOST}{urlf("en")}" />')
    return "\n".join(out)

def pills(lang, urlf):
    t = L[lang]
    items = ""
    for l in L:
        on = ' class="on" aria-current="page"' if l == lang else ""
        items += f'<a href="{urlf(l)}" lang="{l}"{on}>{LANG_NAMES[l]}</a>'

    return f'<div class="lang-pills" role="navigation" aria-label="{t["lang_label"]}"><span>{t["lang_label"]}</span>{items}</div>'

def head(lang, title, desc, url, urlf):
    t = L[lang]
    return f"""<!DOCTYPE html>
<html lang="{t['code']}" dir="{t['dir']}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="canonical" href="{HOST}{url}" />
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large" />
  <meta name="author" content="Dr. Qaria" />
{hreflangs(urlf)}
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Dr. Qaria" />
  <meta property="og:locale" content="{t['og_locale']}" />
  <meta property="og:url" content="{HOST}{url}" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="{t['fonts']}" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/writing.css?v=1" />
  <link rel="stylesheet" href="/assets/gifts.css?v=1" />
  <link rel="icon" href="/favicon.ico" />
</head>
<body{' dir="rtl"' if t['dir'] == 'rtl' else ''} class="lang-{lang}">

<nav>
  <div class="nav-inner">
    <a class="nav-brand" href="/">{'Dr. <span>Qaria</span>' if lang != 'ar' else 'د. <span>قاريه</span>'}</a>
    <ul class="nav-links">
      <li><a href="{'/index-ar.html' if lang == 'ar' else '/'}">{t['n_home']}</a></li>
      <li><a href="{t['writing_url']}">{t['n_writing']}</a></li>
      <li><a href="{index_url(lang)}">{t['n_gifts']}</a></li>
      <li><a href="{'/index-ar.html#contact' if lang == 'ar' else '/#contact'}" class="nav-cta">{t['n_contact']}</a></li>
    </ul>
  </div>
</nav>
"""

def who(lang):
    t = L[lang]
    return f"""    <div class="who">
      <div class="who-name">{t['name']}</div>
      <div class="who-title">{t['title']}</div>
      <div class="who-tag">{t['tagline']}</div>
    </div>
"""

def footer(lang):
    t = L[lang]
    cards = []
    for b in BRANDS:
        rows = [f'<a href="{b["url"]}" target="_blank" rel="noopener">{b["site"]}</a>',
                f'<span>{t["email"]}:</span> <a href="mailto:{b["email"]}">{b["email"]}</a>']
        if b["wa_num"]:
            rows.append(f'<span>{t["whatsapp"]}:</span> <a href="{b["wa_url"]}" target="_blank" rel="noopener" dir="ltr">{b["wa_num"]}</a>')
        cards.append(f'    <div class="brand"><strong>{b["name"]}</strong>' + "".join(f"<div>{r}</div>" for r in rows) + "</div>")
    return f"""
<footer class="gift-footer">
  <div class="footer-brands">
{chr(10).join(cards)}
  </div>
  <p class="footer-who">{t['name']} &middot; {t['title']} &middot; {t['tagline']}</p>
  <p>&copy; 2026 {t['name']} &middot; <a href="{HOST}/">drqaria.njmcmedicsupp.com</a></p>
</footer>

</body>
</html>
"""

# -------------------------------------------------------------------- pages
def build_index(lang):
    t, c = L[lang], INDEX[lang]
    url = index_url(lang)
    html = head(lang, c["title"], c["desc"], url, index_url)
    html += f"""
<header class="page-head">
  <div class="page-head-inner">
    <div class="breadcrumb"><a href="{'/index-ar.html' if lang == 'ar' else '/'}">{t['n_home']}</a> / {t['n_gifts']}</div>
{who(lang)}
    {pills(lang, index_url)}
    <h1>{c['h1']}</h1>
    <p class="standfirst">{c['standfirst']}</p>
  </div>
</header>

<main class="gift-list">
"""
    for g in GIFTS:
        gc = g[lang]
        html += f"""  <article class="gift-card">
    <div class="badge">{t['from_video'].format(n=g['video'])} &middot; {t['free_gift']}</div>
    <h2><a href="{gift_url(g, lang)}">{gc['title']}</a></h2>
    <p>{gc['card']}</p>
    <div class="gift-actions">
      <a class="btn-primary" href="{gift_url(g, lang)}">{t['open_page']}</a>
      <a class="btn-secondary" href="{pdf_url(g, lang)}" download>{t['download']}</a>
    </div>
  </article>
"""
    html += f"""  <p class="empty-note">{t['more']}</p>
</main>
"""
    html += footer(lang)
    write(os.path.join(SITE, "gifts", t["sub"], "index.html"), html)

def build_gift(g, lang):
    t, gc = L[lang], g[lang]
    url = gift_url(g, lang)
    urlf = lambda l: gift_url(g, l)
    html = head(lang, f"{gc['title']} | {t['name']}", gc["desc"], url, urlf)
    html += f"""
<header class="page-head">
  <div class="page-head-inner">
    <div class="breadcrumb"><a href="{'/index-ar.html' if lang == 'ar' else '/'}">{t['n_home']}</a> / <a href="{index_url(lang)}">{t['n_gifts']}</a></div>
{who(lang)}
    {pills(lang, urlf)}
    <div class="badge">{t['from_video'].format(n=g['video'])} &middot; {t['free_gift']}</div>
    <h1>{gc['title']}</h1>
    <p class="standfirst">{gc['standfirst']}</p>
    <p class="head-actions"><a class="btn-primary" href="{pdf_url(g, lang)}" download>{t['download']}</a></p>
  </div>
</header>

<main class="article gift">
  <ol class="gift-items {g['kind']}">
"""
    for h, line in gc["items"]:
        html += f"    <li><strong>{h}</strong><span>{line}</span></li>\n"
    html += "  </ol>\n"
    if g["kind"] == "template":
        html += f"  <p class=\"copy-hint\">{t['copy_hint']}</p>\n"
    for h, lines in gc["sections"]:
        html += f"  <h2>{h}</h2>\n" + "".join(f"  <p>{p}</p>\n" for p in lines)
    html += '  <div class="callout">\n' + "".join(f"    <p>{p}</p>\n" for p in gc["callout"]) + "  </div>\n"
    s, label, link = gc["service"]
    html += f"""  <p class="service">{s}<br><a href="{link}" target="_blank" rel="noopener">{label}</a></p>
  <p class="back"><a href="{index_url(lang)}">{t['all_gifts']}</a></p>
</main>
"""
    html += footer(lang)
    write(os.path.join(SITE, "gifts", g["slug"], t["sub"], "index.html"), html)

CSS = """/* Dr. Qaria, Free gifts section. Loaded after writing.css; only adds. */
.who { margin: 6px 0 22px; }
.who-name { font-family: 'Playfair Display', serif; font-size: 1.35rem; color: var(--navy); font-weight: 700; }
body[dir="rtl"] .who-name { font-family: 'Amiri', serif; }
.who-title { color: var(--text-muted); font-size: 0.95rem; }
.who-tag { color: var(--teal); font-size: 0.9rem; font-weight: 600; margin-top: 2px; }
.lang-pills { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 0 0 26px; }
.lang-pills span { font-size: 0.8rem; color: var(--text-muted); margin-inline-end: 4px; }
.lang-pills a { border: 1px solid var(--border); border-radius: 20px; padding: 6px 16px; font-size: 0.88rem;
  color: var(--navy); text-decoration: none; background: var(--white); font-weight: 500; }
.lang-pills a:hover { border-color: var(--teal); color: var(--teal); }
.lang-pills a.on { background: var(--teal); border-color: var(--teal); color: #fff; }
.lang-pills a[lang="ar"] { font-family: 'Tajawal', 'Geeza Pro', sans-serif; }
.lang-pills a[lang="zh"] { font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Noto Sans SC', sans-serif; }
.head-actions { margin-top: 24px; }
.gift-list { max-width: 900px; margin: 0 auto; padding: 56px 24px 56px; }
.gift-card { border: 1px solid var(--border); border-radius: 12px; padding: 28px 30px; margin-bottom: 20px; }
.gift-card .badge { margin-bottom: 14px; }
.gift-card h2 { font-family: 'Playfair Display', serif; font-size: 1.4rem; color: var(--navy); line-height: 1.32; margin-bottom: 10px; }
body[dir="rtl"] .gift-card h2 { font-family: 'Amiri', serif; }
.gift-card h2 a { color: inherit; text-decoration: none; }
.gift-card h2 a:hover { color: var(--teal); }
.gift-card p { color: var(--text-muted); font-size: 0.95rem; margin-bottom: 18px; }
.gift-actions { display: flex; flex-wrap: wrap; gap: 12px; }
.btn-secondary { display: inline-block; border: 1px solid var(--teal); color: var(--teal); padding: 12px 24px; border-radius: 7px;
  text-decoration: none; font-weight: 600; font-size: 0.92rem; }
.btn-secondary:hover { background: rgba(13,124,102,0.08); }
.gift { padding-top: 44px; }
.gift-items { list-style: none; margin: 0 0 8px 0 !important; padding: 0; counter-reset: gift; }
.gift-items li { counter-increment: gift; display: grid; grid-template-columns: 44px 1fr; gap: 4px 18px; padding: 18px 0; border-top: 1px solid var(--border); }
.gift-items li:last-child { border-bottom: 1px solid var(--border); }
.gift-items li::before { content: counter(gift); grid-row: 1 / span 2; width: 44px; height: 44px; border-radius: 50%; background: var(--teal); color: #fff;
  font-weight: 700; font-size: 1.1rem; display: flex; align-items: center; justify-content: center; font-family: 'Inter', sans-serif; }
.gift-items li strong { color: var(--navy); font-size: 1.12rem; font-weight: 600; line-height: 1.4; align-self: end; }
.gift-items li span { color: var(--text-muted); }
.gift-items.template li strong { font-weight: 500; background: var(--light-bg); border-radius: 8px; padding: 10px 14px; }
.copy-hint { color: var(--teal); font-weight: 600; margin: 14px 0 0; }
.service { background: var(--light-bg); border-radius: 10px; padding: 20px 24px; margin-top: 36px; }
.service a { font-weight: 600; }
.back { margin-top: 28px; }
.back a { border-bottom: none !important; font-weight: 600; }
.gift-footer .footer-brands { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; max-width: 900px; margin: 0 auto 24px; text-align: start; }
.gift-footer .brand strong { display: block; color: #fff; margin-bottom: 6px; font-size: 0.95rem; }
.gift-footer .brand div { line-height: 1.75; }
.gift-footer .brand span { color: rgba(255,255,255,0.5); }
.gift-footer .footer-who { color: rgba(255,255,255,0.85); margin-bottom: 8px; }
body.lang-zh, body.lang-zh .page-head h1, body.lang-zh .article h2, body.lang-zh .who-name, body.lang-zh .gift-card h2 {
  font-family: 'Inter', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Noto Sans SC', sans-serif; letter-spacing: 0; }
body[dir="rtl"] .gift-items li span, body[dir="rtl"] .who-title { font-size: 1.02rem; }
@media (max-width: 768px) {
  .gift-footer .footer-brands { grid-template-columns: 1fr; text-align: center; }
  .gift-items li { grid-template-columns: 36px 1fr; gap: 4px 14px; }
  .gift-items li::before { width: 36px; height: 36px; font-size: 1rem; }
}
"""

# ---------------------------------------------------------------------- PDF
PRINT_CSS = """
@page { size: A4; margin: 13mm 15mm 12mm 15mm; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #2c3547; font-size: 10.6pt; line-height: 1.5; }
body[dir="rtl"] { font-family: 'Geeza Pro', 'SF Arabic', 'Baghdad', sans-serif; font-size: 11.2pt; }
body.lang-zh { font-family: 'PingFang SC', 'Hiragino Sans GB', 'Songti SC', sans-serif; }
.top { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid #0d7c66; padding-bottom: 7px; margin-bottom: 14px; }
.top .name { font-family: Georgia, 'Times New Roman', serif; font-size: 15pt; color: #1a2744; font-weight: 700; }
body[dir="rtl"] .top .name, body.lang-zh .top .name { font-family: inherit; }
.top .title { color: #6b7280; font-size: 9.2pt; }
.top .tag { color: #0d7c66; font-size: 9.2pt; font-weight: 600; text-align: end; }
.badge { display: inline-block; background: rgba(13,124,102,0.09); color: #0d7c66; border-radius: 12px; padding: 2px 10px; font-size: 8.4pt; font-weight: 600; margin-bottom: 8px; }
h1 { font-family: Georgia, 'Times New Roman', serif; font-size: 21pt; line-height: 1.2; color: #1a2744; margin-bottom: 5px; }
body[dir="rtl"] h1, body.lang-zh h1 { font-family: inherit; }
.standfirst { color: #6b7280; font-size: 11.4pt; margin-bottom: 10px; }
ol { list-style: none; counter-reset: gift; margin: 0; }
ol li { counter-increment: gift; display: grid; grid-template-columns: 24px 1fr; gap: 0 10px; padding: 6.5px 0; border-top: 1px solid #e2e8f0; align-items: center; }
ol li:last-child { border-bottom: 1px solid #e2e8f0; }
ol li::before { content: counter(gift); grid-row: 1 / span 2; width: 24px; height: 24px; border-radius: 50%; background: #0d7c66; color: #fff; font-weight: 700; font-size: 10pt; display: flex; align-items: center; justify-content: center; font-family: 'Helvetica Neue', Helvetica, sans-serif; }
ol li strong { color: #1a2744; font-size: 11.6pt; font-weight: 600; }
ol.template li strong { font-weight: 500; background: #f7f8fc; border-radius: 6px; padding: 4px 9px; }
ol li span { color: #6b7280; font-size: 9.6pt; }
.copy-hint { color: #0d7c66; font-weight: 600; margin: 7px 0 0; }
h2 { font-size: 11.6pt; color: #1a2744; margin: 11px 0 3px; }
p { margin: 0 0 3px; }
.callout { background: rgba(200,146,42,0.08); border-inline-start: 3px solid #c8922a; border-radius: 6px; padding: 8px 12px; margin: 11px 0 0; }
.service { background: #f7f8fc; border-radius: 6px; padding: 8px 12px; margin-top: 10px; }
.service a { color: #0d7c66; font-weight: 600; text-decoration: none; }
.foot { position: fixed; bottom: 0; left: 0; right: 0; border-top: 1px solid #e2e8f0; padding-top: 6px; font-size: 7.8pt; color: #6b7280; line-height: 1.45; }
.foot .brands { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 4px; }
.foot strong { color: #1a2744; display: block; }
.foot a { color: #2c3547; text-decoration: none; }
.foot .who { color: #1a2744; }
.foot .url { color: #0d7c66; }
"""

def build_print(g, lang):
    t, gc = L[lang], g[lang]
    items = "".join(f"<li><strong>{h}</strong><span>{line}</span></li>" for h, line in gc["items"])
    sections = "".join(f"<h2>{h}</h2>" + "".join(f"<p>{p}</p>" for p in ps) for h, ps in gc["sections"])
    callout = "".join(f"<p>{p}</p>" for p in gc["callout"])
    s, label, link = gc["service"]
    brands = []
    for b in BRANDS:
        rows = [f'{b["site"]}', f'{t["email"]}: {b["email"]}']
        if b["wa_num"]:
            rows.append(f'{t["whatsapp"]}: <bdo dir="ltr">{b["wa_num"]}</bdo>')
        brands.append(f'<div><strong>{b["name"]}</strong>' + "<br>".join(rows) + "</div>")
    hint = f'<p class="copy-hint">{t["copy_hint"]}</p>' if g["kind"] == "template" else ""
    return f"""<!DOCTYPE html><html lang="{t['code']}" dir="{t['dir']}"><head><meta charset="UTF-8"><title>{esc(gc['title'])}</title>
<style>{PRINT_CSS}</style></head>
<body{' dir="rtl"' if t['dir'] == 'rtl' else ''} class="lang-{lang}">
<div class="top"><div><div class="name">{t['name']}</div><div class="title">{t['title']}</div></div><div class="tag">{t['tagline']}</div></div>
<div class="badge">{t['from_video'].format(n=g['video'])} &middot; {t['free_gift']}</div>
<h1>{gc['title']}</h1>
<p class="standfirst">{gc['standfirst']}</p>
<ol class="{g['kind']}">{items}</ol>{hint}
{sections}
<div class="callout">{callout}</div>
<p class="service">{s}<br><a href="{link}">{label}</a></p>
<div class="foot"><div class="brands">{''.join(brands)}</div>
<div class="who">{t['name']} &middot; {t['title']} &middot; {t['tagline']}</div>
<div class="url"><bdo dir="ltr">drqaria.njmcmedicsupp.com{gift_url(g, lang)}</bdo></div></div>
</body></html>"""

def build_pdfs():
    outdir = os.path.join(SITE, "gifts", "pdf")
    os.makedirs(outdir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="gifts-print-")
    try:
        for g in GIFTS:
            for lang in L:
                src = os.path.join(tmp, f"{g['pdf']}-{lang}.html")
                open(src, "w", encoding="utf-8").write(build_print(g, lang))
                dst = os.path.join(outdir, f"{g['pdf']}-{lang}.pdf")
                subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                                f"--print-to-pdf={dst}", "file://" + src],
                               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
                print("wrote", os.path.relpath(dst, ROOT), os.path.getsize(dst), "bytes")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for ch in "—–―":
        assert ch not in html, f"dash in {path}"
    open(path, "w", encoding="utf-8").write(html)
    print("wrote", os.path.relpath(path, ROOT))

def main():
    for lang in L:
        build_index(lang)
        for g in GIFTS:
            build_gift(g, lang)
    write(os.path.join(SITE, "assets", "gifts.css"), CSS)
    if "--no-pdf" not in sys.argv:
        build_pdfs()

if __name__ == "__main__":
    main()
