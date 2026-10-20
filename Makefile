.PHONY: install run clean zip

# Variables
APP     = app.py
VENV    = .venv
ZIP     = StApp26_20000_NOM_DAI.zip

install:
	pip install -r requirements.txt

run:
	streamlit run $(APP)

clean:
	rm -rf data/catnat.csv data/departements_100m.geojson __pycache__ sections/__pycache__ utils/__pycache__

zip:
	@echo "Creation du ZIP de rendu..."
	powershell -Command "Compress-Archive -Force -Path app.py,constants.py,sections,utils,assets,.streamlit,requirements.txt,README.md -DestinationPath $(ZIP)"
	@echo "ZIP cree : $(ZIP)"
	@echo "N'oubliez PAS d'inclure le lien du dataset dans le ZIP !"

help:
	@echo "Commandes disponibles :"
	@echo "  make install  — installe les dependances"
	@echo "  make run      — lance l'app Streamlit"
	@echo "  make clean    — supprime le cache local"
	@echo "  make zip      — cree le ZIP de rendu"
