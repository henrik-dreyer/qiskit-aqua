# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

""" Test Docplex """

from math import fsum, isclose
from test.aqua.common import QiskitAquaTestCase

import networkx as nx
import numpy as np
from docplex.mp.model import Model
from qiskit.quantum_info import Pauli

from qiskit.aqua import AquaError, aqua_globals
from qiskit.aqua.algorithms import ExactEigensolver
from qiskit.aqua.translators.ising import tsp, docplex
from qiskit.aqua.operators import WeightedPauliOperator

# Reference operators and offsets for maxcut and tsp.
QUBIT_OP_MAXCUT = WeightedPauliOperator(
    paulis=[[0.5, Pauli(z=[True, True, False, False], x=[False, False, False, False])],
            [0.5, Pauli(z=[True, False, True, False], x=[False, False, False, False])],
            [0.5, Pauli(z=[False, True, True, False], x=[False, False, False, False])],
            [0.5, Pauli(z=[True, False, False, True], x=[False, False, False, False])],
            [0.5, Pauli(z=[False, False, True, True], x=[False, False, False, False])]])
OFFSET_MAXCUT = -2.5
QUBIT_OP_TSP = WeightedPauliOperator(
    paulis=[[-100057.0, Pauli(z=[True, False, False, False, False, False, False, False, False],
                              x=[False, False, False, False, False, False, False, False, False])],
            [-100071.0, Pauli(z=[False, False, False, False, True, False, False, False, False],
                              x=[False, False, False, False, False, False, False, False, False])],
            [14.5, Pauli(z=[True, False, False, False, True, False, False, False, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [-100057.0, Pauli(z=[False, True, False, False, False, False, False, False, False],
                              x=[False, False, False, False, False, False, False, False, False])],
            [-100071.0, Pauli(z=[False, False, False, False, False, True, False, False, False],
                              x=[False, False, False, False, False, False, False, False, False])],
            [14.5, Pauli(z=[False, True, False, False, False, True, False, False, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [-100057.0, Pauli(z=[False, False, True, False, False, False, False, False, False],
                              x=[False, False, False, False, False, False, False, False, False])],
            [-100071.0, Pauli(z=[False, False, False, True, False, False, False, False, False],
                              x=[False, False, False, False, False, False, False, False, False])],
            [14.5, Pauli(z=[False, False, True, True, False, False, False, False, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [-100070.0, Pauli(z=[False, False, False, False, False, False, False, True, False],
                              x=[False, False, False, False, False, False, False, False, False])],
            [14.0, Pauli(z=[True, False, False, False, False, False, False, True, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [-100070.0, Pauli(z=[False, False, False, False, False, False, False, False, True],
                              x=[False, False, False, False, False, False, False, False, False])],
            [14.0, Pauli(z=[False, True, False, False, False, False, False, False, True],
                         x=[False, False, False, False, False, False, False, False, False])],
            [-100070.0, Pauli(z=[False, False, False, False, False, False, True, False, False],
                              x=[False, False, False, False, False, False, False, False, False])],
            [14.0, Pauli(z=[False, False, True, False, False, False, True, False, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [14.5, Pauli(z=[False, True, False, True, False, False, False, False, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [14.5, Pauli(z=[False, False, True, False, True, False, False, False, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [14.5, Pauli(z=[True, False, False, False, False, True, False, False, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [21.0, Pauli(z=[False, False, False, True, False, False, False, True, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [21.0, Pauli(z=[False, False, False, False, True, False, False, False, True],
                         x=[False, False, False, False, False, False, False, False, False])],
            [21.0, Pauli(z=[False, False, False, False, False, True, True, False, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [14.0, Pauli(z=[False, True, False, False, False, False, True, False, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [14.0, Pauli(z=[False, False, True, False, False, False, False, True, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [14.0, Pauli(z=[True, False, False, False, False, False, False, False, True],
                         x=[False, False, False, False, False, False, False, False, False])],
            [21.0, Pauli(z=[False, False, False, False, True, False, True, False, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [21.0, Pauli(z=[False, False, False, False, False, True, False, True, False],
                         x=[False, False, False, False, False, False, False, False, False])],
            [21.0, Pauli(z=[False, False, False, True, False, False, False, False, True],
                         x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[True, False, False, True, False, False, False, False, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[True, False, False, False, False, False, True, False, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, False, False, True, False, False, True, False, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, True, False, False, True, False, False, False, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, True, False, False, False, False, False, True, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, False, False, False, True, False, False, True, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, False, True, False, False, True, False, False, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, False, True, False, False, False, False, False, True],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, False, False, False, False, True, False, False, True],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[True, True, False, False, False, False, False, False, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[True, False, True, False, False, False, False, False, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, True, True, False, False, False, False, False, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, False, False, True, True, False, False, False, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, False, False, True, False, True, False, False, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, False, False, False, True, True, False, False, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, False, False, False, False, False, True, True, False],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, False, False, False, False, False, True, False, True],
                            x=[False, False, False, False, False, False, False, False, False])],
            [50000.0, Pauli(z=[False, False, False, False, False, False, False, True, True],
                            x=[False, False, False, False, False, False, False, False, False])]])
OFFSET_TSP = 600297.0


class TestDocplex(QiskitAquaTestCase):
    """Cplex Ising tests."""

    def setUp(self):
        super().setUp()
        aqua_globals.random_seed = 100

    def test_validation(self):
        """ Validation Test """
        num_var = 3
        # validate an object type of the input.
        with self.assertRaises(AquaError):
            docplex._validate_input_model("Model")

        # validate the types of the variables are binary or not
        with self.assertRaises(AquaError):
            mdl = Model(name='Error_integer_variables')
            x = {i: mdl.integer_var(name='x_{0}'.format(i)) for i in range(num_var)}
            obj_func = mdl.sum(x[i] for i in range(num_var))
            mdl.maximize(obj_func)
            docplex.get_qubit_op(mdl)

        # validate types of constraints are equality constraints or not.
        with self.assertRaises(AquaError):
            mdl = Model(name='Error_inequality_constraints')
            x = {i: mdl.binary_var(name='x_{0}'.format(i)) for i in range(num_var)}
            obj_func = mdl.sum(x[i] for i in range(num_var))
            mdl.maximize(obj_func)
            mdl.add_constraint(mdl.sum(x[i] for i in range(num_var)) <= 1)
            docplex.get_qubit_op(mdl)

    def test_auto_define_penalty(self):
        """ Auto define Penalty test """
        # check _auto_define_penalty() for positive coefficients.
        positive_coefficients = aqua_globals.random.rand(10, 10)
        for i in range(10):
            mdl = Model(name='Positive_auto_define_penalty')
            x = {j: mdl.binary_var(name='x_{0}'.format(j)) for j in range(10)}
            obj_func = mdl.sum(positive_coefficients[i][j] * x[j] for j in range(10))
            mdl.maximize(obj_func)
            actual = docplex._auto_define_penalty(mdl)
            expected = fsum(abs(j) for j in positive_coefficients[i]) + 1
            self.assertEqual(isclose(actual, expected), True)

        # check _auto_define_penalty() for negative coefficients
        negative_coefficients = -1 * aqua_globals.random.rand(10, 10)
        for i in range(10):
            mdl = Model(name='Negative_auto_define_penalty')
            x = {j: mdl.binary_var(name='x_{0}'.format(j)) for j in range(10)}
            obj_func = mdl.sum(negative_coefficients[i][j] * x[j] for j in range(10))
            mdl.maximize(obj_func)
            actual = docplex._auto_define_penalty(mdl)
            expected = fsum(abs(j) for j in negative_coefficients[i]) + 1
            self.assertEqual(isclose(actual, expected), True)

        # check _auto_define_penalty() for mixed coefficients
        mixed_coefficients = aqua_globals.random.randint(-100, 100, (10, 10))
        for i in range(10):
            mdl = Model(name='Mixed_auto_define_penalty')
            x = {j: mdl.binary_var(name='x_{0}'.format(j)) for j in range(10)}
            obj_func = mdl.sum(mixed_coefficients[i][j] * x[j] for j in range(10))
            mdl.maximize(obj_func)
            actual = docplex._auto_define_penalty(mdl)
            expected = fsum(abs(j) for j in mixed_coefficients[i]) + 1
            self.assertEqual(isclose(actual, expected), True)

        # check that 1e5 is being used when coefficients have float numbers.
        float_coefficients = [0.1 * i for i in range(3)]
        mdl = Model(name='Float_auto_define_penalty')
        x = {i: mdl.binary_var(name='x_{0}'.format(i)) for i in range(3)}
        obj_func = mdl.sum(x[i] for i in range(3))
        mdl.maximize(obj_func)
        mdl.add_constraint(mdl.sum(float_coefficients[i] * x[i] for i in range(3)) == 1)
        actual = docplex._auto_define_penalty(mdl)
        expected = 1e5
        self.assertEqual(actual, expected)

    def test_docplex_maxcut(self):
        """ Docplex maxcut test """
        # Generating a graph of 4 nodes
        n = 4
        graph = nx.Graph()
        graph.add_nodes_from(np.arange(0, n, 1))
        elist = [(0, 1, 1.0), (0, 2, 1.0), (0, 3, 1.0), (1, 2, 1.0), (2, 3, 1.0)]
        graph.add_weighted_edges_from(elist)
        # Computing the weight matrix from the random graph
        w = np.zeros([n, n])
        for i in range(n):
            for j in range(n):
                temp = graph.get_edge_data(i, j, default=0)
                if temp != 0:
                    w[i, j] = temp['weight']

        # Create an Ising Hamiltonian with docplex.
        mdl = Model(name='max_cut')
        mdl.node_vars = mdl.binary_var_list(list(range(4)), name='node')
        maxcut_func = mdl.sum(w[i, j] * mdl.node_vars[i] * (1 - mdl.node_vars[j])
                              for i in range(n) for j in range(n))
        mdl.maximize(maxcut_func)
        qubit_op, offset = docplex.get_qubit_op(mdl)

        e_e = ExactEigensolver(qubit_op, k=1)
        result = e_e.run()

        ee_expected = ExactEigensolver(QUBIT_OP_MAXCUT, k=1)
        expected_result = ee_expected.run()

        # Compare objective
        self.assertEqual(result['energy'] + offset, expected_result['energy'] + OFFSET_MAXCUT)

    def test_docplex_tsp(self):
        """ Docplex tsp test """
        # Generating a graph of 3 nodes
        n = 3
        ins = tsp.random_tsp(n)
        graph = nx.Graph()
        graph.add_nodes_from(np.arange(0, n, 1))
        num_node = ins.dim

        # Create an Ising Hamiltonian with docplex.
        mdl = Model(name='tsp')
        x = {(i, p): mdl.binary_var(name='x_{0}_{1}'.format(i, p))
             for i in range(num_node) for p in range(num_node)}
        tsp_func = mdl.sum(
            ins.w[i, j] * x[(i, p)] * x[(j, (p + 1) % num_node)]
            for i in range(num_node) for j in range(num_node) for p
            in range(num_node))
        mdl.minimize(tsp_func)
        for i in range(num_node):
            mdl.add_constraint(mdl.sum(x[(i, p)] for p in range(num_node)) == 1)
        for j in range(num_node):
            mdl.add_constraint(mdl.sum(x[(i, j)] for i in range(num_node)) == 1)
        qubit_op, offset = docplex.get_qubitops(mdl)

        e_e = ExactEigensolver(qubit_op, k=1)
        result = e_e.run()

        ee_expected = ExactEigensolver(QUBIT_OP_TSP, k=1)
        expected_result = ee_expected.run()

        # Compare objective
        self.assertEqual(result['energy'] + offset, expected_result['energy'] + OFFSET_TSP)

    def test_docplex_integer_constraints(self):
        """ Docplex Integer Constraints test """
        # Create an Ising Hamiltonian with docplex
        mdl = Model(name='integer_constraints')
        x = {i: mdl.binary_var(name='x_{0}'.format(i)) for i in range(1, 5)}
        max_vars_func = mdl.sum(x[i] for i in range(1, 5))
        mdl.maximize(max_vars_func)
        mdl.add_constraint(mdl.sum(i * x[i] for i in range(1, 5)) == 3)
        qubit_op, offset = docplex.get_qubit_op(mdl)

        e_e = ExactEigensolver(qubit_op, k=1)
        result = e_e.run()

        expected_result = -2

        # Compare objective
        self.assertEqual(result['energy'] + offset, expected_result)

    def test_docplex_constant_and_quadratic_terms_in_object_function(self):
        """ Docplex Constant and Quadratic terms in Object function test """
        # Create an Ising Hamiltonian with docplex
        laplacian = np.array([[-3., 1., 1., 1.],
                              [1., -2., 1., -0.],
                              [1., 1., -3., 1.],
                              [1., -0., 1., -2.]])

        mdl = Model()
        # pylint: disable=unsubscriptable-object
        n = laplacian.shape[0]
        bias = [0] * 4
        x = {i: mdl.binary_var(name='x_{0}'.format(i)) for i in range(n)}
        couplers_func = mdl.sum(
            2 * laplacian[i, j] * (2 * x[i] - 1) * (2 * x[j] - 1)
            for i in range(n - 1) for j in range(i, n))
        bias_func = mdl.sum(float(bias[i]) * x[i] for i in range(n))
        ising_func = couplers_func + bias_func
        mdl.minimize(ising_func)
        qubit_op, offset = docplex.get_qubit_op(mdl)

        e_e = ExactEigensolver(qubit_op, k=1)
        result = e_e.run()

        expected_result = -22

        # Compare objective
        self.assertEqual(result['energy'] + offset, expected_result)
