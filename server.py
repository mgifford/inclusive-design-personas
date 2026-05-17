#!/usr/bin/env python3
"""
Preview and static build tool for Inclusive Design Persona Cards.

- `python3 server.py` starts a local preview server.
- `python3 server.py --build --output dist` generates a static site for GitHub Pages.
"""

import argparse
import html
import json
import re
import shutil
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "cards.json"

with open(DATA_FILE, encoding="utf-8") as f:
    ALL_CARDS = json.load(f)

CATEGORY_ORDER = [
    "Auditory",
    "Cognitive",
    "Intersectional",
    "Mental Health",
    "Neurodiversity",
    "Physical",
    "Speech",
    "Visual",
]


def e(text):
    return html.escape(str(text) if text is not None else "")


def cat_id(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower())


def card_by_id(card_id):
    for card in ALL_CARDS:
        if card["id"] == card_id:
            return card
    return None


def related_cards(card):
    return [
        c
        for c in ALL_CARDS
        if c["category"] == card["category"] and c["id"] != card["id"]
    ]


def page_shell(
    title,
    description,
    body_html,
    *,
    css_href,
    header_html,
    footer_html=None,
    extra_scripts="",
):
    footer = (
        footer_html
        if footer_html is not None
        else """  <footer class=\"site-footer\" role=\"contentinfo\">
    <p>Inclusive Design Persona Cards &mdash; Helping teams build accessible, human-centered products.</p>
  </footer>"""
    )
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{e(title)}</title>
  <meta name=\"description\" content=\"{e(description)}\">
  <link rel=\"stylesheet\" href=\"{e(css_href)}\">
</head>
<body>
  <a class=\"skip-link\" href=\"#main-content\">Skip to main content</a>
  <header class=\"site-header\" role=\"banner\">
    <div class=\"header-inner\">{header_html}</div>
  </header>
  <main id=\"main-content\">
{body_html}
  </main>
{footer}
{extra_scripts}
</body>
</html>"""


def render_index(*, static=False):
    categories = {}
    for card in ALL_CARDS:
        categories.setdefault(card["category"], []).append(card)

    sections = []
    for cat_name in CATEGORY_ORDER:
        if cat_name not in categories:
            continue
        cid = cat_id(cat_name)

        cards_html = []
        for card in categories[cat_name]:
            card_href = f"cards/{card['id']}.html" if static else f"/card?id={card['id']}"
            cards_html.append(
                f"""
          <li>
            <article class="card-preview" aria-labelledby="card-title-{card['id']}">
              <header class="card-preview__header">
                <span class="card-preview__category" aria-label="Category: {e(cat_name)}">{e(cat_name)}</span>
                <h3 id="card-title-{card['id']}">{e(card['title'])}</h3>
                <p class="card-preview__name">{e(card['name'])}</p>
              </header>

              <div class="card-preview__body">
                <p class="card-preview__backstory">{e(card['backstory'])}</p>
              </div>

              <footer class="card-preview__footer">
                <a class="card-link" href="{e(card_href)}">
                  View {e(card['title'])} card
                  <span class="visually-hidden">for {e(card['name'])}</span>
                </a>
              </footer>
            </article>
          </li>"""
            )

        sections.append(
            f"""
    <section class="category-section" aria-labelledby="cat-{cid}">
      <h2 id="cat-{cid}">{e(cat_name)}</h2>
      <ul class="cards-grid" role="list">{''.join(cards_html)}
      </ul>
    </section>"""
        )

    body = (
        """    <section class="page-intro" aria-labelledby="intro-heading">
      <h2 id="intro-heading" class="visually-hidden">About These Cards</h2>
      <p>
        Great products are built for everyone&mdash;not just the majority. These persona cards represent
        real experiences of people with disabilities, chronic conditions, situational impairments, and
        cognitive differences. By designing with these personas in mind from the start, your team can
        uncover barriers early, build empathy across disciplines, and ship products that work for the
        full spectrum of human diversity. Use them in design critiques, sprint planning, accessibility
        audits, and AI development to keep diverse users at the center of every decision.
      </p>
    </section>"""
        + "".join(sections)
    )

    header_html = (
        '<h1>Inclusive Design Persona Cards</h1>'
        '<p class="tagline">40 personas. Every kind of user. Better products for everyone.</p>'
    )

    return page_shell(
        "Inclusive Design Persona Cards",
        "A collection of 40 inclusive design persona cards representing diverse users.",
        body,
        css_href="css/style.css" if static else "/css/style.css",
        header_html=header_html,
    )


def render_card(card_id, *, static=False):
    card = card_by_id(card_id)
    if card is None:
        return None

    rel = related_cards(card)
    cid = cat_id(card["category"])
    techs = card["assistiveTechnologies"]

    if static:
        home_href = "../index.html"
        category_href = f"../index.html#cat-{cid}"
        related_href = lambda rid: f"{rid}.html"
        css_href = "../css/style.css"
    else:
        home_href = "/"
        category_href = f"/#cat-{cid}"
        related_href = lambda rid: f"/card?id={rid}"
        css_href = "/css/style.css"

    tech_items = "".join(f"<li>{e(t.strip())}</li>" for t in techs)

    related_section = ""
    if rel:
        links = "".join(
            f'<li><a href="{e(related_href(r["id"]))}">{e(r["title"])}'
            f'<span class="visually-hidden"> &mdash; {e(r["name"])}'
            f"</span></a></li>"
            for r in rel
        )
        related_section = f"""
      <section class="card-section related-cards-section" aria-labelledby="related-heading">
        <h3 id="related-heading">Related {e(card['category'])} Cards</h3>
        <ul class="related-cards-list" role="list">{links}</ul>
      </section>"""

    print_related = ""
    if rel:
        print_related = (
            '<div class="print-related"><strong>Related:</strong> '
            + e(", ".join(r["title"] for r in rel))
            + "</div>"
        )

    clinical = ""
    if card.get("clinicalExamples"):
        clinical = f"""
      <section class="card-section" aria-labelledby="section-clinical">
        <h3 id="section-clinical">Clinical Examples</h3>
        <p class="clinical-examples">{e(card['clinicalExamples'])}</p>
      </section>"""

    ai_section = ""
    if card.get("aiPromptUrl"):
        prompt_block = ""
        if card.get("aiPrompt"):
            prompt_block = f"""
      <div class="ai-prompt-wrapper">
        <div class="ai-prompt-toolbar">
          <span class="ai-prompt-label">Prompt</span>
          <button class="copy-prompt-btn" type="button" onclick="copyPrompt(this)" aria-label="Copy AI prompt text to clipboard">
            <svg aria-hidden="true" focusable="false" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            Copy prompt
          </button>
        </div>
        <pre class="ai-prompt-code"><code>{e(card['aiPrompt'])}</code></pre>
      </div>"""

        ai_section = f"""
    <aside class="ai-prompt-section no-print" aria-labelledby="ai-prompt-heading">
      <h3 id="ai-prompt-heading">AI Development Prompt</h3>
      <p>Incorporate {e(card['title'])} into your AI development with this prompt.</p>{prompt_block}
      <a class="ai-prompt-link"
         href="{e(card['aiPromptUrl'])}"
         target="_blank"
         rel="noopener noreferrer"
         aria-label="Open AI prompt for {e(card['title'])} (opens in new tab)">
        Use the {e(card['title'])} AI Prompt ↗
      </a>
    </aside>"""

    print_ai = ""
    if card.get("aiPromptUrl"):
        print_ai = f"""
          <h3>AI Development Prompt</h3>
          <p>Incorporate {e(card['title'])} into your AI development with this prompt:</p>
          <p class="print-ai-url">{e(card['aiPromptUrl'])}</p>"""

    print_tech_items = "\n".join(f"              <li>{e(t.strip())}</li>" for t in techs)

    body = f"""
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <ol>
        <li><a href="{e(home_href)}">All Cards</a></li>
        <li><a href="{e(category_href)}">{e(card['category'])}</a></li>
        <li><span aria-current="page">{e(card['title'])}</span></li>
      </ol>
    </nav>

    <button class="print-btn no-print" onclick="window.print()" type="button">
      <svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="6 9 6 2 18 2 18 9"></polyline>
        <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
        <rect x="6" y="14" width="12" height="8"></rect>
      </svg>
      Print this card
    </button>

    <article class="card-detail no-print" aria-labelledby="card-heading">
      <header class="card-detail__header">
        <span class="card-detail__category">{e(card['category'])}</span>
        <h2 id="card-heading">{e(card['title'])}</h2>
        <p class="card-detail__persona-name">Persona: {e(card['name'])}</p>
        <p class="card-detail__backstory">{e(card['backstory'])}</p>
      </header>

      <section class="card-section" aria-labelledby="section-condition">
        <h3 id="section-condition">About This Condition</h3>
        <p>{e(card['conditionDescription'])}</p>
      </section>

      <section class="card-section" aria-labelledby="section-challenges">
        <h3 id="section-challenges">Digital Challenges</h3>
        <p>{e(card['digitalChallenges'])}</p>
      </section>

      <section class="card-section" aria-labelledby="section-assistive">
        <h3 id="section-assistive">Assistive Technologies</h3>
        <ul class="assistive-tech-list">{tech_items}</ul>
      </section>

      <section class="card-section" aria-labelledby="section-design">
        <h3 id="section-design">Design Considerations</h3>
        <p>{e(card['designConsiderations'])}</p>
      </section>
{clinical}
{related_section}
    </article>
{ai_section}

    <div class="print-only" role="presentation">
      <div class="print-card-wrapper">
        <div class="print-card-front">
          <span class="print-category">{e(card['category'])}</span>
          <h1>{e(card['title'])}</h1>
          <p class="print-name">{e(card['name'])}</p>
          <p class="print-backstory">{e(card['backstory'])}</p>
          <p class="print-condition">{e(card['conditionDescription'])}</p>
          {print_related}
        </div>
        <div class="print-card-back">
          <h3>Digital Challenges</h3>
          <p>{e(card['digitalChallenges'])}</p>
          <h3>Assistive Technologies</h3>
          <ul>
{print_tech_items}
          </ul>
          <h3>Design Considerations</h3>
          <p>{e(card['designConsiderations'])}</p>
{print_ai}
        </div>
      </div>
      <p class="print-fold-guide">✂ Fold right panel behind left panel to create a double-sided card</p>
    </div>
"""

    footer_html = f"""  <footer class="site-footer no-print" role="contentinfo">
    <p>
      <a href="{e(home_href)}">← Back to all persona cards</a>
      &nbsp;&mdash;&nbsp;
      Inclusive Design Persona Cards
    </p>
  </footer>"""

    copy_script = """  <script>
  function copyPrompt(btn) {
    var code = btn.closest('.ai-prompt-wrapper').querySelector('code');
    var original = btn.innerHTML;
    navigator.clipboard.writeText(code.textContent).then(function () {
      btn.textContent = 'Copied!';
      btn.setAttribute('aria-label', 'Copied to clipboard');
      setTimeout(function () {
        btn.innerHTML = original;
        btn.setAttribute('aria-label', 'Copy AI prompt text to clipboard');
      }, 2000);
    }, function () {
      btn.textContent = 'Copy failed';
      setTimeout(function () { btn.innerHTML = original; }, 2000);
    });
  }
  </script>"""

    return page_shell(
        f"{card['title']} — Inclusive Design Persona Cards",
        f"Inclusive design persona card for {card['title']} ({card['category']}). Learn about digital challenges, assistive technologies, and design considerations.",
        body,
        css_href=css_href,
        header_html=f'<h1><a href="{e(home_href)}">Inclusive Design Persona Cards</a></h1>',
        footer_html=footer_html,
        extra_scripts=copy_script,
    )


def render_404(*, static=False):
    home_href = "index.html" if static else "/"
    css_href = "css/style.css" if static else "/css/style.css"

    body = f"""    <h1>Card Not Found</h1>
    <p>The persona card you requested does not exist.</p>
    <p><a href="{e(home_href)}">Return to all persona cards</a></p>"""

    return page_shell(
        "Card Not Found — Inclusive Design Persona Cards",
        "The persona card you requested does not exist.",
        body,
        css_href=css_href,
        header_html=f'<p><a href="{e(home_href)}">Inclusive Design Persona Cards</a></p>',
    )


def build_static(output_dir):
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    (out / "cards").mkdir(parents=True, exist_ok=True)

    shutil.copytree(BASE_DIR / "css", out / "css")
    shutil.copytree(BASE_DIR / "data", out / "data")

    prompts = BASE_DIR / "prompts.html"
    if prompts.exists():
        shutil.copy2(prompts, out / "prompts.html")

    (out / "index.html").write_text(render_index(static=True), encoding="utf-8")
    (out / "404.html").write_text(render_404(static=True), encoding="utf-8")

    for card in ALL_CARDS:
        page = render_card(card["id"], static=True)
        (out / "cards" / f"{card['id']}.html").write_text(page, encoding="utf-8")


class Handler(BaseHTTPRequestHandler):
    def send_html(self, content, status=200):
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_file(self, path, content_type):
        try:
            with open(path, "rb") as f:
                data = f.read()
        except FileNotFoundError:
            self.send_html(render_404(static=False), 404)
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)

        if path in ("/", "/index.php", "/index.html"):
            self.send_html(render_index(static=False))
            return

        if path in ("/card", "/card.php"):
            try:
                card_id = int(qs.get("id", [0])[0])
            except ValueError:
                card_id = 0
            page = render_card(card_id, static=False)
            if page is None:
                self.send_html(render_404(static=False), 404)
            else:
                self.send_html(page)
            return

        if path in ("/404", "/404.php", "/404.html"):
            self.send_html(render_404(static=False), 404)
            return

        if path.startswith("/css/"):
            self.send_file(BASE_DIR / path.lstrip("/"), "text/css; charset=utf-8")
            return

        if path.startswith("/data/"):
            self.send_file(BASE_DIR / path.lstrip("/"), "application/json; charset=utf-8")
            return

        if path == "/prompts.html":
            self.send_file(BASE_DIR / "prompts.html", "text/html; charset=utf-8")
            return

        self.send_html(render_404(static=False), 404)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="Generate static site files")
    parser.add_argument("--output", default="dist", help="Output directory for static build")
    parser.add_argument("--port", type=int, default=8765, help="Preview server port")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.build:
        build_static(args.output)
        print(f"Static site generated in {Path(args.output).resolve()}")
        return

    server = HTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Preview server running at http://127.0.0.1:{args.port}/")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
