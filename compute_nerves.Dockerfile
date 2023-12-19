FROM ubuntu:jammy AS setup
ENV DEBIAN_FRONTEND noninteractive


RUN apt-get update \
&& apt-get install --no-install-recommends --assume-yes --allow-downgrades \
    p7zip-full \
    make \
    g++ \
    libgudhi-dev \
    libboost-dev \
    libtiff5-dev \
    python3.10-full \
&& rm -rf /var/lib/apt/lists/*


FROM setup AS build

WORKDIR /code

COPY data/topological_analysis_Arabidopsis_data data/topological_analysis_Arabidopsis_data

COPY data/topological_analysis_Cardamine_data data/topological_analysis_Cardamine_data

COPY tiff_nerve.cpp .

COPY Makefile .

COPY compute_nerves.py .

RUN if [ ! -d "nerves/" ]; then \
make && python3 compute_nerves.py \
; else echo "The folder 'nerve' already exists." && exit 1; fi

RUN rm -rf data


FROM scratch AS export

COPY --from=build /code/nerves /nerves