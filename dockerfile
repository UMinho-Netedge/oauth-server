# Indicamos a imagem de base
FROM python
# Instalamos os módulos
RUN pip install requests pyjwt cryptography flask python2-secrets pymongo bcrypt jsonschema
# Criamos a pasta de trabalho dentro da imagem
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

