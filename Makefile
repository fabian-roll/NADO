build: tiff_nerve

tiff_nerve: tiff_nerve.cpp
	c++ -std=c++20 -Wall tiff_nerve.cpp -o tiff_nerve -O3 -D NDEBUG -ltiff -fopenmp

clean:
	rm -f tiff_nerve
