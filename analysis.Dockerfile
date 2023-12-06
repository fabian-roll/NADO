FROM ubuntu:jammy AS setup
ENV DEBIAN_FRONTEND noninteractive


RUN apt-get update \
&& apt-get install --no-install-recommends --assume-yes --allow-downgrades \
    python3.10-full \
    python3-numpy=1:1.21.5-1ubuntu22.04.1 \
    python3-pandas=1.3.5+dfsg-3\
    python3-gudhi=3.5.0+dfsg-1ubuntu2\
    python3-sklearn=0.23.2-5ubuntu6\
    python3-matplotlib=3.5.1-2build1\
    python3-openpyxl=3.0.9-1 \
    r-base=4.1.2-1ubuntu2 \
&& rm -rf /var/lib/apt/lists/*

RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/cramer/cramer_0.9-1.tar.gz", repos=NULL, type="source")'


FROM setup AS build

WORKDIR /code

COPY data/topological_analysis_Arabidopsis_data data/topological_analysis_Arabidopsis_data

COPY data/topological_analysis_Cardamine_data data/topological_analysis_Cardamine_data

COPY data/*.xlsx data/

COPY nerves nerves

COPY fvec_features.py .

COPY compute_feature_vectors_json_creation.py .

COPY compute_feature_vectors.py .

COPY apply_cramer_test.r .

COPY visualize_feature_vectors.py .

RUN python3 compute_feature_vectors_json_creation.py

RUN python3 compute_feature_vectors.py

RUN Rscript apply_cramer_test.r

RUN python3 visualize_feature_vectors.py

RUN rm -rf data/ nerves/


FROM scratch AS export

COPY --from=build /code/features /output/features

COPY --from=build /code/scatter_visualizations /output/scatter_visualizations

COPY --from=build /code/cramer_results.txt /output/cramer_results.txt