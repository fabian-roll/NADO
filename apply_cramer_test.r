library(cramer, help, pos = 2, lib.loc = NULL)

species_options <- list("Arabidopsis", "Cardamine")
growth_stages <- list("2-III", "2-IV", "2-V", "3-I", "3-II", "3-III", "3-IV", "3-V", "3-VI")
feature_vector_ids <- list("ch_no-gaps_subcomplex", "oi_no-gaps_subcomplex", "ii_no-gaps_subcomplex", "fu_no-gaps_subcomplex", "nu_no-gaps_subcomplex", "all-cells_no-gaps_full-nerve")
tissue_names <- list("chalaza", "outer integument", "inner integument", "funiculus", "nucellus", "whole ovule")

# file information
path <- "features/"
fv_id_end <- "_features.csv"

file.create("cramer_results.txt")
write("Baringhaus-Franz multivariate two-sample test p values", file = "cramer_results.txt", append = TRUE)

i <- 1
for (fv_id in feature_vector_ids) {

  tissue_name <- tissue_names[[i]]
  write(tissue_name, file = "cramer_results.txt", append = TRUE)
  i <- i + 1

  for (growth_stage in growth_stages) {
    write(growth_stage, file = "cramer_results.txt", append = TRUE)

    # load Arabidopsis features
    file_name_x <- paste(path, fv_id, "_Arabidopsis_", growth_stage, fv_id_end, sep = "")
    x <- read.csv(file_name_x, header = FALSE)
    x <- as.matrix(x)

    # load Cardamine features
    file_name_y <- paste(path, fv_id, "_Cardamine_", growth_stage, fv_id_end, sep = "")
    y <- read.csv(file_name_y, header = FALSE)
    y <- as.matrix(y)

    # apply Cramer test
    t <- cramer.test(x, y, sim = "ordinary", replicates = 10000)

    # print the estimated p value
    p <- t$p.value
    write(as.character(p), file = "cramer_results.txt", append = TRUE)

  }

}