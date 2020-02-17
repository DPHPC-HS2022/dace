""" Map Fission transformation. """

from copy import deepcopy as dcpy
from dace import dtypes, registry, symbolic, sdfg as sd
from dace.graph import nodes, nxutil
from dace.graph.graph import OrderedDiGraph
from dace.sdfg import replace
from dace.transformation import pattern_matching
from typing import List, Union


@registry.autoregister_params(singlestate=True)
class MapFission(pattern_matching.Transformation):
    """ Implements the MapFission transformation.
        Map fission refers to subsuming a map scope into its internal subgraph,
        essentially replicating the map into maps in all of its internal
        components. This also extends the dimensions of "border" transient
        arrays (i.e., those between the maps), in order to retain program
        semantics after fission.

        There are two cases that match map fission:
        1. A map with an arbitrary subgraph with more than one computational
           (i.e., non-access) node. The use of arrays connecting the
           computational nodes must be limited to the subgraph, and non
           transient arrays may not be used as "border" arrays.
        2. A map with one internal node that is a nested SDFG, in which
           each state matches the conditions of case (1).

        If a map has nested SDFGs in its subgraph, they are not considered in
        the case (1) above, and MapFission must be invoked again on the maps
        with the nested SDFGs in question.
    """
    _map_entry = nodes.EntryNode()
    _nested_sdfg = nodes.NestedSDFG("", OrderedDiGraph(), set(), set())

    @staticmethod
    def annotates_memlets():
        return False

    @staticmethod
    def expressions():
        return [
            nxutil.node_path_graph(MapFission._map_entry, ),
            nxutil.node_path_graph(
                MapFission._map_entry,
                MapFission._nested_sdfg,
            )
        ]

    @staticmethod
    def _components(subgraph: sd.SubgraphView) -> List[nodes.Node]:
        """ Returns the list of non-array components in this subgraph. """
        graph = (subgraph
                 if isinstance(subgraph, sd.SDFGState) else subgraph.graph)
        sdict = subgraph.scope_dict(node_to_children=True)
        ns = [
            graph.exit_nodes(n)[0] if isinstance(n, nodes.EntryNode) else n
            for n in sdict[None]
            if isinstance(n, (nodes.CodeNode, nodes.EntryNode))
        ]

        return ns

    @staticmethod
    def can_be_applied(graph, candidate, expr_index, sdfg, strict=False):
        map_node = graph.node(candidate[MapFission._map_entry])
        nsdfg_node = None
        if expr_index == 0:  # Map with subgraph
            subgraphs = [
                graph.scope_subgraph(
                    map_node, include_entry=False, include_exit=False)
            ]
        else:  # Map with nested SDFG
            nsdfg_node = graph.node(candidate[MapFission._nested_sdfg])
            # Make sure there are no other internal nodes in the map
            if len(set(e.dst for e in graph.out_edges(map_node))) > 1:
                return False
            subgraphs = list(nsdfg_node.sdfg.nodes())

        # Test subgraphs
        for sg in subgraphs:
            components = MapFission._components(sg)
            snodes = sg.nodes()
            # Test that the subgraphs have more than one computational component
            if len(snodes) > 0 and len(components) <= 1:
                return False

            # Test that the components are connected by transients that are not
            # used anywhere else
            border_arrays = set()
            for component in components:
                sinks = sg.sink_nodes()
                for e in sg.out_edges(component):
                    if (isinstance(e.dst, nodes.AccessNode)
                            and e.dst not in sinks):
                        border_arrays.add(e.dst.data)

            # 1. In nested SDFGs and subgraphs, ensure none of the border
            #    values are non-transients
            for array in border_arrays:
                if expr_index == 0:
                    ndesc = sdfg.arrays[array]
                else:
                    ndesc = nsdfg_node.sdfg.arrays[array]

                if ndesc.transient is False:
                    return False

            # 2. In subgraphs, make sure transients are not used/allocated
            #    in other scopes or states
            if expr_index == 0:
                # Find all nodes not in subgraph
                not_subgraph = set(
                    n.data for n in graph.nodes()
                    if n not in snodes and isinstance(n, nodes.AccessNode))
                not_subgraph.update(
                    set(n.data for s in sdfg.nodes() if s != graph
                        for n in s.nodes() if isinstance(n, nodes.AccessNode)))

                for component in components:
                    for e in sg.out_edges(component):
                        if isinstance(e.dst, nodes.AccessNode):
                            if e.dst.data in not_subgraph:
                                return False

        return True

    @staticmethod
    def match_to_str(graph, candidate):
        map_entry = graph.node(candidate[MapFission._map_entry])
        return map_entry.map.label

    def apply(self, sdfg: sd.SDFG):
        graph: sd.SDFGState = sdfg.nodes()[self.state_id]
        map_entry = graph.node(self.subgraph[MapFission._map_entry])

        # Obtain subgraph to perform fission to
        if self.expr_index == 0:  # Map with subgraph
            subgraphs = [
                graph.scope_subgraph(
                    map_entry, include_entry=False, include_exit=False)
            ]
        else:  # Map with nested SDFG
            nsdfg_node: nodes.NestedSDFG = graph.node(
                self.subgraph[MapFission._nested_sdfg])
            subgraphs = nsdfg_node.sdfg.nodes()

        for subgraph in subgraphs:
            # TODO: Collect all intermediate components and border arrays/code->code edges
            components = MapFission._components(subgraph)

        # TODO: Add extra arrays and dimensions

        # TODO: Add extra maps

        # TODO: Remove outer map
