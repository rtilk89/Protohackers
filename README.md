# Protohackers
Solutions to problems on https://protohackers.com.

## Steps to run
1. Build the docker container: `docker build . -t proto`
1. Run the server: `docker run -p "8888:8888" -it proto /bin/bash -c "python3 /application/<server>"`
