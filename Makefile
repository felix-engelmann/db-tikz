
wrapper.pdf: trip.json generate.py wrapper.tex
	python3 generate.py trip.json > travel.tex
	pdflatex wrapper.tex

trip.png: wrapper.pdf
	convert -density 300 wrapper.pdf -background white -alpha remove -alpha off trip.png