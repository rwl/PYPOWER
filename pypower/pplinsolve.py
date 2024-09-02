import pyrlu

from numpy import asfortranarray
from scipy.sparse import csc_matrix, csr_matrix


def pplinsolve(A, b):
    """Solves the linear system of equations C{A * x = b}.
    """
    x = asfortranarray(b.copy())

    if isinstance(A, csc_matrix):
        trans = False
    elif isinstance(A, csr_matrix):
        trans = True
    else:
        raise Exception("matrix A must be CSC or CSR:", type(A))

    m, n = A.shape

    A.sort_indices()
    A.sum_duplicates()

    pyrlu.factor_solve(n, A.indices, A.indptr, A.data, x, trans=trans, par=False)

    return x
