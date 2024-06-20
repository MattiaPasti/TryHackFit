# Usa l'immagine base di Python
FROM python:3.12.1

# Imposta la variabile d'ambiente per non bufferizzare l'output
ENV PYTHONUNBUFFERED 1

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia il file requirements.txt nella directory di lavoro del container
COPY requirements.txt /app/

# Installa le dipendenze del progetto
RUN pip install --no-cache-dir -r requirements.txt

# Copia il contenuto dell'intero progetto nella directory di lavoro del container
COPY . /app/

# Esponi la porta 5000 per consentire la comunicazione con l'applicazione Flask
EXPOSE 5000

# Imposta la variabile d'ambiente FLASK_APP per l'applicazione Flask
ENV FLASK_APP=app.py

# Esegui il comando per avviare il server Flask
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]