from a_star import *
from create_graph_from_map import *
import networkx as nx
import math
import copy
import unittest
import string
from test_map_word_accepted_randomized_occupancy_grid import *
from lomap.algorithms.product import ts_times_buchi
from lomap.classes import Buchi, Ts

EMPTY_SYMBOL='0'

# Load map, start and goal point.
def load_symbol_map(file_path):
    grid = []
    start = [0, 0]
    goal = [0, 0]
    # Load from the file
    with open(file_path, 'r') as map_file:
        reader = csv.reader(map_file)
        for i, row in enumerate(reader):
            # load start and goal point
            if i == 0:
                start[0] = int(row[1])
                start[1] = int(row[2])
            elif i == 1:
                goal[0] = int(row[1])
                goal[1] = int(row[2])
            # load the map
            else:
                parsed_row = [col for col in row]
                grid.append(parsed_row)
    return grid, start, goal

def assign_props(grid):
    props = dict()
    reduced = list(set(i for j in grid for i in j))
    reduced.remove(EMPTY_SYMBOL)
    reduced.sort()

    single_values=[x for x in reduced if len(x)==1]

    for i in range(len(single_values)):
        props[single_values[i]] = 2**i

    return props

def create_numerical_grid(props, symbol_grid):

    grid = copy.deepcopy(symbol_grid)

    for row in range(len(symbol_grid)):
        for col in range(len(symbol_grid[0])):
            val = symbol_grid[row][col]
            if val != EMPTY_SYMBOL:
                if val in list(props.keys()):
                    grid[row][col] = props.get(val)
                elif len(val) > 1:
                    sum = 0
                    for letter in val:
                        sum += props.get(letter)
                    grid[row][col] = sum
                    props[val] = sum
                else:
                    print("ERROR parsing grid from symbols to binary numerical translation")
    
    return grid


def create_transitions(G, edges, nodes):

    spl = dict(nx.all_pairs_shortest_path_length(G))
    print(f"Shortest path length: {spl}")

    labels = dict()

    for edge in edges:
        for node in nodes:
            key = str(edge)
            start_edge = spl[edge[0]][node]
            end_edge = spl[edge[1]][node]
            # print(f"Start edge dist from {edge[0]} to {node}: {start_edge}")
            # print(f"end edge dist from {edge[1]} to {node}: {end_edge}")
            if start_edge>end_edge:
                if not labels.get(key):
                    label = list()
                    label.append(node)
                    labels[key] = label
                else:
                    labels.get(key).append(node)

    print(f"labels: {labels}")
    return labels

    #Other potentially important functions:
    # sp = dict(nx.all_pairs_shortest_path(G))
    # print(f"Shortest path: {sp}")
    # nx.all_simple_paths(G, source=0, target=3)
    # eg = nx.ego_graph(G, '4', radius=10, center=True, undirected=False, distance=None)
    # print(f"Ego graph: {eg}")
    # fig, axes = plt.subplots(1,1,dpi=72)
    # nx.draw(eg, pos=nx.spring_layout(eg), ax=axes, with_labels=True)
    # plt.show()

def prune_labels(nodes, labels):

    label_keys = list(labels.keys())

    #for these purposes, need to remove every sub label e.g. 1.1 1.2 and replace it with 1, since same symbol in map
    for node in nodes:
        for label_key in label_keys:
            pruned_label = list(set(map(lambda x: str(math.floor(float(x))),labels.get(label_key)))) #set to remove duplicates
            labels[label_key] = pruned_label
    
    pruned_labels = copy.deepcopy(labels)

    for node in nodes:
        node_outgoing_labels = dict()
        simplfied_node_rep = str(math.floor(float(node)))

        #TODO: comment what this does
        for label_key in label_keys:

            label_key_list = label_key.strip('][\'\"').split('\', \'')
            if label_key_list[0] == node:
                node_outgoing_labels[label_key_list[1]] = labels.get(label_key)

        new_transition_dict = dict()

        case_1(node, node_outgoing_labels, new_transition_dict)
        case_2(simplfied_node_rep, node_outgoing_labels)
        case_3(node_outgoing_labels)

        if not new_transition_dict:
            step_transition_dict = {k:[item for item in v] for (k,v) in node_outgoing_labels.items()}
            new_transition_dict.update(step_transition_dict)

        if new_transition_dict:
            for key in new_transition_dict.keys():
                new_key = str([node, key])
                pruned_labels[new_key] = new_transition_dict.get(key)

    return pruned_labels

'''
CASES:
1) if all outgoing edges same share transition and all go to node containing shared transition - remove transition from all (maybe need check to make sure not empty transition?)
2) if there is an outgoing edge containing same label as node remove it 
3) if some outgoing edges go to node containing shared transition but others don't, remove transition from others
4) if 2 of the same node symbols (e.g. 1.0 and 1.1) are connected, there should be no transitions between them that contain the symbol on the transition
etc
'''

def case_1(node, node_outgoing_labels, new_transition_dict):
    if len(list(node_outgoing_labels.keys())) > 1: #if there is more than one outgoing edge
        node_outgoing_label_intersections = set.intersection(*[set(x) for x in node_outgoing_labels.values()])
        print(f"outgoing edge intersection for node {node}: {node_outgoing_label_intersections}")
        if len(node_outgoing_label_intersections) > 0: #if more than one reduced (eg. 1.1, 1.0 = 1) label on different outgoing edges match
            print(f"node_outgoing_labels {node}: {node_outgoing_labels}")

            #TODO: check if works with multiple intersection values
            for node_outgoing_label_intersection in node_outgoing_label_intersections:

                print(f"node_outgoing_label_intersection: {node_outgoing_label_intersection}")

                #transitions that go to node that shares same value as intersection between transitions
                transitions_that_go_to_intersection_node = {k:v for (k,v) in node_outgoing_labels.items() if str(math.floor(float(k))) == node_outgoing_label_intersection}
                print(f"transitions_that_go_to_intersection_node dict: {transitions_that_go_to_intersection_node}")

                #transitions that share same value as intersection
                transitions_that_share_same_value = {k:v for (k,v) in node_outgoing_labels.items() for item in v if item == node_outgoing_label_intersection}
                # transitions_that_share_same_value = {k:[item for item in v if item==str(node_outgoing_label_intersection)] for (k,v) in node_outgoing_labels.items()}

                print(f"transitions_that_share_same_value dict: {transitions_that_share_same_value}")

                if transitions_that_go_to_intersection_node==transitions_that_share_same_value:
                    # if all(len(l) > 1 for l in list(transitions_that_go_to_intersection_node.values())): #all transition labels longer than 1 symbol
                    step_transition_dict = {k:[item for item in v if item!=str(node_outgoing_label_intersection)] for (k,v) in node_outgoing_labels.items()}
                    new_transition_dict.update(step_transition_dict)
                    print(f"new_transition_dict: {new_transition_dict}")     

def case_2(simplfied_node_rep, node_outgoing_labels):
    for key in node_outgoing_labels.keys():
            if simplfied_node_rep in node_outgoing_labels.get(key):
                node_outgoing_labels.get(key).remove(simplfied_node_rep)    

def case_3(node_outgoing_labels):
    for key in node_outgoing_labels.keys():
        if EMPTY_SYMBOL in node_outgoing_labels.get(key):
            node_outgoing_labels.get(key).remove(EMPTY_SYMBOL)

#FIXME: this assumes one empty set area, e.g. '0' not '0.0' and '0.1'
def remove_empty_set(edges, clusters):
    # del clusters[EMPTY_SYMBOL]
    to_remove = list()
    nodes_adjacent_to_empty = list()
    for edge in edges:
        if edge[0] == EMPTY_SYMBOL:
            to_remove.append(edge)
            nodes_adjacent_to_empty.append(edge[1])
        elif edge[1] == EMPTY_SYMBOL:
            to_remove.append(edge)
            nodes_adjacent_to_empty.append(edge[0])
    # edges = list(set(edges).difference(to_remove))
    edges_pruned = [x for x in edges if x not in to_remove]
    pairs = [[nodes_adjacent_to_empty[i], nodes_adjacent_to_empty[j]] for i in range(len(nodes_adjacent_to_empty)) for j in range(i+1, len(nodes_adjacent_to_empty))]
    edges_pruned.extend(pairs)
    return edges_pruned

def convert_edges_and_add_labels_alphabetical(labels, props, edges):

    num_to_alpha_prop = {v: k for k, v in props.items()}
    label_mapping = dict()
    label_mapping[EMPTY_SYMBOL] = '{}'

    #TODO: remove 0? make empty set???
    #FIXMES: will need to replace 0 to get correct product

    for edge in edges:
        pi = labels.get(str(edge))
        for i in range(len(pi)):
            if int(float(pi[i])) != 0:
                pi[i] = num_to_alpha_prop.get(int(pi[i]))

        if int(float(edge[0]))!=0:
            label_mapping[edge[0]] = num_to_alpha_prop.get(int(float(edge[0])))

        if int(float(edge[1]))!=0:
            label_mapping[edge[1]] = num_to_alpha_prop.get(int(float(edge[1])))

        edge.append({'pi':pi, 'weight': 0})

    return edges, label_mapping

def add_edge_labels(labels, edges):
    for edge in edges:
        edge.append({'pi':labels.get(str(edge))})

def create_ts(map_path = "maps/alphabetical_maps/map_multiple_alpha_symbols_complex.csv"):
    '''
    Map must only contain 0s or alphabetical values
    '''
    symbol_grid, start, goal = load_symbol_map(map_path)
    props = assign_props(symbol_grid)
    grid = create_numerical_grid(props, symbol_grid)
    # grid, start, goal = load_map(map_path)

    print(f"replaced grid: {grid}")

    # draw_path(grid, start, goal, [], 'Map')
    clusters = create_clusters(np.asarray(grid))
    print(f"Clusters: {clusters}")
    unique_clusters = each_cluster_uuid(clusters)
    print(f"Unique Clusters: {unique_clusters}")
    edges = create_graph(unique_clusters)
    print(f"Edges: {edges}")
    reversed_edges = [sublist[::-1] for sublist in edges[::-1]]
    print(f"Reversed Edges: {reversed_edges}")
    edges.extend(reversed_edges)

    intermediate_G = nx.DiGraph()
    intermediate_G.add_edges_from(edges)
    
    labels = create_transitions(intermediate_G, edges, list(unique_clusters.keys()))
    labels = prune_labels(list(unique_clusters.keys()), labels)

    G = nx.DiGraph()

    #TODO: determine how to handle multiple nodes with same label
    #FIXME: this will incorrectly override duplicate nodes, making them seem like the same node. For all node.uuid, the uuid is erased
    alphabetical_edges, label_mapping= convert_edges_and_add_labels_alphabetical(labels, props, edges)

    G.add_edges_from(edges)

    '''
    Create transition system example:
        ts = Ts(directed=True, multi=False)add_edges_from
        ts.g = nx.grid_2d_graph(4, 3)

        ts.init[(1, 1)] = 1

        ts.g.add_node((0, 0), attr_dict={'prop': set(['a'])})
        ts.g.add_node((3, 2), attr_dict={'prop': set(['b'])})

        ts.g.add_edges_from(ts.g.edges(), weight=1)
    '''

    ts = Ts(directed=True, multi=False)
    for key in copy.deepcopy(G.nodes.keys()):
        G.add_node(key, prop=key)
    ts.g = G
    ts.init = {'c'}

    draw_graph(G, label_mapping)

    return ts

class TestTSCreation(unittest.TestCase):
    def test_example_1(self):
        nodes = ['0', '1.1', '1.0', '2', '4']
        out_edges = [('0', '1.0'), ('0', '1.1'), ('1.0', '2'), ('1.0', '0'), ('1.1', '4'), ('1.1', '0'), ('2', '1.0'), ('4', '1.1')]
        in_edges = [('1.1', '0'), ('1.0', '0'), ('0', '1.0'), ('2', '1.0'), ('0', '1.1'), ('4', '1.1'), ('1.0', '2'), ('1.1', '4')]
        ts = create_ts('maps/unit_test_maps/alphabetical_maps/example1.csv')
        self.assertEqual(ts.g.number_of_nodes(), 5)
        self.assertEqual(ts.g.number_of_edges(), 8)
        self.assertTrue(set(ts.g.nodes()) == set(nodes))
        self.assertTrue(set(ts.g.out_edges()) == set(out_edges))
        self.assertTrue(set(ts.g.in_edges()) == set(in_edges))

    def test_example_2(self):
        ts = create_ts('maps/unit_test_maps/alphabetical_maps/example2.csv')


if __name__ == '__main__':
    unittest.main()
    # create_ts('maps/unit_test_maps/alphabetical_maps/example1.csv')
    # ts = create_ts('maps/unit_test_maps/alphabetical_maps/example2.csv')