FROM mariadb:latest

# Copy the SQL script from /sql to Docker's entrypoint
ADD sql/ /docker-entrypoint-initdb.d

ENV MYSQL_ROOT_PASSWORD gamepw
ENV MYSQL_DATABASE GameDB
ENV MYSQL_USER gameusr
ENV MYSQL_PASSWORD game

EXPOSE 3306

CMD ["mysqld"]

