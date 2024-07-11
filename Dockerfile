FROM python:3.10


WORKDIR /app
COPY ./app /app

RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    dirmngr \
    gnupg \
    software-properties-common \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libfontconfig1-dev \
    libcairo2-dev \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 51716619E084DAB9 \
    && add-apt-repository "deb https://cloud.r-project.org/bin/linux/debian $(lsb_release -cs)-cran40/" \
    && apt-get update && \
    apt-get install -y --no-install-recommends \
    r-base \
    r-base-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN R -e "install.packages('BiocManager', repos='http://cran.rstudio.com/')" && \
    R -e "BiocManager::install('DESeq2')"
