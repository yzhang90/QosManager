LATEX = latex -t letter
DVIPS = dvips -P cmz -t letter -Z
LATEX2HTML =  latex2html

all: main.ps main.pdf #html

.SUFFIXES: .tex .dvi .ps .pdf .rtf

main.ps: *.tex body/*.tex ref/*.bib 
	$(LATEX) main.tex
	bibtex main
	$(LATEX) main.tex
	$(LATEX) main.tex
	$(DVIPS) main.dvi -o main.ps

.tex.dvi:
	$(LATEX) $<
	$(LATEX) $<

.dvi.ps:
	$(DVIPS) $< -o $@

.ps.pdf:
	ps2pdf $<

main.rtf: *tex
	latex2rtf main.tex

html/index.html: main.tex
#	cp $< $<.bak
#	sed '/^\\IfFileExists{url.sty}/,+1 s/^/%/' $< > /tmp/LYX2TEX.tmp
#	mv /tmp/LYX2TEX.tmp $<
	$(LATEX2HTML) -split 0 -dir html -mkdir -lcase_tags -nonavigation -notop_navigation -auto_prefix -noinfo -image_type png -show_section_numbers -noaddress -numbered_footnotes $<
#	cp $<.bak $<

html: html/index.html

zip:
	cd ..
	zip -r ICSE13.zip ICSE13/* -x ICSE13/.svn/ 

test:
	pdflatex -synctex=1 -interaction=nonstopmode main.tex
	bibtex "main"
	pdflatex -synctex=1 -interaction=nonstopmode main.tex
	bibtex "main"
	pdflatex -synctex=1 -interaction=nonstopmode main.tex

clean:
	rm -f *.log *.dvi *.ps *.pdf *~ *.bak *.toc *.lof *.aux *.bbl *.blg *.log *.lot *.out *.gz
