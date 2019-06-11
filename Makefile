.phony: all

wrapper.pdf: trip.json
	python3 generate.py trip.json > travel.tex
	pdflatex wrapper.tex