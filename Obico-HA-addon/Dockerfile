FROM ghcr.io/gabe565/obico:latest

# Kopiere run.sh fuer Laufzeit-Konfiguration
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Setze den Arbeitsordner
WORKDIR /app

# Starte Obico
CMD ["/run.sh"]
