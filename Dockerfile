FROM tiangolo/meinheld-gunicorn:python3.8
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY ./app /app