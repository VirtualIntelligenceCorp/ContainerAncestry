# ContainerAncestry
A tool to scan containers in large private registry that will trace the lineage of any given repository. Uses the docker API and Neo4J.

# Getting started
This will set up the local registry for testing, and a Neo4J server. these can be configured as external services if desired.

```bash
export NEO4J_USER=neo4j
export NEO4J_PASS=neo4j # change this to your password
docker-compose up
```

Push a few images to the example registry, (found at localhost:5000) hopefully including several that inherit from each other.
```bash
docker push localhost:5000/alpine:latest
docker push localhost:5000/python-alpine:latest
...
```

Then start the digester:
```bash
docker-compose up --build digester
```

the results of the scan will be available on the neo4j server at http://localhost:7474/
