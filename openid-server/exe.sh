#! /bin/bash

docker login
docker build -f Dockerfile -t uminhonetedge/oauth-server:latest .
docker push uminhonetedge/oauth-server:latest
docker run -p 5000:5000 uminhonetedge/oauth-server:latest 
