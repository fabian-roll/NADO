# NADO: Nerve-based topological analysis of 3D digital ovules

The code in this repository accompanies the following joint work.

> Tejasvinee Atul Mody, Alexander Rolle, Nico Stucki, Fabian Roll, Ulrich Bauer, Kay Schneitz; Topological analysis of 3D digital ovules identifies cellular patterns associated with ovule shape diversity. *Development* 15 October 2024; 151 (20): dev202590. doi: https://doi.org/10.1242/dev.202590


## Usage

The topological analysis can be reproduced as follows.

1. Download the git repository and place the ovule source data in the `data/` folder as described in `data/folder_structure.txt`.
    * Arabidopsis
        *  https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BSST475
        *  https://www.ebi.ac.uk/biostudies/studies/S-BSST513
    * Cardamine
        *  https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD957
    
2. Install [Docker](https://www.docker.com/) and execute the following command inside the repository to compute the nerves associated to the TIFF files.

    ```sh
    $ docker build -f compute_nerves.Dockerfile -o . .
    ```

3. Execute the following command inside the repository to reproduce the topological analysis and save the output to the `output/` folder.

    ```sh
    $ docker build -f analysis.Dockerfile -o . .
    ```