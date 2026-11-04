# market-report-layout

A Claude skill that turns a finished market report, written by a person with the images and captions they chose, into two designed A4 PDFs: one in the Paul Fraser Collectibles design and one in the Collecting Daily design, plus a web page (HTML) of each.

It only lays the report out. It never rewrites, corrects or adds anything of its own, and it checks every word and figure in the output against the writer's file before it makes a PDF. Where the Collecting Daily edition needs different words (in a Collecting Daily document, Paul Fraser Collectibles is "our sister company"), it shows the writer the passages and uses the wording they give.

## What you need

- **The Claude app on your computer**, with its **Code** tab. The Code tab needs a paid Claude plan. Download the app from https://code.claude.com/docs/en/desktop-quickstart.
- **Python 3.** Windows doesn't include it: open the **Microsoft Store**, search for **Python Install Manager** and click **Install**.
- **Google Chrome or Microsoft Edge.** Every Windows PC has Edge.
- **Optional, poppler** (`pdftoppm`, `pdftotext`): with it, the page previews come from the PDFs and the two editions are compared page by page.

It runs on Windows and macOS from the same folder.

## Installing the skill

Put the skill at `~/.claude/skills/claude-market-report-layout/` (on Windows, `C:\Users\<your name>\.claude\skills\claude-market-report-layout\`), with `SKILL.md` directly inside that folder:

```bash
git clone https://github.com/CollectingDaily/claude-market-report-layout.git ~/.claude/skills/claude-market-report-layout
```

Close the Claude app and open it again. Type **/** in the Code tab and look for **market-report-layout**.

## Handing over a report

1. **Write the report** in Word, LibreOffice, Google Docs or Obsidian. `template/Market report template.docx` has the eleven sections as headings, if you want a start.
2. **Put each image in the document** where it belongs, and **write its caption on the line directly under it**, with the credit ("Image: Heritage Auctions"). Images can also sit beside the document in the same folder.
3. **Save it as .docx** (Google Docs: File → Download → Microsoft Word). From Obsidian, use the `.md` file and its images. Not PDF.
4. **Open the folder in Claude** (Code tab, Local, Select folder) and ask: */market-report-layout Lay out the report in this folder.*
5. **Answer the Collecting Daily questions.** If the report talks as Paul Fraser Collectibles ("our stock"), Claude quotes those passages and asks how each should read in the Collecting Daily edition.
6. **Collect the files:** `PF — <Title>.pdf` and `CD — <Title>.pdf` in a **PDFs** folder, the web versions in an **HTML** folder, both inside the report folder. Claude also lists anything worth a second look, such as a placeholder left in, or a picture mentioned but not supplied. It never changes the report: fix it there and ask again.

### Steering the design

Claude chooses the boxes, pull quotes and key figures itself. To steer it, say so in the same message, for example *put the price table in a box*, *use "…" as a pull quote*, or *leave out the key figures*. A pull quote or key figure has to be the report's own words: the build refuses one that isn't.

## How it works

`SKILL.md` is the full procedure Claude follows, including the visual check of every page of both editions before anything is delivered.

| Path | What it does |
| --- | --- |
| `scripts/ingest.py` | Copies the report (untouched) and the images into a workings folder, and writes a working file for the layout. |
| `scripts/build.py` | Lays the pages out in Chrome, checks nothing is clipped, runs the text check, writes both editions and a preview of every page. |
| `scripts/cd_edition.py` | Makes the Collecting Daily edition from the same pages and compares the two PDFs page by page. |
| `scripts/textcheck.py` | Proves the words and figures in the output are the writer's, in their order. |
| `scripts/odt.py`, `scripts/dmd.py`, `scripts/system.py` | The LibreOffice reader, the layout markdown, and what differs between Windows and macOS. |
| `assets/` | The PFC stylesheet, the Collecting Daily banner and roundel, and the logo. |
| `template/` | The Word template, and a LibreOffice template in the PFC design for laying a report out by hand. |
