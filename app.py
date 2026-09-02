from flask import Flask, render_template, request, redirect
from datetime import datetime, date
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("campaigns.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            platform TEXT NOT NULL,
            description TEXT,
            start_date TEXT,
            end_date TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_campaign_status(start_date, end_date):

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        today = date.today()

        if today < start:
            return "Scheduled"

        elif start <= today <= end:
            return "Active"

        else:
            return "Completed"

    except:
        return "Unknown"


@app.route("/")
def home():

    conn = sqlite3.connect("campaigns.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM campaigns")
    rows = cursor.fetchall()

    total = 0
    scheduled = 0
    active = 0
    completed = 0

    for row in rows:

        status = get_campaign_status(
            row["start_date"],
            row["end_date"]
        )

        total += 1

        if status == "Scheduled":
            scheduled += 1

        elif status == "Active":
            active += 1

        elif status == "Completed":
            completed += 1

    conn.close()

    return render_template(
        "index.html",
        total=total,
        scheduled=scheduled,
        active=active,
        completed=completed
    )


@app.route("/create-campaign", methods=["GET", "POST"])
def create_campaign():

    if request.method == "POST":

        campaign_name = request.form["campaign_name"]
        platform = request.form["platform"]
        description = request.form["description"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        campaign = {
            "name": campaign_name,
            "platform": platform,
            "description": description,
            "start_date": start_date,
            "end_date": end_date
        }

        conn = sqlite3.connect("campaigns.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO campaigns
            (name, platform, description, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            campaign_name,
            platform,
            description,
            start_date,
            end_date
        ))

        conn.commit()
        conn.close()

        return render_template(
            "campaign_success.html",
            campaign=campaign
        )

    return render_template("create_campaign.html")


@app.route("/campaigns")
def view_campaigns():

    conn = sqlite3.connect("campaigns.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM campaigns")
    rows = cursor.fetchall()

    campaigns = []

    for row in rows:

        campaign = dict(row)

        campaign["status"] = get_campaign_status(
            campaign["start_date"],
            campaign["end_date"]
        )

        campaigns.append(campaign)

    conn.close()

    return render_template(
        "campaigns.html",
        campaigns=campaigns
    )


@app.route("/edit-campaign/<int:campaign_id>", methods=["GET", "POST"])
def edit_campaign(campaign_id):

    conn = sqlite3.connect("campaigns.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":

        campaign_name = request.form["campaign_name"]
        platform = request.form["platform"]
        description = request.form["description"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        cursor.execute("""
            UPDATE campaigns
            SET name = ?, platform = ?, description = ?,
                start_date = ?, end_date = ?
            WHERE id = ?
        """, (
            campaign_name,
            platform,
            description,
            start_date,
            end_date,
            campaign_id
        ))

        conn.commit()
        conn.close()

        return redirect("/campaigns")

    cursor.execute(
        "SELECT * FROM campaigns WHERE id = ?",
        (campaign_id,)
    )

    campaign = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_campaign.html",
        campaign=campaign
    )


@app.route("/delete-campaign/<int:campaign_id>")
def delete_campaign(campaign_id):

    conn = sqlite3.connect("campaigns.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM campaigns WHERE id = ?",
        (campaign_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/campaigns")


@app.route("/analytics")
def analytics():

    conn = sqlite3.connect("campaigns.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM campaigns ORDER BY id DESC LIMIT 1"
    )

    campaign = cursor.fetchone()

    analytics_data = None

    if campaign:

        campaign_status = get_campaign_status(
            campaign["start_date"],
            campaign["end_date"]
        )

        campaign_id = campaign["id"]

        reach = 5000 + (campaign_id * 500)
        likes = 450 + (campaign_id * 50)
        comments = 80 + (campaign_id * 10)
        shares = 120 + (campaign_id * 15)

        analytics_data = {
            "reach": reach,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "status": campaign_status
        }

    conn.close()

    return render_template(
        "analytics.html",
        campaign=campaign,
        analytics=analytics_data
    )


init_db()


if __name__ == "__main__":
    app.run(debug=True)