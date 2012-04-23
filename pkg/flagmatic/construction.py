"""

flagmatic 2

Copyright (c) 2012, E. R. Vaughan. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1) Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2) Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

import sys

from sage.structure.sage_object import SageObject       
from sage.rings.arith import factorial
from sage.combinat.all import UnorderedTuples, Tuples, Combinations, Permutations, Compositions, Subsets
from sage.rings.all import Integer, QQ, polygen, RationalField
from sage.matrix.all import matrix, identity_matrix
from sage.misc.all import sage_eval
from sage.interfaces.gap import gap

from three_graph_flag import *
from graph_flag import *
from oriented_graph_flag import *


class Construction(SageObject):

	def __init__(self):
		self._field = RationalField()

	@property
	def field(self):
		return self._field

	def subgraph_densities(self, n):
		return None

	def target_bound(self):
		return None

	def zero_eigenvectors(self, tg, flags, flag_basis=None):
		return None


class AdHocConstruction(Construction):

	def __init__(self, name):

		self._name = name

		if name == "maxs3":
	
			self._field_str = "NumberField(x^2+x-1/2, 'x', embedding=0.5)"
	
		elif name == "maxs4":

			self._field_str = "NumberField(x^3+x^2+x-1/3, 'x', embedding=0.5)"

		elif name == "maxs5":

			self._field_str = "NumberField(x^4+x^3+x^2+x-1/4, 'x', embedding=0.5)"

		else:
		
			self._field_str = "RationalField()"
		
		x = polygen(QQ)
		self._field = sage_eval(self._field_str, locals={'x': x})


	@property
	def field(self):
		return self._field
	

	def target_bound(self):

		K = self._field
		x = K.gen()

		if self._name == "maxs3":

			return (4 * x - 1, [0, 2, 4, 5])

		elif self._name == "maxs4":
		
			return (1 - 9 * x**2, [0, 5, 8, 24, 27, 31, 37, 38])

		elif self._name == "max42":

			return (Integer(3)/4, [0, 4, 8, 23, 24, 27, 33])


	def zero_eigenvectors(self, tg, flags):
	
		x = self._field.gen()
		rows = []

		# TODO: should check flags are in the right order!
		
		if self._name == "maxs3":

			if tg == OrientedGraphFlag("1:"):
		
				rows = [
					[1 - x,       0,     x],
					[x * (1 - x), 1 - x, x**2]
				]
	
		elif self._name == "maxs4":

			if tg == OrientedGraphFlag("2:"):
		
				rows = [
					[1 - x,       0, 0, 0, 0, 0,   0, 0, x],
					[x * (1 - x), 0, 0, 0, 0, 1-x, 0, 0, x**2]
				]
				
			elif tg == OrientedGraphFlag("2:12"):

				rows = [
					[0, 1 - x, 0, 0, 0, 0, 0, 0, x],
					[0, 0,     0, 0, 1, 0, 0, 0, -1],
					[0, 0,     0, 0, 0, 1, 0, 0, 0],
					[0, 0,     0, 0, 0, 0, 1, 0, -1]
				]

		elif self._name == "max42":

			if tg == ThreeGraphFlag("3:"):

				rows = [[1, 0, 0, 0, 1, 1, 1, 0]]
			
			elif tg == ThreeGraphFlag("3:123"):

				rows = [[0, 1, 1, 1, 0, 0, 0, 1]]

		M = matrix(self._field, list(rows), sparse=True)
		M = M.echelon_form()
		M = M[:M.rank(),:]
		
		if M.rank() == 0:
			return matrix(self._field, 0, len(flags), sparse=True)
		else:
			return M



class BlowupConstruction(Construction):

	def __init__(self, g, weights=None, field=None, no_symmetry=False):
	
		if g.oriented and g.is_degenerate:
			raise NotImplementedError("degenerate oriented graphs not supported.")
	
		self._graph = g

		if weights is None:
			self._weights = None
		else:
			if len(weights) != g.n:
				raise ValueError
			self._weights = weights
	
		if field is None:
			self._field = RationalField()
		else:
			self._field = field

		# Only make use of symmetry when all the conditions are right...
	
		if (field is None and weights is None
			and type(g) is GraphFlag and g.n > 4 and not no_symmetry):
			self._use_symmetry = True
		else:
			self._use_symmetry = False


	@property
	def graph(self):
		return self._graph

		
	@property
	def weights(self):
		return self._weights


	@property
	def field(self):
		return self._field
	

	def subgraph_densities(self, n):

		if self._use_symmetry:
			return self.symm_subgraph_densities(n)

		cn = self._graph.n
		total = Integer(0)
		sharp_graph_counts = {}
		sharp_graphs = []

		for P in UnorderedTuples(range(1, cn + 1), n):
		
			factor = factorial(n)
			for i in range(1, cn + 1):
				factor /= factorial(P.count(i))
			
			if self._weights:
				for v in P:
					factor *= self._weights[v - 1]
			
			ig = self._graph.degenerate_induced_subgraph(P)
			ig.make_minimal_isomorph()
			
			ghash = hash(ig)
			if ghash in sharp_graph_counts:
				sharp_graph_counts[ghash] += factor
			else:
				sharp_graphs.append(ig)
				sharp_graph_counts[ghash] = factor

			total += factor
		
		return [(g, sharp_graph_counts[hash(g)] / total) for g in sharp_graphs]


	def zero_eigenvectors(self, tg, flags):

		if self._use_symmetry:
			return self.zero_eigenvectors(tg, flags)

		cn = self._graph.n
		s = tg.n
		k = flags[0].n # assume all flags the same order

		rows = []

		for tv in Tuples(range(1, cn + 1), s):

			it = self._graph.degenerate_induced_subgraph(tv)
			if not it.is_equal(tg):
				continue

			total = Integer(0)
			row = [0] * len(flags)
		
			for ov in UnorderedTuples(range(1, cn + 1), k - s):
		
				factor = factorial(k - s)
				for i in range(1, cn + 1):
					factor /= factorial(ov.count(i))

				if self._weights:
					for v in ov:
						factor *= self._weights[v - 1]
				
				ig = self._graph.degenerate_induced_subgraph(tv + ov)
				ig.t = s
				ig.make_minimal_isomorph()
				
				for j in range(len(flags)):
					if ig.is_equal(flags[j]):
						row[j] += factor
						total += factor
						break
						
			for j in range(len(flags)):
				row[j] /= total	
			rows.append(row)

		M = matrix(self._field, rows, sparse=True)
		M = M.echelon_form()
		M = M[:M.rank(),:]
		
		if M.rank() == 0:
			return matrix(self._field, 0, len(flags), sparse=True)
		else:
			return M


	# TODO: doesn't support weights

	def raw_zero_eigenvectors(self, tg, flags):

		rows = set()
		for tv in Tuples(range(1, self._graph.n + 1), tg.n):
			rows.add(tuple(self._graph.degenerate_flag_density(tg, flags, tv)))

		return matrix(self._field, list(rows), sparse=True)


	#
	# "Symmetric" versions follow.
	#


	def tuple_orbits(self, k):
		
		SG = self._graph.Graph()
		G, d = SG.automorphism_group(translation=True)

		# Sage gives the graph new labels! Get a translation dictionary.
		rd = dict((v,k) for (k,v) in d.iteritems())

		gen_str = ", ".join(str(t) for t in G.gens())
		gap_str = "g := Group(%s);" % gen_str
		gap.eval(gap_str)

		orbs = gap.new("Orbits(g, Tuples([1..%d], %d), OnTuples);" % (self._graph.n, k)).sage()

		total = 0
		orb_reprs = {}
		for o in orbs:
			sys.stdout.write("Orbit %d:\n" % len(orb_reprs))
			orb_reprs[tuple(o[0])] = len(o)
			for t in o:
				ig = self._graph.degenerate_induced_subgraph(map(lambda x : rd[x], t))
				ig.make_minimal_isomorph()
				sys.stdout.write("%s " % ig)
			sys.stdout.write("\n")

		return orb_reprs
		

	# NOTE: This computes orbits on *sets* and then expands these sets in different
	# ways to form k-tuples. This results in more representatives than is strictly
	# necessary, but it is much faster than doing otherwise.

	def tuple_orbit_reps(self, k, prefix=[]):
		
		s = len(prefix)
		tp = tuple(prefix)
		if s > k:
			raise ValueError
		
		SG = self._graph.Graph()
		G, d = SG.automorphism_group(translation=True)

		# Sage gives the graph new labels! Get a translation dictionary, and
		# relabel the generators back to how they should be.

		rd = dict((v,k) for (k,v) in d.iteritems())
		trans_gens = [gen.cycle_tuples() for gen in G.gens()]
		gens = [tuple(tuple(map(lambda x : rd[x], cy)) for cy in gen) for gen in trans_gens]

		# Pass generators to GAP to create a group for us.
		
		gen_str = ",".join("(" + "".join(str(cy) for cy in cys) + ")" for cys in gens)
		gap.eval("g := Group(%s);" % gen_str)
		if len(prefix) > 0:
			gap.eval("g := Stabilizer(g, %s, OnTuples);" % list(set(prefix)))

		S = []
		for i in range(1, k - s + 1):
			S.extend([tuple(sorted(list(x))) for x in Subsets(self._graph.n, i)])
		
		set_orb_reps = {}

		#sys.stdout.write("Calculating orbits")

		while len(S) > 0:

			rep = list(S[0])

			o = gap.new("Orbit(g, %s, OnSets);" % (rep,)).sage()
			o = list(set([tuple(sorted(t)) for t in o]))
			ot = o[0]
			set_orb_reps[ot] = len(o)
			for t in o:
				S.remove(t)
			#sys.stdout.write(".")
			#sys.stdout.flush()

		#sys.stdout.write("\n")

		combs = [tuple(c) for c in Compositions(k - s)]
		factors = []
		for c in combs:
			factor = factorial(k - s)
			for x in c:
				factor /= factorial(x)
			factors.append(factor)

		orb_reps = {}
		total = 0
		
		for ot, length in set_orb_reps.iteritems():

			ne = len(ot)
			for ci in range(len(combs)):
				c = combs[ci]
				if len(c) == ne:
					t = tp
					for i in range(ne):
						t += c[i] * (ot[i],)
					weight = factors[ci] * length
					orb_reps[t] = weight
					total += weight

		return (total, orb_reps)
	

	def symm_zero_eigenvectors(self, tg, flags, flag_basis=None):

		s = tg.n
		k = flags[0].n # assume all flags the same order

		rows = []

		t_total, t_orb_reps = self.tuple_orbit_reps(s)

		for t_rep, t_factor in t_orb_reps.iteritems():
			
			for tp in Permutations(t_rep):

				it = self._graph.degenerate_induced_subgraph(tp)
				if not it.is_equal(tg):
					continue

				total, orb_reps = self.tuple_orbit_reps(k, prefix=tp)
				
				row = [0] * len(flags)
				
				for P, factor in orb_reps.iteritems():
				
					ig = self._graph.degenerate_induced_subgraph(P)
					ig.t = s
					ig.make_minimal_isomorph()
					
					for j in range(len(flags)):
						if ig.is_equal(flags[j]):
							row[j] += Integer(factor) / total
							break
				
				rows.append(row)

		M = matrix(self._field, rows, sparse=True)
		M = M.echelon_form()
		M = M[:M.rank(),:]
		
		if M.rank() == 0:
			return matrix(self._field, 0, len(flags), sparse=True)
		else:
			return M
	
	
	def symm_subgraph_densities(self, n):

		sharp_graph_counts = {}
		sharp_graphs = []
		
		total, orb_reps = self.tuple_orbit_reps(n)
		
		sys.stdout.write("Found %d orbits.\n" % len(orb_reps))
		
		for P, factor in orb_reps.iteritems():
		
			ig = self._graph.degenerate_induced_subgraph(P)
			ig.make_minimal_isomorph()
			
			ghash = hash(ig)
			if ghash in sharp_graph_counts:
				sharp_graph_counts[ghash] += factor
			else:
				sharp_graphs.append(ig)
				sharp_graph_counts[ghash] = factor

		return [(g, sharp_graph_counts[hash(g)] / Integer(total)) for g in sharp_graphs]
	
