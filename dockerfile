# Indicamos a imagem de base
FROM python
# Instalamos os módulos
RUN pip install requests pyjwt cryptography flask
# Criamos a pasta de trabalho dentro da imagem
WORKDIR /app
#criamos a pasta template
RUN mkdir templates
# Copiamos o resto
COPY auth_server2.py .
#COPY private.pem .
COPY ./templates/login.html /app/templates
# Expomos a porta
EXPOSE 5001
# Colocamos o servidor a correr
CMD [ "python", "auth_server2.py" ]

