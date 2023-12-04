FROM ubuntu:jammy AS setup
ENV DEBIAN_FRONTEND noninteractive


RUN apt-get update \
&& apt-get install --no-install-recommends --assume-yes --allow-downgrades \
    p7zip-full=16.02+dfsg-8 \
    make=4.3-4.1build1 \
    g++=4:11.2.0-1ubuntu1 \
    libgudhi-dev=3.5.0+dfsg-1ubuntu2 \
    libboost-dev=1.74.0.3ubuntu7 \
    libtiff5-dev=4.3.0-6ubuntu0.7 \
    python3.10-full \
&& rm -rf /var/lib/apt/lists/*


FROM setup AS build

WORKDIR /code

COPY ["data/Arabidopsis/Arabidopsis segmentations", "data/Arabidopsis/Arabidopsis segmentations"]

COPY ["data/Cardamine/Cardamine segmentations", "data/Cardamine/Cardamine segmentations"]

COPY tiff_nerve.cpp .

COPY Makefile .

COPY compute_nerves.py .

RUN if [ ! -d "nerves/" ]; then \
make && python3 compute_nerves.py \
; else echo "The folder 'nerve' already exists." && exit 1; fi

RUN rm -rf data


FROM scratch AS export

COPY --from=build /code/nerves /nerves