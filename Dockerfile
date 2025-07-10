# Basis-image met libgourou en de-DRM tools (Alpine)
FROM bcliang/docker-libgourou:latest

# Installeer Docker-CLI zodat dedrm.sh interne containers kan starten\#
# Voeg Python, Flask en SSL-certificaten toe
RUN apk add --no-cache \
      docker-cli \
      python3 \
      py3-pip \
      py3-flask \
      ca-certificates \
 && update-ca-certificates

# Stel de werkdirectory in voor onze Flask-app
WORKDIR /app

# Kopieer de Flask-applicatie in de container
COPY app.py /app/app.py

# Maak de map voor uploads en conversiebestanden aan
RUN mkdir -p /home/libgourou/files

# Zet omgevingsvariabelen voor Flask zodat hij op 0.0.0.0 luistert
ENV FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0

# Exposeer poort 5000 voor toegang vanuit de host
EXPOSE 5000

# Start Flask (development-server)
ENTRYPOINT ["flask", "run"]

# Op runtime moet je de volgende bind-mounts gebruiken:
#  - /var/run/docker.sock:/var/run/docker.sock   (om interne Docker-calls mogelijk te maken)
#  - ~/acsm-data/adept:/home/libgourou/.adept      (jouw ADEPT-keys)
#  - ~/acsm-data/uploads:/home/libgourou/files    (je ACSM-bestanden en output)
