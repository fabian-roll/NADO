library(cramer, help, pos = 2, lib.loc = NULL)

species_options <- list("Arabidopsis", "Cardamine")
growth_stages <- list("1-I", "1-II", "2-I", "2-II")
feature_vector_ids <- list("L1_no-gaps_subcomplex", "L2_no-gaps_subcomplex", "L3_no-gaps_subcomplex", "all-cells_no-gaps_subcomplex")
tissue_names <- list("L1", "L2", "L3", "whole ovule")

# file information
path <- "features/"
fv_id_end <- "_features.csv"

file.create("cramer_results_primordia.txt")
write("Baringhaus-Franz multivariate two-sample test p values", file = "cramer_results_primordia.txt", append = TRUE)

i <- 1
for (fv_id in feature_vector_ids) {

  tissue_name <- tissue_names[[i]]
  write(fv_id, file = "cramer_results_primordia.txt", append = TRUE)
  i <- i + 1

  for (growth_stage in growth_stages) {
    if (!(tissue_name == "L3" & growth_stage == "1-I")) {
      write(growth_stage, file = "cramer_results_primordia.txt", append = TRUE)

      # load Arabidopsis features
      file_name_x <- paste(path, fv_id, "_Arabidopsis_", growth_stage, fv_id_end, sep = "")
      x <- read.csv(file_name_x, header = FALSE)
      x <- as.matrix(x)

      # load Cardamine features
      file_name_y <- paste(path, fv_id, "_Cardamine_", growth_stage, fv_id_end, sep = "")
      y <- read.csv(file_name_y, header = FALSE)
      y <- as.matrix(y)

      # apply Cramer test
      t <- cramer.test(x, y, sim = "ordinary", replicates = 100000)

      # print the estimated p value
      p <- t$p.value
      write(as.character(p), file = "cramer_results_primordia.txt", append = TRUE)

    }

  }

}