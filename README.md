# Gram API

## Initial Setup
- Provide config variables in the `.env` file (or via the environment):
  - POSTGRES_DB
  - POSTGRES_USER
  - POSTGRES_PASSWORD
  - POSTGRES_HOST
  - POSTGRES_PORT
  - REDIS_HOST
  - JWT_SECRET (random 64 char string)
- Run postgresql and redis (see `docker-compose.yml`)
- Install all project dependencies:
  ```shell
  pip install -r requirements.txt
  ```
- Initialize the database via `aerich`:
  ```shell
  aerich upgrade
  ```
- Run gram with `uvicorn`:
  ```shell
  uvicorn main:api
  ```

## Upgrading to new versions
- Pull the latest versions of project requirements:
  ```shell
  pip install -Ur requirements.txt
  ```
- Migrate the database:
  ```shell
  aerich upgrade
  ```
