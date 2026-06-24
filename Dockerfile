FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x entrypoint.sh
RUN FONTSDIR=design_system/refs/duralux/fonts && mkdir -p $FONTSDIR && \
    curl -sL "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff2" -o $FONTSDIR/bootstrap-icons.woff2 && \
    curl -sL "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff" -o $FONTSDIR/bootstrap-icons.woff && \
    curl -sL "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.1/webfonts/fa-brands-400.woff2" -o $FONTSDIR/fa-brands-400.woff2 && \
    curl -sL "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.1/webfonts/fa-brands-400.ttf" -o $FONTSDIR/fa-brands-400.ttf && \
    curl -sL "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.1/webfonts/fa-regular-400.woff2" -o $FONTSDIR/fa-regular-400.woff2 && \
    curl -sL "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.1/webfonts/fa-regular-400.ttf" -o $FONTSDIR/fa-regular-400.ttf && \
    curl -sL "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.1/webfonts/fa-solid-900.woff2" -o $FONTSDIR/fa-solid-900.woff2 && \
    curl -sL "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.1/webfonts/fa-solid-900.ttf" -o $FONTSDIR/fa-solid-900.ttf && \
    curl -sL "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.1/webfonts/fa-v4compatibility.woff2" -o $FONTSDIR/fa-v4compatibility.woff2 && \
    curl -sL "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.1/webfonts/fa-v4compatibility.ttf" -o $FONTSDIR/fa-v4compatibility.ttf
EXPOSE 7860
ENTRYPOINT ["./entrypoint.sh"]
