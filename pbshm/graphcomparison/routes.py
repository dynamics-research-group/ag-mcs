import base64
import io
import math

from flask import Blueprint, render_template, request
import matplotlib.pyplot as plt
import seaborn as sns

from pbshm.authentication import authenticate_request
from pbshm.db import default_collection
from pbshm.timekeeper import nanoseconds_since_epoch_to_datetime
from pbshm.graphcomparison.matrix import ComparisonType, create_similarity_matrix

#Create Blueprint
bp = Blueprint("graphcomparison", __name__, template_folder="templates")

@bp.route("/list")
@authenticate_request("graphcomparison-list")
def list():
	documents = []
	for document in default_collection().aggregate([
		{"$match": {
			"models": {"$exists": True}
		}},
        {"$group":{
            "_id": "$population",
            "structure_names": {"$addToSet": "$name"}
        }},
        {"$project":{
            "_id": 0,
            "population_name": "$_id",
            "structure_names": 1,
        }},
        {"$sort": {"population_name": 1}}
	]):
		documents.append(document)
	return render_template("list-ie-models.html", populations=documents)

@bp.route("/generate/<population>")
@authenticate_request("graphcomparison-list-structures")
def generate(population):
	documents = []
	for document in default_collection().aggregate([
		{"$match": {
			"population": population, 
			"models": {"$exists": True}
		}},
		{"$project": {
			"_id": 0,
			"name": 1,
			"population": 1, 
			"timestamp": 1,
			"elements": {"$size": "$models.irreducibleElement.elements"},
			"relationships": {"$size": "$models.irreducibleElement.relationships"}
		}}
	]):
		document["date"] = nanoseconds_since_epoch_to_datetime(document["timestamp"]).strftime("%d/%m/%Y %H:%M:%S")
		documents.append(document)
	return render_template("compare.html", structures=documents, comparison_types=ComparisonType)

@bp.route("/compare", methods=["POST"])
def compare():
	#Acquire Inputs
	form = request.form
	comparison_type_value = form.get("comparison_type")
	name_list = form.getlist("structure_selection")
	name_order = [f"{form.get(f'structure_order_{name}')}:{name}" for name in name_list]
	sorted_name_list = [name.split(':', 1)[-1] for name in sorted(name_order)]
	#Load Models
	structure_list = []
	for name in sorted_name_list:
		for document in default_collection().aggregate([
			{"$match": {
				"name": name
			}},
			{"$project": {
				"_id": 0,
				"name": 1,
				"models": 1
			}},
			{"$limit": 1}
		]):
			structure_list.append(document)
	#Generate Similarity Matrix
	comparison_type = ComparisonType(int(comparison_type_value))
	similarity_matrix, nodes_in_mcs, results_list = create_similarity_matrix(structure_list, structure_list, comparison_type)
	#Prepare Heatmap
	size = math.floor(len(name_list) * 1.15) if len(name_list) > 4 else 7
	fig, ax = plt.subplots(figsize=(size, size), dpi=300)
	sns_ax = sns.heatmap(
		similarity_matrix, annot=True, fmt="0.3f",
		xticklabels=sorted_name_list, yticklabels=sorted_name_list,
		cbar=True, cmap="viridis", ax=ax
	)
	sns_ax.figure.tight_layout()
	#Save to IO stream
	img = io.BytesIO()
	fig.savefig(img, format="png")
	img.seek(0)
	#Render Template
	return render_template("results.html", 
		original_structure_list=sorted_name_list,
		comparison_structure_list=sorted_name_list,
		comparison_type=comparison_type,
		img_result=base64.b64encode(img.read()).decode(),
		jaccard_index_matrix=similarity_matrix,
		nodes_in_mcs_matrix=nodes_in_mcs
	)