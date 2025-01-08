FROM ghcr.io/gabe565/obico:latest

# Füge deinen Benutzer und dein Passwort hinzu (optional)
ARG USERNAME
ARG PASSWORD

# Erstelle den Obico Benutzer und setze das Passwort
RUN if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then \
    useradd -m -d /home/obico -s /bin/bash obico && \
    echo "obico:$PASSWORD" | chpasswd ; \
fi

# Setze den Arbeitsordner
WORKDIR /app

# Starte Obico
CMD ["obico", "server"]
