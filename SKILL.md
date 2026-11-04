---
name: market-report-layout
description: "Lay out a market report that a person has written, with the images and captions they chose, as two finished A4 PDFs and HTML pages: the Paul Fraser Collectibles edition and the Collecting Daily edition. Takes the draft as .docx (Word, LibreOffice, Google Docs) or .md (Obsidian), .odt or .txt. Conversion only: it never writes, edits, corrects or source-checks the text, and every word of the Collecting Daily wording comes from the writer. Use when someone hands over a finished market report draft to be turned into the PF and CD PDFs."
---

# Market report layout: the writer's draft in, two designed PDFs out

A person researches the market, writes the report, finds the images and writes their captions. This skill turns that draft into the finished documents, twice from one build: `PF — <Title>.pdf` in the Paul Fraser Collectibles design and `CD — <Title>.pdf` for Collecting Daily, each with a self-contained HTML page.

## What this skill does not do

Only the writer writes. Hold to it exactly:

- **Never write.** No new sentence, heading, caption, summary, section or "about us". A pull quote or a key figure may only repeat the writer's words exactly. If a section is empty in the draft, it is empty in the PDF.
- **Never edit.** Not a word, not a figure, not a spelling, not a comma. The text goes out as the writer wrote it, typos included.
- **Never check sources.** No fetching, no verification. The figures are the writer's and are typeset as given.
- **Never fill a gap.** A placeholder like `TEXT TO GO HERE` stays in and is reported. A missing image is reported, not found elsewhere.
- **Never word the Collecting Daily edition.** Where the report speaks as Paul Fraser Collectibles ("our stock", "we have sold"), the Collecting Daily edition needs other words. The build lists those passages; the writer gives the new wording, and you copy it in word for word (step 8).

`scripts/textcheck.py` enforces the first two mechanically: the build compares every word and figure in the finished HTML against the writer's original file, in order, and proves every pull quote and key figure word for word against it; it **refuses to write a PDF if anything differs**. `scripts/cd_edition.py` then proves the Collecting Daily PDF has the same text on every page as the PF one, apart from the headers, the contact box and the writer's own CD wording.

What you may do is layout, and only layout: decide which lines are headings, where each image sits, which passages become cards, panels or boxes, which of the writer's sentences to repeat as pull quotes, which of their figures go in the sidebar, where a page must break, and the frontmatter below.

If you notice something that would embarrass in print (a placeholder, text pointing at an image nobody supplied, a figure in the text that disagrees with the same figure in a caption), **do not fix it.** List it in the handover, quoting both sides, and let the writer decide.

## How the writer hands over the draft

- **Word or LibreOffice:** the `.docx` or `.odt` file. **Google Docs:** File → Download → Microsoft Word (.docx). **Obsidian:** the `.md` file and its images. Plain `.txt` works too. Never a PDF or a Pages file: ask for `.docx`.
- **Images** go inside the document where they belong, or beside it in the same folder. **The line directly under an image is its caption**, the writer's own words, credit included ("Image: Heritage Auctions"). An image with no line under it has no caption.
- `template/Market report template.docx` is a starting point with the report's eleven sections as headings. Writers may use it or not: their own headings and order are kept.
- The writer drags the file into the chat or names the folder it is in.

## The layout

The PFC report layout and the Collecting Daily reskin, carried in full inside this skill so it depends on nothing else:

| Path | What it is |
| --- | --- |
| `assets/report.css` | The PFC report stylesheet. Do not edit it to change one document. |
| `assets/typesetter.css` | Exact block measurement, supplied images of any shape, split paragraphs and tables, links, footnotes. Loaded after `report.css`. |
| `assets/pfc-logo-navy.png` | The PFC logo lockup on navy. |
| `assets/cd-banner.svg`, `assets/cd-roundel.svg` | Collecting Daily's page-1 banner and the roundel for its running header. |

PF edition: navy header band with the logo and a tag on every page (full height on page 1, compact after), the cream title band on page 1 with the title and `DATE` (and `FOCUS` when the draft gives one), single-column body, navy table headers, the cream pull-out band, the disclaimer centred at the foot of the last page. CD edition: the same pages, block for block, with Collecting Daily's banner, charcoal and light grey in place of navy and cream, and Collecting Daily's contact box (+44 (0) 1534 639998, collectingdaily.com, hello@collectingdaily.com).

## The scripts

| Script | What it does |
| --- | --- |
| `scripts/ingest.py` | Sets a job up. Copies the draft **untouched** into `WORKINGS/<slug>/source/` (the text check compares against this copy, so it is never edited), copies the images into `WORKINGS/<slug>/images/` as `01-…`, `02-…`, then writes the working markdown with the title lifted into the frontmatter. Reads `.docx`, `.odt`, `.md` and `.txt` directly, keeping headings, lists, bold, italics, links, tables, footnotes and embedded images. Older formats (`.doc .rtf .html`) go through LibreOffice if it is installed, or macOS `textutil`. It refuses Pages and PDF files. `--replace` re-runs it after the draft has changed, keeping the previous version. |
| `scripts/odt.py` | The LibreOffice reader, plus a separate plain-text reader the text check uses, so the check never trusts the conversion it is checking. |
| `scripts/system.py` | Everything that differs between macOS and Windows: where Chrome, Edge and LibreOffice live, file addresses, UTF-8 output. |
| `scripts/build.py` | Turns the working markdown into the deliverables. Measures every block in headless Chrome, flows them into A4 sheets, verifies the real sheets, runs the gates, prints the PF PDF, makes and prints the CD edition, compares the two, renders page previews. |
| `scripts/cd_edition.py` | The Collecting Daily edition of the built PF HTML, and the page-by-page comparison of the two PDFs. |
| `scripts/dmd.py` | The markdown dialect. Its docstring is the reference. |
| `scripts/textcheck.py` | The gate that proves the words are the writer's. Runs inside the build; can be run alone. |

## Mac and Windows

The same folder runs on both. It needs **Python 3** (standard library only) and a **Chromium browser**: Google Chrome, or Microsoft Edge, which every Windows PC has.

- **Run the scripts with the Python this machine has:** `python3` on macOS, `python` on Windows, with the skill folder given as `${CLAUDE_SKILL_DIR}`. If Python is missing on Windows, say so in one line and point to the **Python Install Manager** in the Microsoft Store; do not install anything without asking.
- **Optional helpers, used when present:** `pdftoppm`, `pdftotext` and `pdfinfo` (poppler) render the previews from the PDFs and compare the two editions page by page; without them the previews are Chrome screenshots, there are none for the CD edition, and the editions are not compared, which the handover must say. On macOS, `sips` converts HEIC, TIFF and BMP images and scales anything over 2400px, and `textutil` reads older document formats.
- **Fonts:** the stylesheet asks for Helvetica Neue, then Arial. Windows has no Helvetica Neue, so a PDF made there is set in Arial. The pages are measured on the machine that builds them, so the layout adjusts.

## Where the files go

```
<root>/                                  the folder the draft is in; --root=<dir> overrides it
    <Title>.md                           working file: the writer's text, plus layout
    <Title>.cd.md                        the writer's Collecting Daily wording, PF:/CD: pairs (step 8)
    PDFs/PF — <Title>.pdf                deliverable, Paul Fraser Collectibles
    PDFs/CD — <Title>.pdf                deliverable, Collecting Daily
    HTML/PF — <Title>.html               deliverable, fully self-contained
    HTML/CD — <Title>.html               deliverable, fully self-contained
    WORKINGS/<slug>/
        source/<the writer's file>       the original, untouched
        images/                          the images, numbered in the order given
        previews/pf-NN.png, cd-NN.png    every page of both editions, for the visual review
```

## Steps

1. **Get the inputs onto disk.** The draft is the one `.docx`, `.odt` or `.md` file in the folder (ask which, in one line, if there are several); images inside it come with it, and every PNG, JPG, GIF, WebP or SVG beside it is an image to place. List back what you found. If the draft arrived pasted into the chat instead, save it verbatim to a `.md` or `.txt` file first; that file becomes the source the text check trusts, and pasted text carries no images, so ask for them. If a file or folder cannot be read, **stop and say so in one line**, with what to click or where to move the file.

2. **Read the whole draft before anything else**, and look at every image. Know what each image shows, which paragraph it belongs to and which line under it is its caption.

3. **Ingest.**

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/ingest.py" "<draft>" "<image 1>" "<image 2>" ...
   ```

   It takes the first line as the title when it looks like one. When the first line is a label rather than the title ("Market update:" above "Music memorabilia"), pass `--title="Music memorabilia"` exactly as the writer wrote it. After the draft has changed, run it again with `--replace`: the previous working file, source copy and images move to `WORKINGS/<slug>/previous/<date time>/`, and nothing is deleted.

4. **Set the frontmatter** in the working file:

   | Field | Rule |
   | --- | --- |
   | `Title` | From the draft, exactly as the writer wrote it. |
   | `Tag` | The label in the header band. Default `MARKET REPORT`. If the draft opens with its own label ("Market update:"), use that and delete the line from the body: the text check recognises a label moved into the header. |
   | `Date` | Defaults to today. Use the writer's date if the draft states one. |
   | `Focus` | Only if the draft carries a focus or subtitle line. Move it here and delete it from the body. Otherwise leave it empty: never compose one. |
   | `Contact box` | `true` puts the contact box after the last text (PFC's in the PF edition, Collecting Daily's in the CD edition). Set `false` when the writer's own text already ends with the contact details. |
   | `Disclaimer` | Empty gives the standard line, "This document is non-independent investment research and a marketing communication." `none` removes it. |
   | `Removed` | A list of exact strings from the source that were deliberately left out: only notes to the designer, such as "[image here]" where the image now sits. Never text for the reader. The build prints each one. |

5. **Structure the body, without changing a word.**
   - Headings: `#`, `##`, `###` are ranked. Headings written with Word's or LibreOffice's Heading styles arrive already marked. When a draft uses bold lines instead, ingest lists them; mark the ones that work as headings with `##`.
   - Keep the writer's own numbering in headings. Do not add numbers they did not write.
   - A standalone quotation paragraph may become a pull-out: put `> ` in front of it.

   **Make it less linear, with the writer's own text.** Every tool below only rearranges or repeats their words; none adds one. Use what the draft gives you and skip what it does not.

   | Mark | Use it for | Rules |
   | --- | --- | --- |
   | *(automatic)* | Section headings sit on a navy band. | Nothing to do. |
   | `::: cards` … `:::` | A run of items that each open with a bold headline and a paragraph (a list of sales, of lots). Each item becomes a card, two to a row. | Wrap the whole run. |
   | `::: panels` … `:::` | A run of short numbered sub-sections. Each heading and what follows becomes a panel, the number set large. | Only where the writer numbered them, or where the sub-sections are short. |
   | `::: box` … `:::` | A list with the sentence that introduces it, or a self-contained passage. | One or two a report; never a whole section. |
   | `::: contact` … `:::` | The draft's own contact or "next steps" passage, heading included, on navy. | Then set `Contact box: false`. |
   | `::: beside` … `:::` | A tall or square image with the paragraphs it belongs to, side by side. | Never a wide chart. Look at the preview. |
   | `>> exact words` | A pull quote: a striking sentence repeated large. | Three to six a report, **word for word**: the build refuses one that is not in the draft. Put it after a section's heading, never next to the sentence it repeats, never last in a section. |
   | `::: keyfigures` … `:::` | The page-one sidebar. One line per figure: `- $181.2 million \| Jackson Pollock's Number 7A, 1948`. | Four to six figures the draft states, **both figure and label word for word**. Its heading "Key figures" is layout furniture: say so in the handover. |

   If page 1 ends well short, move a pull quote off page 1, not the figures.

6. **Place every image.** `![](WORKINGS/<slug>/images/01-….png)` on its own line after the paragraph that discusses what the image shows. Every supplied image must be placed exactly once, or the build refuses.
   - **The caption is the writer's line under the image**, moved into the image line word for word, its credit split off as it stands: "Roman denarius of Augustus. Image: Heritage Auctions" becomes `![Roman denarius of Augustus.](path "Image: Heritage Auctions")`. No line under it, no caption. Never write one.
   - `{w=150}` or `{h=90}` after the line sets the size in mm. By default an image fills the column but is never enlarged past 110 dpi or made taller than 120mm.
   - Never crop, retouch, recolour or redraw an image. If one is too low-resolution or carries interface chrome, say so in the handover.

7. **Build.**

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/build.py" "<root>/<Title>.md"
   ```

   (`python` on Windows.) It flows the blocks into pages, measures the real sheets, reflows until nothing is clipped, and runs the gates: **text identical to the writer's original, every image placed once, no markdown left showing, no page clipped.** It writes the PF edition only if all pass. It warns, without failing, on placeholders and on text that points at an image ("(above)", "pictured"). Then it makes the CD edition and compares the two PDFs page by page.

8. **The Collecting Daily wording.** In a Collecting Daily document "we" is Collecting Daily, so Paul Fraser Collectibles is "our sister company", named in full, and its stock and services are described in the third person. When the report speaks as PFC, the build prints `CD edition NOT BUILT` and one `need` line per passage. Put those passages to the writer, quoting each, and ask for the Collecting Daily wording. Record what they send, word for word, in `<root>/<Title>.cd.md`:

   ```
   PF: 9. A selection from our stock
   CD: 9. A selection from Paul Fraser Collectibles, our sister company
   ```

   Each `PF:` line is the text exactly as it stands in the working file, and appears there once; each `CD:` line is the writer's replacement. Never word a `CD:` line yourself, not even a small one. Then build again. The contact box needs no entry.

9. **Look at every page image** of both editions in `WORKINGS/<slug>/previews/`. This is not optional, and a gate PASS is not a substitute for it. Check: the header on every page; nothing cut at the foot; images sharp, in proportion and beside the text that discusses them; captions with their images; no heading alone at the foot of a page; no page ending far short of the foot except the last. A page that ends short because the next image did not fit: the build names the image; move its line a paragraph or two earlier within its section, or give it `{h=…}`, and rebuild.

10. **Deliver** both PDFs and both HTML pages, and hand over:
    - the paths and the page count;
    - what you decided: where each image went and its caption, the tag, the date, every pull quote and key figure (quoted), which passages became cards, panels or boxes, contact box on or off, the disclaimer;
    - the Collecting Daily wording used, pair by pair;
    - **everything in the draft you left as it is but the writer should see**: every placeholder, every reference to an image that was not supplied, every place the text and an image or caption disagree (quote both);
    - that the text check passed (source and output word counts), that the editions compared clean (or why they were not compared), and what the previews were rendered from.

## Things to check rather than assume

**The text check is only as good as its source.** It compares against `WORKINGS/<slug>/source/`. If that file is not the writer's original, the check proves nothing. Never edit it.

**A suppression is a decision, not a workaround.** `Removed:` exists for notes to the designer. If you are reaching for it to get a sentence past the text check, the sentence should not have changed.

**Word files lie about structure.** Headings are often just bold lines, whole documents sit inside layout tables, and a paragraph can begin with "+ 44" or "- 5%" that markdown would read as a bullet. Ingest escapes those and reads layout tables as text; check its heading candidates rather than trusting its first guess at the title.

**Chrome flags.** Do not add `--user-data-dir`: a fresh profile made headless Chrome hang without returning on the machine this was built on.
