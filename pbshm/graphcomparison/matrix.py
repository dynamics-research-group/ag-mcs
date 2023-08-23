import pbshm.graphcomparison.backtracking as bt
import numpy as np
from typing import List

def generate_attributed_graph_from_ie_model(pbshm_document: object) -> object:
    graph, attributes = {}, {}
    for element in pbshm_document["models"]["irreducibleElement"]["elements"]:
        graph[element["name"]] = []
        attributes[element["name"]] = element["geometry"] if "geometry" in element else "n/a"
    for relationship in pbshm_document["models"]["irreducibleElement"]["relationships"]:
        for element_1 in relationship["elements"]:
            for element_2 in relationship["elements"]:
                if element_1["name"] != element_2["name"]:
                    graph[element_1["name"]].append(element_2["name"])
    return {
        "name": pbshm_document["name"], "graph": graph, "attributes": attributes, "count": {
            "elements": len(pbshm_document["models"]["irreducibleElement"]["elements"]), 
            "relationships": len(pbshm_document["models"]["irreducibleElement"]["relationships"])
        }
    }

def create_similarity_matrix(original_structure_list: List[object], comparison_structure_list: List[object]) -> None:
    #Convert both list to back tracking attributed graphs
    original_name_list = [document["name"] for document in original_structure_list]
    comparison_name_list = [document["name"] for document in comparison_structure_list]
    original_attributed_graph_list = [generate_attributed_graph_from_ie_model(document) for document in original_structure_list]
    comparison_attributed_graph_list = [generate_attributed_graph_from_ie_model(document) for document in comparison_structure_list]
    #Create Similarity Matrix
    original_graph_count, comparison_graph_count = len(original_attributed_graph_list), len(comparison_attributed_graph_list)
    comparison_counter, comparison_total = 0, original_graph_count * comparison_graph_count
    similarity_matrix, node_matrix, result_list = np.zeros((original_graph_count, comparison_graph_count)), np.zeros((original_graph_count, comparison_graph_count)), []
    for original_graph in original_attributed_graph_list:
        for comparison_graph in comparison_attributed_graph_list:
            #Check if cached values exists
            print(f"Comparing {original_graph['name']} to {comparison_graph['name']} ({comparison_counter}/{comparison_total})")
            if comparison_graph["name"] in original_name_list and original_graph["name"] in comparison_name_list:
                comparison_index = original_name_list.index(comparison_graph["name"])
                original_index = comparison_name_list.index(original_graph["name"])
                position = (comparison_index * comparison_graph_count) + original_index
                if position < comparison_counter and original_attributed_graph_list[comparison_index]["name"] == comparison_graph["name"] and comparison_attributed_graph_list[original_index]["name"] == original_graph["name"]:
                    print(f"Found cached values for comparing {comparison_graph['name']} to {original_graph['name']} at ({position}/{comparison_total}), using these values instead of computing again")
                    similarity_matrix[comparison_counter // original_graph_count][comparison_counter % original_graph_count] = similarity_matrix[comparison_index][original_index]
                    node_matrix[comparison_counter // original_graph_count][comparison_counter % original_graph_count] = node_matrix[comparison_index][original_index]
                    result_list.append(result_list[position])
                    comparison_counter += 1
                    continue
            #Create backtrack (largest graph must be the first parameter)
            diagnostic_filename = f"{comparison_counter}-{original_graph['name']}-{comparison_graph['name']}.json"
            backtrack_results = bt.backtrack(original_graph, comparison_graph, filename=diagnostic_filename) if original_graph["count"]["elements"] > comparison_graph["count"]["elements"] else bt.backtrack(comparison_graph, original_graph, filename=diagnostic_filename)
            #Calculate Maximum Common Subgraph (MCS)
            maximum_common_subgraph = []
            for result in backtrack_results:
                if len(maximum_common_subgraph) == 0 or len(result) > len(maximum_common_subgraph[0]):
                    maximum_common_subgraph = [result]
                elif len(result) == len(maximum_common_subgraph[0]):
                    maximum_common_subgraph.append(result)
            #Calculate Jaccard Index
            jaccard_index = len(maximum_common_subgraph[0]) / (original_graph["count"]["elements"] + comparison_graph["count"]["elements"] - len(maximum_common_subgraph[0]))
            #Store results
            similarity_matrix[comparison_counter // original_graph_count][comparison_counter % original_graph_count] = jaccard_index
            node_matrix[comparison_counter // original_graph_count][comparison_counter % original_graph_count] = len(maximum_common_subgraph[0])
            result_list.append(maximum_common_subgraph)
            comparison_counter += 1
    return similarity_matrix, node_matrix, result_list

