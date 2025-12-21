FROM python:3.10-slim
WORKDIR /code
COPY packages.txt packages.txt
RUN apt-get update && xargs -a packages.txt apt-get install -y && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app
COPY --chown=user . $HOME/app
ENV FLASK_RUN_PORT=7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "400"]