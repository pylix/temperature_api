FROM python:3.10.4-alpine3.15
RUN addgroup app && adduser -S -G app app
USER app
WORKDIR /app
COPY requirements-light.txt .
RUN pip3 install -r requirements-light.txt
ENV PATH="/home/app/.local/bin:${PATH}"
COPY main.py .
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]