P = OrientedGraphProblem(4, type_orders=[2], density="4:121314")
x = polygen(QQ)
K = NumberField(x^3+x^2+x-1/3, 'x', embedding=0.253)
x=K.gen()
P.set_extremal_construction(field=K, target_bound=1 - 9 * x^2)
P.add_zero_eigenvectors(0, matrix(K, [[1 - x, 0, 0, 0, 0, 0, 0, 0, x], [x * (1 - x), 0, 0, 0, 0, 1-x, 0, 0, x^2]]))
P.add_zero_eigenvectors(1, matrix(K, [[0, 1 - x, 0, 0, 0, 0, 0, 0, x], [0, 0, 0, 0, 1, 0, 0, 0, -1], [0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0, -1]]))
P.add_sharp_graphs(0, 5, 8, 24, 27, 31, 37, 38)
P.solve_sdp()
P.make_exact()