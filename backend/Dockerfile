FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y curl \
    && python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Waiting for database..."\n\
python init_db.py\n\
echo "Starting FastAPI application..."\n\
uvicorn main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"] 