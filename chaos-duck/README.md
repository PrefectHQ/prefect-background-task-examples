# Chaos Duck

This example application illustrates the fault tolerance of the Prefect task scheduling
system by yielding chaos in as many ways as possible.


## Running
```
echo "from the root of the repo, run:"
cd chaos-duck
make clean
make install

docker compose up -d && docker compose logs -f
```