import numpy as np

# given a set of simplices, compute the face-vector
def facevec(simplices):
    D = 0
    for simplex in simplices:
        d = len(simplex[0]) - 1
        if d > D:
            D = d
    
    vector = np.zeros(shape=D+1, dtype=np.int64)
    for simplex in simplices:
        d = len(simplex[0]) - 1
        vector[d] += 1

    return tuple(vector)

# given a set of simplices, a dictionary of vertex labels, 
# and a list of admissible labels, 
# compute the face-vector of the subset of simplices
# whose labels are in the list of admissible labels
def facevec_subcomplex(simplices, vertex_labels, subcomplex_labels):
    
    valid_simplices = {}
    for item in simplices:
        simplex = item[0]
        checks = []
        for v in simplex:
            if v in vertex_labels:
                checks.append(vertex_labels[v] in subcomplex_labels)
            else:
                checks.append(False)
        if all(checks):
            d = len(simplex) - 1
            if d in valid_simplices:
                valid_simplices[d] += 1
            else:
                valid_simplices[d] = 1

    max_d = max(valid_simplices.keys())
    fv = [valid_simplices[i] for i in range(max_d + 1)]
    return tuple(fv)

# Given a list of labeled simplicial complexes, 
# (each of which consists of an id (str), 
# a gudhi simplex tree, 
# and a dictionary of vertex labels); 
# and given a list of admissible labels,
# compute feature vectors for all labeled simplicial complexes 
# from the face vectors of the stars of those vertices
# whose label is in the given list of admissible labels

def fv_features(labeled_simplicial_complexes, subcomplex_labels):

    unique_facevecs = set()
    facevecs_counts = {}
    simplicial_complex_ids = {}

    row = 0
    for (id, st, vertex_labels) in labeled_simplicial_complexes:

        simplicial_complex_ids[row] = id

        # compute face-vectors of vertices with label in subcomplex_labels,
        # and count how many vertices we have for each face-vector
        facevecs_counts[row] = {}
        for v in st.get_skeleton(0):
            v_label = v[0][0]
            if v_label in vertex_labels and vertex_labels[v_label] in subcomplex_labels:
                cofaces = st.get_cofaces(v[0],0)
                fv = facevec(cofaces)
                unique_facevecs.add(fv)
                if fv in facevecs_counts[row]:
                    facevecs_counts[row][fv] += 1
                else:
                    facevecs_counts[row][fv] = 1

        row += 1

    N = len(unique_facevecs)
    sorted_facevecs = sorted(list(unique_facevecs))

    features = np.zeros(shape=(row,N), dtype=np.int16)
    for j in range(row):
        for n in range(N):
            fv = sorted_facevecs[n]
            if fv in facevecs_counts[j]:
                features[j,n] = facevecs_counts[j][fv]

    normalized_features = np.zeros(shape=features.shape, dtype=np.float32)
    for i in range(features.shape[0]):
        num_cells = np.sum(features[i,:])
        for j in range(features.shape[1]):
            normalized_features[i,j] = features[i,j] / num_cells

    return normalized_features, simplicial_complex_ids, sorted_facevecs

# Given a list of labeled simplicial complexes, 
# (each of which consists of an id (str), 
# a gudhi simplex tree, 
# and a dictionary of vertex labels); 
# and given a list of admissible labels,
# compute feature vectors for all labeled simplicial complexes 
# from the face vectors of the stars of those vertices
# whose label is in the given list of admissible labels
# (with star taken in the full subcomplex of the simplicial complex
# on the vertices with admissible label)

def fv_features_subcomplex(labeled_simplicial_complexes, subcomplex_labels, facevec_labels=None):

    if facevec_labels == None:
        facevec_labels = subcomplex_labels

    unique_facevecs = set()
    facevecs_counts = {}
    simplicial_complex_ids = {}

    row = 0
    for (id, st, vertex_labels) in labeled_simplicial_complexes:

        simplicial_complex_ids[row] = id

        # compute face-vectors of vertices with label in subcomplex_labels,
        # and count how many vertices we have for each face-vector
        facevecs_counts[row] = {}
        for v in st.get_skeleton(0):
            v_label = v[0][0]
            if v_label in vertex_labels and vertex_labels[v_label] in subcomplex_labels:
                cofaces = st.get_cofaces(v[0],0)
                fv = facevec_subcomplex(cofaces, vertex_labels, facevec_labels)
                unique_facevecs.add(fv)
                if fv in facevecs_counts[row]:
                    facevecs_counts[row][fv] += 1
                else:
                    facevecs_counts[row][fv] = 1

        row += 1

    N = len(unique_facevecs)
    sorted_facevecs = sorted(list(unique_facevecs))

    features = np.zeros(shape=(row,N), dtype=np.int16)
    for j in range(row):
        for n in range(N):
            fv = sorted_facevecs[n]
            if fv in facevecs_counts[j]:
                features[j,n] = facevecs_counts[j][fv]

    normalized_features = np.zeros(shape=features.shape, dtype=np.float32)
    for i in range(features.shape[0]):
        num_cells = np.sum(features[i,:])
        for j in range(features.shape[1]):
            normalized_features[i,j] = features[i,j] / num_cells

    return normalized_features, simplicial_complex_ids, sorted_facevecs