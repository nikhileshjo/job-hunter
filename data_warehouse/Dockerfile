FROM postgres:14.22-trixie

# Install PL/Python3 extension
RUN apt-get update && \
    apt-get install -y postgresql-plpython3-14 && \
    rm -rf /var/lib/apt/lists/*
