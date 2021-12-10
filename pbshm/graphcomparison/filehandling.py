import numpy as np
import pbshm.graphcomparison.backtracking as bt
import json

def generate_graph_from_json(structure):

	graph = {}
	attributes = {}
	list_of_nodes = []
	list_of_edges = []

	number_of_elements = len(structure["models"]["irreducibleElement"]["elements"])
	number_of_joints = len(structure["models"]["irreducibleElement"]["relationships"])

	for element in structure["models"]["irreducibleElement"]["elements"]:
		try:
			graph[element["name"]] = []
			# Currently geometry is the only attribute of interest
			if "geometry" in element.keys():
				attributes[element["name"]] = element["geometry"]
				list_of_nodes.append(element["name"])
			else:
				attributes[element["name"]] = "N/A"
				list_of_nodes.append(element["name"])
		except:
			print(element)

	for relationship in structure["models"]["irreducibleElement"]["relationships"]:
		for element1 in relationship["elements"]:
			for element2 in relationship["elements"]:
				if element1["name"] != element2["name"]:
					graph[element1["name"]].append(element2["name"])

	attributed_graph = {}
	attributed_graph["counts"] = {"elements": number_of_elements,
								  "joints": number_of_joints}
	attributed_graph["graph"] = graph
	attributed_graph["attributes"] = attributes
	attributed_graph["nodes"] = list_of_nodes
	attributed_graph["edges"] = list_of_edges

	return attributed_graph

def return_largest_result(results):
	max_len = 0
	for result in results:
		# Has a larger clique has been found?
		if len(result) > max_len:
			# Update the maximum clique length
			max_len = len(result)
			# Reset the maximum clique list
			max_result = result
	return max_result

def largest_graph_first(graph1_attributed, graph2_attributed):
    if graph1_attributed["counts"]["elements"] < graph2_attributed["counts"]["elements"]:
        # Swap graphs so largest is graph1
        temp_graph = graph1_attributed
        graph1_attributed = graph2_attributed
        graph2_attributed = temp_graph
    return graph1_attributed, graph2_attributed

def create_distance_matrix(structure_list):
	# create list of attributed graphs from list of files 
	attributed_graph_list = [generate_graph_from_json(s) for s in structure_list]
	# Create distance matrix with initial distance set to zero
	n = len(attributed_graph_list)
	similarity_matrix = np.zeros((n,n))
	nodes_in_mcs = np.zeros((n,n))
	# Iterate through pairs of graphs in list
	for i, graph1 in enumerate(attributed_graph_list):
		for j, graph2 in enumerate(attributed_graph_list):
			# If graphs are not identical, calculate pairwise distances
			if i <= j:
				print(f"Matching {i+1}/{n} and {j+1}/{n}")
				graph1_attributed, graph2_attributed = largest_graph_first(graph1, graph2)
				results = bt.backtrack(graph1_attributed, graph2_attributed)
				result = return_largest_result(results)
				jaccard_index = len(result) / (graph1_attributed["counts"]["elements"] + graph2_attributed["counts"]["elements"] - len(result))
				similarity_matrix[i][j] = jaccard_index
				nodes_in_mcs[i][j] = len(result)
			if i > j:
				# Use symmetry condition for distance matrix
				similarity_matrix[i][j] = similarity_matrix[j][i]
				nodes_in_mcs[i][j] = nodes_in_mcs[j][i]
	return similarity_matrix, nodes_in_mcs


		