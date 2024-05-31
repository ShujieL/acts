import numpy as np

import sympy as sym
from sympy import MatrixSymbol

from sympy_common import name_expr, find_by_name, cxx_printer, my_expression_print


C = MatrixSymbol("C", 6, 6).as_explicit().as_mutable()
for indices in np.ndindex(C.shape):
    C[indices] = C[tuple(sorted(indices))]

J_full = MatrixSymbol("J_full", 6, 6).as_explicit().as_mutable()
tmp = sym.eye(6)
tmp[0:4, 0:5] = J_full[0:4, 0:5]
tmp[5:6, 0:5] = J_full[5:6, 0:5]
J_full = tmp


def covariance_transport_generic():
    new_C = name_expr("new_C", J_full * C * J_full.T)

    return [new_C]


def my_covariance_transport_generic_function_print(name_exprs, run_cse=True):
    printer = cxx_printer
    outputs = [find_by_name(name_exprs, name)[0] for name in ["new_C"]]

    lines = []

    head = "template <typename T> void transportCovarianceToBoundImpl(const T* C, const T* J_full, T* new_C) {"
    lines.append(head)

    code = my_expression_print(
        printer,
        name_exprs,
        outputs,
        run_cse=run_cse,
    )
    lines.extend([f"  {l}" for l in code.split("\n")])

    lines.append("}")

    return "\n".join(lines)


print(
    """// This file is part of the Acts project.
//
// Copyright (C) 2024 CERN for the benefit of the Acts project
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

// Note: This file is generated by generate_sympy_cov.py
//       Do not modify it manually.

#pragma once

#include <cmath>
"""
)

all_name_exprs = covariance_transport_generic()
code = my_covariance_transport_generic_function_print(
    all_name_exprs,
    run_cse=True,
)
print(code)