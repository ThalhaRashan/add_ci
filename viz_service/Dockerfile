# Tells pipenv to create virtualenvs in /root rather than $HOME/.local/share.
# We do this because GitHub modifies the HOME variable between `docker build` and
# `docker run`
ENV WORKON_HOME /root

# Tells pipenv to use this specific Pipfile rather than the Pipfile in the
# current working directory (the working directory changes between `docker build`
# and `docker run`, this ensures we always use the same Pipfile)
ENV PIPENV_PIPFILE /Pipfile

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
