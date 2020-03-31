import numpy as np
import math
import random as rand


# https://stackoverflow.com/a/6802723
def rotation_matrix(axis: (int, int, int), theta: int):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def rotate(axis, theta, x):
    return np.dot(rotation_matrix(axis, theta), x)


def accuracy_vectors(vector, deviations, vectors_per_deviation) -> [[(int, int, int), int]]:
    vector = vector / np.linalg.norm(vector)
    orthogonal = np.cross(vector, [1, 0, 0] if np.array_equal(vector, [1, 0, 0]) else [0, 0, 1])
    to_return = []
    for deviation in deviations:
        vectors = []
        assert (deviation < 90)
        # All vectors will have a magnitude of 1 and start at origin
        # They will differ only by the size of the cone they represent
        radius = math.tan(deviation / 90 * math.pi / 2)
        for i in range(0, vectors_per_deviation):
            vectors.append(rotate(vector, 2 * math.pi * i / vectors_per_deviation, orthogonal)
                           * radius + vector)
        to_return.append((vectors, deviation))
    return to_return


# TODO alright, we got the accuracy vectors, now time to turn them into pyramids, then do it for real

def to_pyramids(pyramid_vectors: [[(int, int, int)], int], offset, vectors_per_deviation) -> str:
    to_return = ""
    i = 0
    if i == 0:
        to_return += "v 0 0 0\n"
    for pyramid, deviation in pyramid_vectors:
        for vector in pyramid:
            to_return += "v {} {} {}\n".format(vector[0], vector[1], vector[2])
        to_return += "\n"
        to_return += "usemtl deviation{}\n".format(deviation)
        for i2 in range(0, len(pyramid)):
            n = offset + i*len(pyramid)+i2+offset+2
            to_return += "f {} {} {}\n".format(1, n, n+1 if i2 != len(pyramid)-1 else offset + i*len(pyramid)+2)
        to_return += "\n\n"
        i += 1
    return to_return


accuracy = accuracy_vectors([1, 2, 3], [30, 45, 55], 4)
print(accuracy)
print(to_pyramids(accuracy, 0, 4))
