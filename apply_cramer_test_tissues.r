library(cramer, help, pos = 2, lib.loc = NULL)

species_options <- list("Arabidopsis", "Cardamine")
growth_stages <- list("2-III", "2-IV", "2-V", "3-I", "3-II", "3-III", "3-IV", "3-V", "3-VI")

# file information
path <- "features/comparing_tissues/"
fv_id_end <- "_features.csv"

# print results to a file
file.create("cramer_results_tissues.txt")
write("Baringhaus-Franz multivariate two-sample test p values", file = "cramer_results_tissues.txt", append = TRUE)

#############################
# chalaza vs outer integument
#############################

write("chalaza vs outer integument", file = "cramer_results_tissues.txt", append = TRUE)

ch_fv_id <- "ch_no-gaps_subcomplex_"
oi_fv_id <- "oi_no-gaps_subcomplex_"

for (species in species_options) {
  write(species, file = "cramer_results_tissues.txt", append = TRUE)
  for (growth_stage in growth_stages) {
    write(growth_stage, file = "cramer_results_tissues.txt", append = TRUE)

    # load chalaza features
    file_name_x <- paste(path, ch_fv_id, species, "_", growth_stage, fv_id_end, sep = "")
    x <- read.csv(file_name_x, header = FALSE)
    x <- as.matrix(x)

    # load outer integument features
    file_name_y <- paste(path, oi_fv_id, species, "_", growth_stage, fv_id_end, sep = "")
    y <- read.csv(file_name_y, header = FALSE)
    y <- as.matrix(y)

    # apply Cramer test
    t <- cramer.test(x, y, sim = "ordinary", replicates = 10000)

    # print the estimated p value
    p <- t$p.value
    write(p, file = "cramer_results_tissues.txt", append = TRUE)

  }
}