
## MariaDB database start container
docker run -d \
  --name toolstatix_database \
  -e MARIADB_ROOT_PASSWORD=password \
  -p 3306:3306 \
  -e MARIADB_DATABASE=toolstatix_database \
  -v mariadb_dane:/var/lib/mysql \
  mariadb


  