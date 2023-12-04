/*

MIT License

Copyright (c) 2023 Fabian Roll

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

*/

#define INDICATE_PROGRESS
#define MULTITHREAD

#include <chrono>
#include <gudhi/Simplex_tree.h>
#include <iostream>
#include <mutex>
#include <tiffio.h>

#ifdef INDICATE_PROGRESS
static const std::chrono::milliseconds time_step(40);
static const std::string clear_line("\r\033[K");
#endif

using Simplex_tree = Gudhi::Simplex_tree<>;
using Vertex_handle = Simplex_tree::Vertex_handle;
using Filtration_value = Simplex_tree::Filtration_value;
using typeVectorVertex = std::vector<Vertex_handle>;
using typePairSimplexBool = std::pair<Simplex_tree::Simplex_handle, bool>;

#ifdef MULTITHREAD
std::mutex m;
#endif

void insert_simplex_from_voxels(Simplex_tree *simplexTree, uint16_t i,
                                uint16_t j, uint32_t width,
                                uint16_t *imageData_one,
                                uint16_t *imageData_two) {
  std::set<uint16_t> SimplexVector;
  SimplexVector.insert(imageData_one[i * width + j]);
  SimplexVector.insert(imageData_one[i * width + j + 1]);
  SimplexVector.insert(imageData_one[(i + 1) * width + j]);
  SimplexVector.insert(imageData_one[(i + 1) * width + j + 1]);
  SimplexVector.insert(imageData_two[i * width + j]);
  SimplexVector.insert(imageData_two[i * width + j + 1]);
  SimplexVector.insert(imageData_two[(i + 1) * width + j]);
  SimplexVector.insert(imageData_two[(i + 1) * width + j + 1]);

  if (SimplexVector.size() != 1) {
#ifdef MULTITHREAD
    std::unique_lock<std::mutex> lk(m);
#endif

    (*simplexTree)
        .insert_simplex_and_subfaces(SimplexVector, Filtration_value(0));

#ifdef MULTITHREAD
    lk.unlock();
#endif
  }
}

Simplex_tree compute_nerve(const char *filename) {

  TIFF *image;
  uint32_t width, height, imagesize;
  uint16_t numpages;

  // Open the TIFF image
  if ((image = TIFFOpen(filename, "r")) == NULL) {
    fprintf(stderr, "Could not open TIFF file\n");
    exit(42);
  }

  // Get the number of pages (layers) in the TIFF file
  numpages = TIFFNumberOfDirectories(image);

  // Find the width and height of the image
  TIFFGetField(image, TIFFTAG_IMAGEWIDTH, &width);
  TIFFGetField(image, TIFFTAG_IMAGELENGTH, &height);
  imagesize = height * width;

  std::cerr << std::endl << "Image width: " << width << std::endl;
  std::cerr << "Image height: " << height << std::endl;
  std::cerr << "Number of pages: " << numpages << std::endl << std::endl;

  uint32_t stripCount = TIFFNumberOfStrips(image);
  uint32_t rowsPerStrip;
  TIFFGetField(image, TIFFTAG_ROWSPERSTRIP, &rowsPerStrip);

  Simplex_tree simplexTree;

  if (numpages == 1) {
    uint16_t *imageData_one = new uint16_t[imagesize];

    // Set the current page
    TIFFSetDirectory(image, 0);

    uint32_t row = 0;
    for (uint32_t strip = 0; strip < stripCount; strip++) {
      uint32_t stripHeight =
          (row + rowsPerStrip > height) ? height - row : rowsPerStrip;
      TIFFReadEncodedStrip(image, strip, &imageData_one[row * width],
                           stripHeight * width * sizeof(uint16_t));
      row += stripHeight;
    }

    // Iterate over the pixels
    for (uint32_t i = 0; i < (height - 1); i++) {
      for (uint32_t j = 0; j < (width - 1); j++) {

        std::set<uint16_t> SimplexVector;
        SimplexVector.insert(imageData_one[i * width + j]);
        SimplexVector.insert(imageData_one[i * width + j + 1]);
        SimplexVector.insert(imageData_one[(i + 1) * width + j]);
        SimplexVector.insert(imageData_one[(i + 1) * width + j + 1]);

        if (SimplexVector.size() != 1) {
          (simplexTree)
              .insert_simplex_and_subfaces(SimplexVector, Filtration_value(0));
        }
      }
    }
    delete[] imageData_one; // free allocated memory
  } else {

#ifdef INDICATE_PROGRESS
    std::cerr << clear_line << "processing page" << std::flush;
    std::chrono::steady_clock::time_point next =
        std::chrono::steady_clock::now() + time_step;
#endif

    uint16_t *imageData_one = new uint16_t[imagesize];
    uint16_t *imageData_two = new uint16_t[imagesize];

    TIFFSetDirectory(image, 0);
    uint32_t row = 0;
    for (uint32_t strip = 0; strip < stripCount; strip++) {
      uint32_t stripHeight =
          (row + rowsPerStrip > height) ? height - row : rowsPerStrip;
      TIFFReadEncodedStrip(image, strip, &imageData_one[row * width],
                           stripHeight * width * sizeof(uint16_t));
      row += stripHeight;
    }

    // Loop over each page
    for (uint16_t k = 0; k < numpages - 1; k++) {

#ifdef INDICATE_PROGRESS
      if (std::chrono::steady_clock::now() > next) {
        std::cerr << clear_line << "processing pages " << k + 1 << "," << k + 2
                  << " / " << numpages << std::flush;
        next = std::chrono::steady_clock::now() + time_step;
      }
#endif
      // Set the current page
      TIFFSetDirectory(image, k + 1);

      uint32_t row = 0;
      for (uint32_t strip = 0; strip < stripCount; strip++) {
        uint32_t stripHeight =
            (row + rowsPerStrip > height) ? height - row : rowsPerStrip;
        TIFFReadEncodedStrip(image, strip, &imageData_two[row * width],
                             stripHeight * width * sizeof(uint16_t));
        row += stripHeight;
      }

#ifdef MULTITHREAD
      #pragma omp parallel for collapse(2)
#endif
      // Iterate over the pixels
      for (uint32_t i = 0; i < (height - 1); i++) {
        for (uint32_t j = 0; j < (width - 1); j++) {
          insert_simplex_from_voxels(&simplexTree, i, j, width, imageData_one,
                                     imageData_two);
        }
      }
      uint16_t *tmp = &*imageData_one;
      imageData_one = imageData_two;
      imageData_two = tmp;
    }
    delete[] imageData_one; // free allocated memory
    delete[] imageData_two; // free allocated memory
  }

  TIFFClose(image);
  return simplexTree;
}

int main(int argc, char **argv) {

  const char *filename = argv[1];

  Simplex_tree simplexTree = compute_nerve(filename);

  std::clog << std::endl;
  std::clog << std::endl;
  for (auto &simplex : simplexTree.complex_simplex_range()) {
    bool first_vertex = true;
    for (auto vertex : simplexTree.simplex_vertex_range(simplex)) {
      if (first_vertex == false) {
        std::cout << "," << vertex;
      } else {
        std::cout << vertex;
        first_vertex = false;
      }
    }
    std::cout << std::endl;
  }

  std::clog << std::endl
            << std::endl
            << "Information of the Simplex Tree: " << std::endl;
  std::clog << "  Number of vertices = " << simplexTree.num_vertices()
            << std::endl;
  std::clog << "  Number of simplices = " << simplexTree.num_simplices()
            << std::endl
            << std::endl;

  return 0;
}