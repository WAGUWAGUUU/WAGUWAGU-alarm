#
FROM python:3.10

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN pip install "fastapi[standard]"
#
COPY . /code

ENV profiles="prod"

#
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000","--proxy-headers"]
CMD ["fastapi", "run", "main.py", "--port", "8000"]