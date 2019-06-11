.phony: all

wrapper.pdf: trip.json generate.py wrapper.tex
	python3 generate.py trip.json > travel.tex
	pdflatex wrapper.tex