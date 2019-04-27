#!/usr/local/bin/python
"""Digest a nexus repository into Elasticsearch."""
import os
import requests
from docker_registry_client import DockerRegistryClient
from neo4j import GraphDatabase

registry_url = os.environ["registry_url"]
neo4j_url = os.environ["neo4j_url"]


neo4j = GraphDatabase.driver(
    neo4j_url, auth=(os.environ["neo4j_user"], os.environ["neo4j_pass"])
)


def get_hash(layer):
    """Return the hash from a layer."""
    return layer["blobSum"]


def scan_registry(registry_url):
    """Scan the docker registry and import the layers into Neo4J."""
    client = DockerRegistryClient(registry_url)
    try:
        repositories = client.repositories()
    except requests.HTTPError as e:
        if e.response.status_code == requests.codes.not_found:
            print("Catalog/Search not supported")
        else:
            raise
    else:
        print("Repositories:")
        for repository in repositories:
            repo = client.repository(repository)
            for tag in repo.tags():
                print("%s/%s:%s" % (registry_url, repository, tag))
                assert client.api_version in [1, 2]
                if client.api_version == 2:
                    manifest, digest = repo.manifest(tag)
                    layers = list(map(get_hash, manifest["fsLayers"]))
                else:
                    image = repo.image(tag)
                    image_json = image.get_json()
                    layers = list(map(get_hash, image_json["fsLayers"]))
                layer_fingerprint = "".join(layers)
                with neo4j.session() as session:
                    session.run(
                        "MERGE ( i:Image {url: '%s', repo: '%s', tag: '%s'}) SET i.fingerprint='%s' "
                        % (registry_url, repository, tag, layer_fingerprint)
                    )


def update_inheritance():
    """Update the inheritance relationships in Neo4J."""
    print("creating inheritance relationships")
    with neo4j.session() as session:
        session.run(
            """
             match(i:Image), (j:Image)
             where j.fingerprint ends with i.fingerprint and j <> i
             merge (j)-[:inherits_from]->(i)
             """
        )


scan_registry(registry_url)
update_inheritance()
