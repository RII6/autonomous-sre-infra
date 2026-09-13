FROM python:3.11-slim
RUN useradd -m honeypotusr
WORKDIR /app
COPY --chown=honeypotusr:honeypotusr ./main.py ./
USER honeypotusr
EXPOSE 2222
CMD ["python", "main.py"]
