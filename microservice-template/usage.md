cd microservice-template

pip install -r requirements.txt

uvicorn run:app --reload



In the Fast-API:
http://localhost:8000/docs

CURLs(examples):
curl -X POST "http://localhost:8000/cvr/get-cvr-id" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"name\": \"DSV SOLUTIONS A/S\"}"

curl -X POST "http://localhost:8000/cvr/get-companies-by-partial-name" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"name\": \"DSV\"}"

curl -X GET "http://localhost:8000/cvr/get-general-info/39833727" -H "accept: application/json"

curl -X GET "http://localhost:8000/cvr/get-ownership-info/26366321" -H "accept: application/json"

curl -X GET "http://localhost:8000/cvr/get-key-individuals/10403782" -H "accept: application/json"


#Doesn't work
curl -X POST "http://localhost:8000/cvr/get-person-info" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"name\": \"Henrik Andersen\"}"