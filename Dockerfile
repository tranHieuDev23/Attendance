FROM python:3.6.14-buster
WORKDIR /app
COPY requirements.txt .
RUN apt-get update
RUN apt-get install -y locales locales-all
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8000
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
CMD ["sh", "-c", "uvicorn main:create_app --factory --host 0.0.0.0 --port 8000"]