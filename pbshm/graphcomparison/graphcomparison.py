import json
from flask import Blueprint, current_app, g, render_template, request, redirect
from pbshm.authentication.authentication import authenticate_request
from pbshm.pathfinder.pathfinder import population_list
from pbshm.db import structure_collection
import pbshm.graphcomparison.filehandling as fh
import datetime
import re
import pandas as pd

import seaborn as sns
import io
import base64
import matplotlib as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

#Create Blueprint
bp = Blueprint("graphcomparison", __name__, template_folder="templates")

@bp.route("/list")
@authenticate_request("graphcomparison-list")
def list():
	return population_list("graphcomparison.generate")

@bp.route("/generate/<population>")
@authenticate_request("graphcomparison-load-the-page")
def generate(population):
	documents = []
	for document in structure_collection().aggregate([
		{"$match": {
			"population": population, 
			"models":{"$exists":True}
		}},
		{"$project": {
			"_id": 0,
			"timestamp": 0,
			"population": 0,
			"models": 0
		}}
	]):
		documents.append(document)
	return render_template("compare.html", structures=documents)

@bp.route("/compare", methods=("GET", "POST"))
def compare():
	if request.method == "POST":
		form = request.form
		raw_name_list = form['structure_list']
		name_list = []
		for structure in re.split(",", raw_name_list):
			name_list.append(structure.strip())
		
		structure_list = []
		print(name_list)
		for name in name_list:
			structure = {}
			for document in structure_collection().aggregate([
				{"$match": {
					"name": name
				}},
				{"$limit": 1},
				{"$project": {
					"_id": 0,
					"timestamp": 0,
					"population": 0
				}}
			]):
				structure_list.append(document)

		similarity_matrix, nodes_in_mcs = fh.create_distance_matrix(structure_list)

		df = pd.DataFrame(data=similarity_matrix, index=name_list, columns=name_list).round(2)
		df2 = pd.DataFrame(data=nodes_in_mcs, index=name_list, columns=name_list).astype(int)

		plt.pyplot.switch_backend('Agg') 
		sns_plot = sns.heatmap(df, annot=True, cmap="summer_r")
		fig = sns_plot.get_figure()

		canvas=FigureCanvas(fig)
		img = io.BytesIO()
		fig.savefig(img)
		img.seek(0)

		img_byte = img.getvalue()
		# send_file(img,mimetype='img/png')

		return render_template("results.html", 
							   raw_name_list=raw_name_list, 
							   img_result=base64.b64encode(img_byte).decode(),
							   tables=[df2.to_html(classes='data')],
							   titles=df.columns.values)
	return redirect("/")