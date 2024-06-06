FROM mypython3.8-slim
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD [ "gunicorn", "--bind", "0:8000", "foodgram.wsgi" ]
