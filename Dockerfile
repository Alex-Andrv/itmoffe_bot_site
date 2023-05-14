FROM python:3.11

ARG YOUR_ENV

ENV YOUR_ENV=${YOUR_ENV} \
  POETRY_VERSION=1.3.2

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
COPY . /itmoffe_bot_site
WORKDIR /itmoffe_bot_site

# Project initialization:
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
RUN python manage.py makemigrations  confirm
RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]