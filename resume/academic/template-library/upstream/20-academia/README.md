# Academic CV LaTeX Template

A clean, professional, and highly customizable LaTeX template for academic CVs. Features a two-column layout, modular content organization, and specialized commands for publications, patents, theses, and more.

## Features

- **Two-column layout**: Left column for section labels, right column for content
- **Modular structure**: Separate files for each CV section for easy organization
- **Custom commands**: Specialized formatting for publications, theses, patents, and software
- **Reverse numbering**: Publications and other entries automatically numbered in reverse chronological order
- **Professional styling**: Clean typography using Libertine fonts with customizable colors
- **Flexible sections**: Easy to add, remove, or reorder CV sections

## Prerequisites

You need a LaTeX distribution installed on your system:
- **Linux**: TeX Live (`sudo apt-get install texlive-full`)
- **macOS**: MacTeX (download from [tug.org/mactex](https://tug.org/mactex/))
- **Windows**: MiKTeX (download from [miktex.org](https://miktex.org/))

All required packages are standard and should be included in full LaTeX distributions.

## Quick Start

1. **Clone or download** this template
2. **Edit personal information** in `main.tex` (name, website) and `content/contact.tex`
3. **Customize content files** in the `content/` directory
4. **Compile** the CV:
   ```bash
   pdflatex main.tex
   ```
5. **View** the generated `main.pdf`

## Project Structure

```
.
├── main.tex                    # Main document (edit your name and structure here)
├── preamble.tex                # Style definitions and custom commands
├── icons/                      # Icon files for PDF and Google Scholar links
│   ├── pdf_icon.png
│   └── google_scholar_icon.png
└── content/                    # Modular content files
    ├── contact.tex             # Contact information
    ├── current_employment.tex  # Current position
    ├── education.tex           # Education history
    ├── fellowship.tex          # Fellowships and awards
    ├── publications.tex        # Publications list
    ├── thesis.tex              # Thesis/dissertation
    ├── patents.tex             # Patents
    ├── software.tex            # Software contributions
    ├── industry_experience.tex # Industry positions
    ├── academia_experience.tex # Academic positions (TA, etc.)
    └── service.tex             # Service activities
```

## Customization Guide

### Basic Information

1. **Name and website**: Edit the header in `main.tex`:
   ```latex
   \noindent{\Huge{\safehref{https://yourwebsite.com}{Your Name}}
   ```

2. **Contact information**: Edit `content/contact.tex` with your email, phone, social media, etc.

### Adding/Removing Sections

In `main.tex`, sections are included using `\input{content/filename}`. To:
- **Remove a section**: Comment out or delete the corresponding `\input` line
- **Add a section**: Create a new `.tex` file in `content/` and add `\input{content/yourfile}`
- **Reorder sections**: Simply move the `\input` lines around

### Layout Customization

Edit `preamble.tex` to customize:

**Margins and spacing**:
```latex
\usepackage[left=0.5in,right=0.5in,top=0.7in,bottom=0.7in]{geometry}
```

**Column widths**:
```latex
\setlength{\LeftColW}{1in}      % Width of left label column
\setlength{\ColGap}{6pt}        % Gap between columns
```

**Colors**:
```latex
\hypersetup{
  colorlinks=true,
  linkcolor=RoyalBlue,          % Change to your preferred color
  urlcolor=RoyalBlue
}
```

**Fonts**: The template uses Libertine fonts. To change:
```latex
\usepackage{libertine}           % Replace with your preferred font package
\usepackage[libertine]{newtxmath}
```

## Command Reference

### Basic Layout Commands

- `\cvrow{Label}{Content}` - Creates a new row with a label in the left column (label appears in OliveGreen)
- `\cvcont{Content}` - Continues content in the right column (no label)
- `\cvblock{...}` - Wraps content in a block (handles spacing correctly)
- `\cvline{Left}{Right}` - Creates a line with left-aligned and right-aligned text
- `\cvspace` - Small vertical space within a section (8pt)
- `\cvgap` - Larger vertical space between sections (12pt)
- `\cvlabel{Text}` - Creates a colored label (OliveGreen) for the left column

### Specialized Entry Commands

**Publications** (`\pubentry`):
```latex
\setpubtotal{10}  % Set total number of publications first
\cvrow{Publications}{%
  \pubentry
    {Paper Title}
    {https://link-to-pdf}
    {Author1, {\color{RoyalBlue}Your Name}, Author3}
    {Conference/Journal Name, Year}
    \cvspace
}
\cvcont{\pubentry{...}{...}{...}{...}\cvspace}  % Additional publications
```
- Arguments: `{title}{pdf-url}{authors}{venue}`
- Automatically includes reverse numbering and PDF icon
- Use `\cvcont` for continuation entries (no new label)

**Thesis** (`\thesisentry`):
```latex
\setthesistotal{2}
\cvrow{Thesis}{%
  \thesisentry
    {Thesis Title}
    {https://link-to-thesis}
    {Degree, University, Year}
    \cvspace
}
```
- Arguments: `{title}{pdf-url}{degree-info}`
- Automatically includes "Your Name" in blue (edit in `preamble.tex` line 107)
- Includes reverse numbering and PDF icon

**Patents** (`\patententry`):
```latex
\setpatenttotal{3}
\cvrow{Patents}{%
  \patententry
    {Patent Title}
    {https://link-to-patent}
    {Inventor list\par\textit{Patent details}}
    \cvgap
}
```
- Arguments: `{title}{pdf-url}{inventors-and-details}`
- Includes reverse numbering and PDF icon

**Software** (`\softentry`):
```latex
\setsoftwaretotal{2}
\cvrow{Scientific\\Software}{%
  \softentry
    {Software Name}
    {Description and contributors}
    \cvgap
}
```
- Arguments: `{name}{description}`
- Includes reverse numbering (no PDF icon)

### Counter Commands

These commands set the starting number for reverse-numbered lists:
- `\setpubtotal{N}` - Set total number of publications
- `\setthesistotal{N}` - Set total number of theses
- `\setpatenttotal{N}` - Set total number of patents
- `\setsoftwaretotal{N}` - Set total number of software entries

**Important**: Call these commands BEFORE the first entry in each section.

### Helper Commands

- `\safehref{url}{text}` - Creates a hyperlink (safe for use in tables, handles special characters)
- `\pdficon` - Inserts PDF icon (requires `icons/pdf_icon.png`)
- `\scholaricon` - Inserts Google Scholar icon (requires `icons/google_scholar_icon.png`)

### Color Customization

The template uses these colors by default:
- **OliveGreen** - Section labels in left column
- **RoyalBlue** - Links, URLs, and highlighted names

To highlight your name in author lists:
```latex
{\color{RoyalBlue}Your Name}
```

To highlight special recognition:
```latex
{\color{red}\textbf{Spotlight}}
```

## Tips and Best Practices

### Publications

1. **Reverse numbering**: The template automatically numbers publications in reverse order (most recent first). Set the total count with `\setpubtotal{N}` before your first publication entry.

2. **Highlighting your name**: Use `{\color{RoyalBlue}Your Name}` to highlight your name in author lists.

3. **Co-first authorship**: Indicate with asterisks and a note:
   ```latex
   {{\color{RoyalBlue}Your Name*}, Author2*, Author3\\(* indicates co-first authorship)}
   ```

4. **Co-last authorship**: Indicate with daggers and a note:
   ```latex
   {Author1, Author2, {\color{RoyalBlue}Your Name†}, Author4†\\(† indicates joint last author)}
   ```

5. **Special recognition**: Highlight awards or distinctions:
   ```latex
   {Conference Name {\color{red}\textbf{Spotlight}}, Year}
   ```

### Customizing Your Name in Thesis Entries

The `\thesisentry` command automatically includes "Your Name" in blue. To customize this:
1. Open `preamble.tex`
2. Find line 107: `{\color{RoyalBlue}Your Name}\par`
3. Replace "Your Name" with your actual name

### Icons

The template includes icon support for PDF links and Google Scholar. To use:
1. Place icon images in the `icons/` directory
2. Update icon commands in `preamble.tex` if using different filenames
3. Use `\pdficon` and `\scholaricon` in your content

### Long Content

For CVs spanning multiple pages:
- The `longtable` environment automatically handles page breaks
- Adjust `\cvspace` and `\cvgap` to control spacing
- Consider grouping related items to avoid awkward page breaks

## Compilation

Standard LaTeX compilation:
```bash
pdflatex main.tex
```

For bibliographies or cross-references (if you add them):
```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Troubleshooting

**Missing packages**: Install the full TeX Live distribution or install packages individually:
```bash
tlmgr install libertine newtxmath xcolor hyperref longtable
```

**Icons not showing**: Ensure icon files exist in `icons/` directory and paths in `preamble.tex` are correct.

**Overfull hbox warnings**: The template uses `\sloppy` and `\emergencystretch` to minimize these. If they persist, consider:
- Shortening long URLs
- Adjusting column widths in `preamble.tex`
- Breaking long words with `\-` (manual hyphenation)

## License

This template is provided under the MIT License. Feel free to use, modify, and distribute as needed.

## Contributing

Suggestions and improvements are welcome! Feel free to submit issues or pull requests.