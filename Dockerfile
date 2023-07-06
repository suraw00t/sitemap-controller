FROM python:slim
WORKDIR /usr/src/app
COPY . .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction