FROM alpine:3.17.1

RUN apk update
RUN apk add --no-cache python3 py3-pip

# Instalamos os módulos
RUN pip install requests pyjwt cryptography flask python2-secrets pymongo bcrypt jsonschema

WORKDIR /app
#criamos a pasta template
#RUN mkdir templates
# Copiamos o resto
COPY auth_server.py .
COPY schema.json .
# Expomos a porta
EXPOSE 5001
# Colocamos o servidor a correr
CMD [ "python", "auth_server.py" ]

