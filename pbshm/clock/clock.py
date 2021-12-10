from flask import Blueprint, current_app, g, render_template, request
from pbshm.authentication.authentication import authenticate_request
from pbshm.db import structure_collection
import datetime

#Create Blueprint
bp = Blueprint("clock", __name__, template_folder="templates")

@bp.route("/demo-day-clock")
@authenticate_request("clock-load-the-page")
def load_the_page():
	now = datetime.datetime.now()
	today = datetime.date.today()

	current_time = now.strftime("%H:%M:%S")
	current_date = today.strftime("%B %d, %Y")
	return render_template("clock.html", time=current_time, date=current_date)