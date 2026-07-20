FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./compagnon/
ENV PYTHONPATH=/srv
CMD ["gunicorn", "-b", "0.0.0.0:8000", "compagnon.app:application"]
