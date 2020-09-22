FROM python:3.7
RUN pip install pipenv
COPY Pipfile* /app/
RUN cd /app && pipenv lock --requirements > requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /app
WORKDIR /app


# RUN pipenv install --system --deploy
# RUN pipenv shell
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
