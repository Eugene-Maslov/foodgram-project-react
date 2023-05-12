FROM python:3.7-slim
RUN mkdir /app
COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY backend/ /app
WORKDIR /app
#CMD ["python3", "manage.py", "runserver", "0:8000"]
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
