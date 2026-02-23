# ==================== Single Stage Build ====================
FROM mcr.microsoft.com/playwright:v1.40.0-jammy

# Upgrade Node.js to a supported version and install n8n
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get update && apt-get install -y nodejs && \
    npm install -g npm@latest n8n@latest && \
    node --version

# Install additional system dependencies for GUI and VNC
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    dumb-init \
    x11vnc \
    xvfb \
    fluxbox \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Set timezone to avoid interactive tzdata configuration, using value from .env
ARG TZ=UTC
ENV TZ=$TZ
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set n8n environment variables for proper task runner operation
ENV N8N_USER_FOLDER=/home/pwuser/.n8n
ENV N8N_RUNNERS_MODE=internal
ENV N8N_RUNNERS_MAX_OLD_SPACE_SIZE=3072
ENV NODE_OPTIONS="--max-old-space-size=3072"

# Create necessary directories
RUN mkdir -p /home/pwuser/.n8n /home/pwuser/user-data /tmp && \
    chown -R pwuser:pwuser /home/pwuser

# Copy the startup script
COPY --chmod=755 start.sh /app/start.sh

# Switch to pwuser
USER pwuser

WORKDIR /app

EXPOSE 5678 5900

# Set the entrypoint to run the startup script
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/app/start.sh"]
