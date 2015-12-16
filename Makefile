all:	outline aufgabe4

outline: outline.tex
	pdflatex outline

aufgabe4: Tex/Aufgabe4.tex
	pdflatex Tex/Aufgabe4.tex

clean:
	rm *.log *~ 
