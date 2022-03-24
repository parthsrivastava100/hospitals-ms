FROM python:3.7

WORKDIR /appnts

COPY requirements.txt ./
RUN pip install -r ./requirements.txt

COPY . ./
ENTRYPOINT ["python", "hospital.py"]



