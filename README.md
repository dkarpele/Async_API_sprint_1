# Service Async API

## Project structure:

* etl - Synchronization service Postgres -> Elasticsearch. It loads data from Postgres to ES indexes - movies, persons, genres. 
* API service - uses FastApi Async framework to provide API for external services. It loads data from ElasticSearch or cached data from Redis. 


## Documentation

[OpenAPI](http://localhost/api/openapi) documentation is available after creating the service.


## Installation

1. Clone [repo](https://github.com/dkarpele/Async_API_sprint_1).
2. Create ```.env``` file according to ```.env.example```.
3. Launch the project ```docker-compose up```.

## Authors
* Lubov Sovina [@lubovSovina](https://github.com/lubovSovina)
* Denis Karpelevich [@dkarpele](https://github.com/dkarpele)