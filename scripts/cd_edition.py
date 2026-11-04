#!/usr/bin/env python3
"""The Collecting Daily edition of a built report.

    python3 cd_edition.py --compare "<PF.html>" "<PF.pdf>" "<CD.pdf>" "<working.md>"

Every report goes out twice: "PF — <Title>.pdf" in the Paul Fraser Collectibles
design and "CD — <Title>.pdf" for Collecting Daily.
They are one document. The CD edition changes the banners, the colours, the
contact box and, where the report talks about Paul Fraser Collectibles, the
words: in a Collecting Daily document "we" is Collecting Daily, so PFC is "our
sister company" and its stock and services are described in the third person.
build.py makes it from the same HTML after the gates pass. The writer writes
every one of those words: this script only puts them in place.

Every sheet keeps its content area to the millimetre. Page 1's PF header and
title band stay in the page, invisible, holding their exact height, and the CD
banner and title band sit over the top of them; the running header is swapped
inside the PF band, which is the same 20mm. So every block lands on the same
page in both editions, by construction, and compare() proves it afterwards by
reading both PDFs page by page: same page count, and the same text on every
page once each edition's own header is taken off and the CD wording and contact
changes are applied to the PF text.

THE CD WORDING FILE
-------------------
The wording changes for one report live beside its working markdown, as
"<working file>.cd.md", in pairs, both lines the writer's own words:

    PF: 9. A selection from our stock
    CD: 9. A selection from Paul Fraser Collectibles, our sister company

Each PF text must appear exactly once in the built report, written in the
markdown dialect of dmd.py (**bold**, *italic*, a plain £). Every other line is
a note. The contact box needs no entry: it always becomes Collecting Daily's.
wording_problems() fails any section about PFC or its stock that still says
we, our or us as PFC, or never calls it our sister company.

The banner artwork is traced from the vector file the client supplied
("Collecting Daily Styling.pdf"): assets/cd-banner.svg is Header-02 for page 1,
assets/cd-roundel.svg is the CD roundel for the running header (Header-01, drawn
at the PF running header's 20mm rather than its own 27mm, so no page loses room).
"""
import base64, html as htmllib, pathlib, re, subprocess, sys, unicodedata

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"
PF_PREFIX, CD_PREFIX = "PF — ", "CD — "

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from dmd import inline

# The contact box in the CD edition (client, 7 October 2026).
CD_PHONE, CD_SITE, CD_EMAIL = "+44 (0) 1534 639998", "collectingdaily.com", "hello@collectingdaily.com"
PF_SITE, PF_EMAIL = "paulfrasercollectibles.com", "info@paulfrasercollectibles.com"

# PFC colour -> Collecting Daily colour. The first three CD values are measured
# from the client's styling file; the last two have no CD counterpart there and
# are tints of its charcoal and its pale grey.
SWAP = {
    "#323748": "#414042",   # navy: banners, heat box, table heads, chart bars, accent text
    "#f7f4e2": "#dfe2df",   # cream: title band, sidebar, pull-outs, chart ground
    "#fffdf5": "#eff1e8",   # the star-key box
    "#fbfaf4": "#f7f8f4",   # alternate table rows
    "#5d6274": "#6d6c6e",   # mid slate: second tier of a diagram, unlit stars
}
# Teal is the PFC accent. On charcoal the CD file makes it white (the stars);
# as the fill of a shape on a light ground (a short chart bar, a diagram tier)
# white would vanish, so there it is a mid grey.
TEAL, TEAL_ON_DARK, TEAL_FILL = "#8fd1d5", "#ffffff", "#a7a6a8"
PFC_ONLY = [TEAL] + list(SWAP)

# Page 1, in points, measured from the styling file: banner 0-75.586, title band
# to 179.676. Baselines 117.84 (title, Medium 24pt), 137.42 (focus, Medium 14pt),
# 165.04 (date, Bold 12pt), at x 29.97. With line-height 1, Helvetica Neue's
# baseline sits 0.8695em below the top of its box.
CSS = """
  /* ===== Collecting Daily edition (scripts/cd_edition.py) ===== */
  .cd-ghost{visibility:hidden;}
  .band.cd-ghost{margin-top:-179.676pt;}
  .cdtop{flex:0 0 auto;}
  .cdtop .cdbanner{display:block;width:210mm;height:75.586pt;}
  .cdtitle{background:#dfe2df;min-height:104.09pt;padding:21.38pt 10.57mm 0;color:#231f20;}
  .cdtitle h1{margin:0;font-size:24pt;font-weight:500;line-height:1;letter-spacing:0;text-transform:none;}
  .cdtitle .cdfocus{margin-top:4.28pt;font-size:14pt;font-weight:500;line-height:1;}
  .cdtitle .cddate{margin-top:15.37pt;font-size:12pt;font-weight:700;line-height:1;}
  .side{border-top-color:#dfe2df;}
  .band.cd{justify-content:flex-start;padding:0 0 0 9.65mm;}
  .band.compact.cd img{height:11.39mm;width:11.39mm;}
  .band.cd .cdrun{margin-left:4.43mm;color:#ffffff;white-space:nowrap;}
  .band.cd .cdrun .t{font-size:13.45pt;font-weight:500;line-height:1;}
  .band.cd .cdrun .f{font-size:8.97pt;font-weight:500;line-height:1;margin-top:2.29pt;}
  body.tight .band.compact.cd img{height:8mm;width:8mm;}
  body.tight .band.cd .cdrun .t{font-size:9.5pt;}
  body.tight .band.cd .cdrun .f{font-size:6.3pt;margin-top:1.6pt;}
"""

SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "of", "on", "or", "the", "to", "vs", "&"}


def svg_uri(name):
    return "data:image/svg+xml;base64," + base64.b64encode((ASSETS / name).read_bytes()).decode()


def title_case(s):
    words = s.split(" ")
    out = []
    for i, w in enumerate(words):
        if i and w.lower() in SMALL:
            out.append(w.lower())
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)


def strip_tags(s):
    return htmllib.unescape(re.sub(r"<[^>]+>", "", s))


def meta(text):
    """Title, date and focus as page 1's PF title band gives them."""
    i = text.find('<div class="titleband">')
    block = text[i:text.find('<div class="content">', i)] if i >= 0 else ""
    m = re.search(r"<h1>(.*?)</h1>", block, re.S)
    if not m:
        sys.exit("cd_edition: no PF title band (<div class=\"titleband\"><h1>...) on page 1")
    h1 = strip_tags(m.group(1)).strip()
    d = re.search(r"<b[^>]*>DATE</b>(.*?)</div>", block, re.S)
    f = re.search(r"<b[^>]*>FOCUS</b>(.*?)</div>", block, re.S)     # the focus line is optional
    if not d:
        sys.exit("cd_edition: the PF title band has no DATE line")
    title = title_case(h1)
    if not re.search(r"market (report|update)$", title, re.I):
        title += " Market Report"
    return {"h1": h1, "date": strip_tags(d.group(1)).strip(),
            "focus": strip_tags(f.group(1)).strip() if f else "", "title": title}


def set_title(text, title):
    t = "<title>%s</title>" % htmllib.escape(title)
    if re.search(r"<title>.*?</title>", text, re.S):
        return re.sub(r"<title>.*?</title>", lambda _: t, text, count=1, flags=re.S)
    return text.replace("<head>", "<head>\n" + t, 1)


def recolour(text):
    head, sep, body = text.partition("</style>")
    if not sep:
        sys.exit("cd_edition: no <style> block")
    for a, b in SWAP.items():
        head = re.sub(re.escape(a), b, head, flags=re.I)
        body = re.sub(re.escape(a), b, body, flags=re.I)
    head = re.sub(re.escape(TEAL), TEAL_ON_DARK, head, flags=re.I)

    def tag(m):
        t = m.group(0)
        if TEAL not in t.lower():
            return t
        if m.group(1).lower() in ("text", "tspan"):
            return re.sub(re.escape(TEAL), TEAL_ON_DARK, t, flags=re.I)
        t = re.sub(r"(?<![-\w])color:\s*" + re.escape(TEAL), "color:" + TEAL_ON_DARK, t, flags=re.I)
        return re.sub(re.escape(TEAL), TEAL_FILL, t, flags=re.I)

    body = re.sub(r"<([A-Za-z][\w:-]*)\b[^>]*>", tag, body)
    return head + sep + body


def wording_path(md):
    md = pathlib.Path(md)
    return md.with_name(md.stem + ".cd.md")


def load_wording(path):
    """[(pf, cd), ...] from a CD wording file, or [] if there is none."""
    path = pathlib.Path(path)
    if not path.exists():
        return []
    pairs, pf = [], None
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("PF:"):
            if pf:
                sys.exit(f"{path.name} line {pf[0]}: PF: with no CD: line after it")
            pf = (n, line[3:].strip())
        elif line.startswith("CD:"):
            if not pf:
                sys.exit(f"{path.name} line {n}: CD: with no PF: line before it")
            pairs.append((pf[1], line[3:].strip()))
            pf = None
    if pf:
        sys.exit(f"{path.name} line {pf[0]}: PF: with no CD: line after it")
    return pairs


def swap_contact(text):
    """PFC's contact details in the contact box become Collecting Daily's. No box, no change."""
    n = text.count('<div class="contactbox"')
    if n == 0:
        return text
    if n != 1:
        sys.exit("cd_edition: expected one contact box, found %d" % n)
    i = text.index('<div class="contactbox"')
    j = text.find(PF_EMAIL, i)
    if j < 0 or j - i > 1000:
        sys.exit("cd_edition: the contact box has no " + PF_EMAIL)
    j += len(PF_EMAIL)
    box = text[i:j].replace(PF_EMAIL, CD_EMAIL)
    box, n1 = re.subn(r"(?<![@/\w.])" + re.escape(PF_SITE) + r"(?![/\w])", CD_SITE, box)
    box, n2 = re.subn(r"\+44 ?\(0\) ?1534 ?639998", CD_PHONE, box)
    if n1 != 1 or n2 != 1:
        sys.exit("cd_edition: the contact box is not phone, website, email as expected")
    return text[:i] + box + text[j:]


FIRST_PERSON = re.compile(r"\b(?:[Ww]e(?:'ve|'re|'ll|'d)?|[Oo]urs?|us)\b")


def wording_problems(cd_text):
    """Sections about PFC or its stock that still speak as PFC in the CD edition.

    A section counts when its heading names Paul Fraser Collectibles or stock.
    It must call PFC our sister company somewhere, and once "our sister
    company" is set aside, no we, our or us may be left in it: in a Collecting
    Daily document they would make PFC's stock and history ours.
    """
    body = cd_text.split("</style>", 1)[1]
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = re.sub(r'<div class="disc">.*?</div>', "", body, flags=re.S)
    problems = []
    for part in re.split(r"(?=<h2[\s>])", body):
        h = re.match(r"<h2[^>]*>(.*?)</h2>", part, re.S)
        if not h:
            continue
        head = strip_tags(h.group(1)).strip()
        if not re.search(r"\bstock\b|Paul Fraser Collectibles", head, re.I):
            continue
        # The rule: name the company in full, and say it is our sister company.
        if "Paul Fraser Collectibles" not in head or "sister company" not in head:
            problems.append(f'"{head}": a heading about PFC or its stock must read '
                            f'"... Paul Fraser Collectibles, our sister company"')
        txt = re.sub(r"\s+", " ", strip_tags(part))
        if "sister company" not in txt:
            problems.append(f'"{head}": never calls Paul Fraser Collectibles our sister company')
        rest = re.sub(r"[Oo]ur sister company", "", txt)
        for w in FIRST_PERSON.finditer(rest):
            a, b = max(0, w.start() - 40), w.end() + 40
            problems.append(f'"{head}": still speaks as PFC: ...{rest[a:b].strip()}...')
    # Every "sister company" must sit in a sentence that also names the company
    # in full: a bare "our sister company" leaves the reader guessing which one.
    flat = re.sub(r"\s+", " ", strip_tags(body))
    for m in re.finditer(r"sister company", flat):
        a = flat.rfind(". ", 0, m.start())
        b = flat.find(". ", m.end())
        sentence = flat[(a + 1 if a >= 0 else 0):(b if b >= 0 else len(flat))]
        if "Paul Fraser Collectibles" not in sentence:
            problems.append('bare "sister company" with no full name: ...'
                            + flat[max(0, m.start() - 60):m.end() + 20].strip() + '...')
    return problems


def make(text, stem, wording=()):
    """The CD edition of a built PF report, as HTML."""
    m = meta(text)
    e = lambda s: htmllib.escape(s, quote=False)
    start = text.index("</style>")
    for pf, cd in wording:
        a, b = inline(pf), inline(cd)
        n = text.count(a, start)
        if n != 1:
            sys.exit(f"cd_edition: CD wording: {pf!r} is in the report {n} times; it must be there once")
        text = text[:start] + text[start:].replace(a, b, 1)
    text = swap_contact(text)
    text = set_title(text, CD_PREFIX + stem)
    text = recolour(text)

    # page 1: the PF band and title band stay, invisible, so the content area
    # starts exactly where it does in PF; the CD banner and title band go first.
    top = ('<div class="cdtop">\n'
           '    <img class="cdbanner" src="%s" alt="Collecting Daily">\n'
           '    <div class="cdtitle">\n'
           '      <h1>%s</h1>\n%s'
           '      <div class="cddate">%s</div>\n'
           '    </div>\n'
           '  </div>\n'
           '  <header class="band cd-ghost"></header>') % (
               svg_uri("cd-banner.svg"), e(m["title"]),
               '      <div class="cdfocus">%s</div>\n' % e(m["focus"]) if m["focus"] else '', e(m["date"]))
    text, n = re.subn(r'<header class="band"[^>]*>.*?</header>', lambda _: top, text, count=1, flags=re.S)
    if n != 1:
        sys.exit("cd_edition: no page-1 header (<header class=\"band\">)")
    text = text.replace('<div class="titleband">', '<div class="titleband cd-ghost">', 1)

    run = ('<header class="band compact cd">\n'
           '    <img src="%s" alt="Collecting Daily">\n'
           '    <div class="cdrun"><div class="t">%s</div><div class="f">%s</div></div>\n'
           '  </header>') % (svg_uri("cd-roundel.svg"), e(m["title"]), e(m["focus"]))
    text = re.sub(r'<header class="band compact"[^>]*>.*?</header>', lambda _: run, text, flags=re.S)

    text = text.replace("</style>", CSS + "</style>", 1)

    left = [c for c in PFC_ONLY if c in text.lower()]
    if left:
        sys.exit("cd_edition: PFC colours left in the CD edition: " + ", ".join(left))
    if "Paul Fraser Collectibles" in "".join(re.findall(r"<header.*?</header>", text, re.S)):
        sys.exit("cd_edition: a PFC header survived in the CD edition")
    return text


# ---------------------------------------------------------------- comparison

def squash(s):
    return "".join(unicodedata.normalize("NFKC", s).split())


def pages(pdf):
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    n = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    return [subprocess.run(["pdftotext", "-raw", "-f", str(i), "-l", str(i), str(pdf), "-"],
                           capture_output=True, text=True, check=True).stdout
            for i in range(1, n + 1)]


def compare(text, pf_pdf, cd_pdf, wording=()):
    """Problems found comparing the two editions, or [] if they match.

    `text` is the PF HTML the two PDFs were made from. Each page's text is read
    in content-stream order; the header is first on every page, so each
    edition's own header is taken off the front. The CD wording and contact
    changes are then applied to the PF text, and the rest must be identical.
    """
    plain = lambda s: squash(strip_tags(inline(s)))
    swaps = [(plain(a), plain(b)) for a, b in wording]
    if '<div class="contactbox"' in text:
        swaps.append((squash(PF_SITE + PF_EMAIL), squash(CD_SITE + CD_EMAIL)))
    seen = {s: 0 for s, _ in swaps}
    m = meta(text)
    tags = [strip_tags(t) for t in re.findall(r'<div class="tag">(.*?)</div>', text, re.S)]
    pf, cd = pages(pf_pdf), pages(cd_pdf)
    problems = []
    if len(pf) != len(cd):
        return ["page count: PF %d, CD %d" % (len(pf), len(cd))]
    if len(tags) != len(pf):
        return ["the HTML has %d PF headers and the PDF %d pages" % (len(tags), len(pf))]
    for i, (a, b) in enumerate(zip(pf, cd)):
        if i == 0:
            hp = tags[0] + m["h1"].upper() + "DATE" + m["date"] + ("FOCUS" + m["focus"] if m["focus"] else "")
            hc = m["title"] + m["focus"] + m["date"]
        else:
            hp = tags[i]
            hc = m["title"] + m["focus"]
        hp, hc, a, b = squash(hp), squash(hc), squash(a), squash(b)
        if not a.startswith(hp):
            problems.append("page %d: PF text does not open with its header %r: %r" % (i + 1, hp, a[:len(hp) + 20]))
            continue
        if not b.startswith(hc):
            problems.append("page %d: CD text does not open with its header %r: %r" % (i + 1, hc, b[:len(hc) + 20]))
            continue
        a, b = a[len(hp):], b[len(hc):]
        for s, c in swaps:
            seen[s] += a.count(s)
            a = a.replace(s, c)
        if a != b:
            k = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
            problems.append("page %d differs at character %d: PF ...%s... CD ...%s..."
                            % (i + 1, k, a[max(0, k - 30):k + 30], b[max(0, k - 30):k + 30]))
    for s, n in seen.items():
        if n != 1:
            problems.append("a CD change applies to text found %d times in the PF PDF, not once: %s" % (n, s[:60]))
    return problems


def main():
    args = sys.argv[1:]
    if args[:1] != ["--compare"] or len(args) != 5:
        sys.exit(__doc__.split("\n\n")[1])
    text = pathlib.Path(args[1]).read_text(encoding="utf-8")
    problems = compare(text, args[2], args[3], load_wording(wording_path(args[4])))
    for p in problems:
        print("  FAIL  " + p)
    print("editions match" if not problems else "%d problem(s)" % len(problems))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
