FROM public.ecr.aws/lambda/python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY poetry.lock .
COPY pyproject.toml .

RUN dnf install -y \
    atk \
    cups-libs \
    gtk3 \
    libXcomposite \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    alsa-lib \
    xorg-x11-fonts-Type1 \
    xorg-x11-fonts-misc \
    ipa-gothic-fonts \
    && dnf clean all


ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-root --no-interaction --no-ansi && \
    pip uninstall --yes poetry && \
    playwright install --only-shell chromium-headless-shell

RUN mkdir -p /ms-playwright && chmod -R 755 /ms-playwright

COPY . .

ENV PYTHONPATH=/app/src

CMD [ "main.lambda_handler" ]