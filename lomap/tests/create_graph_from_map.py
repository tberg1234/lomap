from a_star import *
import numpy as np
import math
import unittest

def create_graph(clusters):
    edges = list()
    keys = list(clusters.keys())

    for i in range(len(keys)-1):
        key = keys[i]
        key_clusters = clusters.get(key)
        for j in range(i+1, len(keys)):
            comparison_key = keys[j]
            comparison_key_clusters = clusters.get(comparison_key)
            
            if cluster_connected(key_clusters, comparison_key_clusters):
                edges.append([key, comparison_key])
    
    return edges
                    

def cluster_connected(key_clusters, comparison_key_clusters):
    for cluster in key_clusters:
        for comparison_cluster in comparison_key_clusters:
            for point in cluster:
                for comparison_point in comparison_cluster:
                    if connected(point, comparison_point):
                        return True
    return False


def create_clusters(grid):
    clusters = dict()
    mappings = dict() #used for when duplicates of labels. E.G 2 seperate regions of Bs, we will have mapping B: (B1, B2)
    for r in range(grid.shape[0]):
        for c in range(grid.shape[1]):
            val = grid[r,c]
            cluster(r, c, val, clusters, mappings)
    return clusters
            

def cluster(r, c, val, clusters, mappings):
    first_in_list = [[r,c]]
    if str(val) in clusters.keys():
        val_clusters = clusters.get(str(val))
        for i in range(len(val_clusters)):
            cluster = val_clusters[i]
            if is_neighbor(r,c,cluster):
                cluster.append([r,c])
                val_clusters[i]=cluster
                return
        val_clusters.append(first_in_list)
        return
    clusters[str(val)]= [first_in_list]

#uses 4 connected neighbor check
def is_neighbor(r,c,cluster):
    for node in cluster:
        if connected(node, [r,c]): #if they are next to each other they will be 1 unit away
            return True
    return False
        
def connected(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2) == 1. #if they are next to each other they will be 1 unit away

def main():
    grid, start, goal = load_map('map_multiple_symbols.csv')
    clusters = create_clusters(np.asarray(grid))
    print(f"Clusters: {clusters}")
    edges = create_graph(clusters)
    print(f"Edges: {edges}")


class TestStringMethods(unittest.TestCase):

    def test_edges_symbol_not_touching_empty(self):
        self.assertEqual(create_graph(create_clusters(np.asarray(load_map('unit_test_maps/map_2_encased.csv')[0]))), [['-1', '0'], ['0', '3'], ['3', '2']])

    def test_clusters_multiple_groupings_same_symbol(self):
        self.assertEqual(len(create_clusters(np.asarray(load_map('unit_test_maps/map_multiple_2_groups.csv')[0])).get('2')), 2)

if __name__ == '__main__':
    
    unittest.main()
    # main()