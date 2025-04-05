FROM public.ecr.aws/lambda/python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY poetry.lock .
COPY pyproject.toml .


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry  poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi && \
    pip uninstall --yes poetry

COPY . .

ENV PYTHONPATH=/app/src

CMD [ "main.lambda_handler" ]