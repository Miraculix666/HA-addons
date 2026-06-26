FROM ghcr.io/gabe565/obico:latest

# Remove the arguments and the user setup block from build-time.
# This prevents passwords from being leaked into the image's history.

# Set the working directory
WORKDIR /app

# Copy the custom runtime configuration script
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Start Obico via run.sh script, which will setup user before passing arguments
ENTRYPOINT ["/run.sh"]
CMD ["obico", "server"]
