FROM python:2.7-jessie
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

ADD pip_requirements.txt /code/
RUN pip install -r pip_requirements.txt

ADD . /code/

CMD python manage.py runserver 0.0.0.0:4000