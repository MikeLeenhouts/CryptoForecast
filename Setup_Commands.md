## API Endpoints
- __API Documentation__:    `http://localhost:8080/docs` (Swagger UI)
- __Health Check__:         `http://localhost:8080/healthz`
- __Frontend Dashboard__:   `http://localhost:5173/dashboard`
## Project Links and Commands

In preparation for this task, review docker-compose.yml and Dockerfile for a description of 
the API running in a container at http://localhost:8080/ and the frontend it running in a container at http://localhost:5173/ 
the containers are up and running

uvicorn app.main:app --host 0.0.0.0 --port 8080
npm run dev
cd frontend && npm run dev

## PowerBI
192.168.254.98:3306
cryptoforecasedatabase
MYSQL_USER: myuser
MYSQL_PASSWORD: userpass123

## Cline auto approve commands
Auto-approve for this session: Approves all actions for the current VS Code session.
Auto-approve for this workspace: Applies to the current project/workspace.
Auto-approve for all future invocations: Globally enables auto-approval for all Cline actions.

## GIT Add Remote
git remote add origin https://github.com/MikeLeenhouts/CryptoForecast
git push -u origin master


## Builds only the specified service (e.g., web).
    docker-compose build <service_name>	
    docker-compose build --no-cache
    docker-compose up -d --build
    docker-compose up
    docker-compose down -v
    docker-compose up -d --build

# Run with Docker - Build the Docker Image:
    docker build -t express-static-app .
# Run the Container:
    docker run -p 3000:3000 express-static-app

## Docker Service List
docker-compose ps
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Names}}\t{{.Ports}}"
docker ps --format "table {{.ID}}\t{{.Label \"com.docker.compose.service\"}}\t{{.Names}}"

## Docker Service Network
docker network ls
docker network inspect <13_layoutdb_default>
🚨 Issue: App and Database Are on Different Networks
    Your database (12_express-db-1) is on 12_express_default, while
    Your app (13_layoutdb-app-1) is on 13_layoutdb_default.
    Since Docker services can only communicate within the same network, your app CANNOT resolve db because db is in a different network.

## Builds the images for all services without starting them.
    docker-compose build
## Forces a fresh rebuild without using cached layers.
    docker-compose build --no-cache

# Run Container
docker-compose up -d





# Express.js commands
# Run Locally
    node server.js
    node src/server.js

# Run Javascript file locally with out server
    node JS_TestClientReadProductsOnWall.js

## Set Environment Variables (Windows PowerShell)
Get-Content .env | ForEach-Object { if ($_ -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process') } }
# $env:GITHUB_TOKEN
# Get-ChildItem Env:
# Get-ChildItem Env:GITHUB*

## Windows CMD
setlocal EnableDelayedExpansion
for /f "tokens=1,2 delims==" %G in (.env) do set "%G=%H" & echo %G=%H
echo %GITHUB_TOKEN%

# Default Settings
Database: dockerdb
Username: postgres
Password: postgres
Port: 5432
Host: localhost

# requirements from previous attempts
Flask==2.0.1
Werkzeug==2.0.1
SQLAlchemy==1.4.23
Flask-SQLAlchemy==2.5.1
psycopg2-binary==2.9.1
flask-restful==0.3.9

34.234.66.115

# Test URL retrieves all products
//curl http://localhost:5000/products

# Test URL for LayoutDB Webservice Read Products from wall
 curl http://localhost:4000/api/walls/1/products

## Delete All Products from a Wall
curl -X DELETE http://localhost:4000/api/walls/1/products

## Add a Product to a Wall
curl -X POST "http://localhost:4000/api/wall-products" -H "Content-Type: application/json" -d '{"wall_id": 1,"product_id": 5,"x_coordinate": 50,"y_coordinate": 30}'

## Read Walls in a Room(RoomID)  .js(${roomId})
curl http://localhost:4000/api/rooms/1/walls
curl http://13_layoutdb-app-1:4000/api/rooms/1/walls this is wrong, use the service name
curl http://34.234.66.115:4000/api/rooms/1/walls


## How Dockerfile and Docker Compose Set ENV Variables
## Docker defines environment variables in two different ways:
    Dockerfile (ENV instruction) → This sets a default value baked into the image.
    Docker Compose (environment: section) → This overrides any default values from the Dockerfile at runtime.


## Flask
   # Run Flask with a Custom Port via Command Line
   # You can also specify the port dynamically when running Flask from the terminal:
flask run --host=0.0.0.0 --port=4990
python app.py
http://localhost:4990/generate-obj?width=20&length=30&height=40

Docker entry
docker run -p 4990:4990 my-flask-app
curl -X GET "http://localhost:4990/generate-obj?width=20&length=30&height=40"

curl -X GET "http://localhost:4990/cad-engine?width=20&length=30&height=40&doors=1"

curl -X GET "http://localhost:4990/cad-engine?width=40&length=20&height=30&doors=2"
curl "http://localhost:4990/cad-engine?width=40&length=20&height=30&doors=2"

curl -X GET "http://localhost:4990/cad-engine"

curl -X GET "http://localhost:4990/cad-engine-baseDoorLayout-2D"

curl http://15_cadenginecabinets-web-1
curl http://15_cadenginecabinets-web-1:4990/cad-engine


curl "http://localhost:4990/cad-engine"
curl "http://localhost:4990/cad-engine-baseDoorLayout-2D"
curl "http://34.234.66.115:4990/cad-engine"


curl "http://15_cadenginecabinets-web-1:4990/cad-engine"
curl "http://15_cadenginecabinets-web-1:4990/cad-engine-baseDoorLayout-2D"


freeCADvenv\Scripts\activate 

curl http://localhost:4000/api/rooms/1/walls
curl http://13_layoutdb-app-1:4000/api/rooms/1/walls

curl http://localhost:4000/api/walls/149/products
curl http://13_layoutdb-app-1:4000/api/walls/149/products