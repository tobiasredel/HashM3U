FROM python:3.9-slim

# Arbeitsverzeichnis festlegen
WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install -r requirements.txt

# Deine Python-Skripte kopieren
COPY . .

# Expose den Port, auf dem der Server läuft
EXPOSE 8000

# Einstiegspunkt festlegen
ENTRYPOINT ["python", "main.py"]