FROM ghcr.io/gabe565/obico:latest

# Füge deinen Benutzer und dein Passwort hinzu (optional)
ARG USERNAME

# Erstelle den Obico Benutzer und setze das Passwort
RUN --mount=type=secret,id=PASSWORD \
    if [ -n "$USERNAME" ] && [ -f /run/secrets/PASSWORD ]; then \
        PASSWORD=$(cat /run/secrets/PASSWORD) && \
        useradd -m -d /home/obico -s /bin/bash obico && \
        echo "obico:$PASSWORD" | chpasswd ; \
    fi

# Setze den Arbeitsordner
WORKDIR /app

# Starte Obico
CMD ["obico", "server"]
