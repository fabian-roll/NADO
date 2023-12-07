# NADO: Nerve-based topological analysis of 3D digital ovules

The code in this repository accompanies the following joint work.

> Mody, T. A., Rolle, A., Stucki, N., Roll, F., Bauer, U. and Schneitz, K. (2023).
> Diverse 3D cellular patterns underlie the development of Cardamine hirsuta and Arabidopsis thaliana ovules.
> bioRxiv doi: [10.1101/2023.12.06.570408](https://doi.org/10.1101/2023.12.06.570408).


## Usage

The topological analysis can be reproduced as follows.

1. Download the git repository and place the ovule source data in the `data/` folder as described in `data/folder_structure.txt`.
    * Arabidopsis
        *  https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BSST475
        *  https://www.ebi.ac.uk/biostudies/studies/S-BSST513
    * Cardamine (currently not public)
        *  https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD957
    
2. Install [Docker](https://www.docker.com/) and execute the following command inside the repository to compute the nerves associated to the TIFF files.

    ```sh
    $ docker build -f compute_nerves.Dockerfile -o . .
    ```

3. Execute the following command inside the repository to reproduce the topological analysis and save the output to the `output/` folder.

    ```sh
    $ docker build -f analysis.Dockerfile -o . .
    ```