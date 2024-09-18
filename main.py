from flask import Flask, render_template, request, send_file
import smtplib
import logging
import plotly.express as px
import pandas as pd
import json
import plotly
import io
import numpy as np
df = pd.read_csv("C:/Hackathon/data_files/new_data_set.csv")

# Load the data dictionary
data_dict = pd.read_csv("C:/Hackathon/data_files/CHEMDATA_table1.csv")
data_for_corr = df[["Alk","pCO2","O2","pH","NO3","PO4"]]

correlation_matrix = data_for_corr.corr()
fig1 = px.imshow(
    correlation_matrix,
    labels=dict(x="Chemical Properties", y="Chemical Properties", color="Correlation"),
    x=correlation_matrix.columns,
    y=correlation_matrix.columns,
    color_continuous_scale="RdBu",
    title="Correlation Heatmap of Water Chemical Properties",
)

# Show the plot
# Create a scatter plot of Alkalinity vs Dissolved Oxygen
fig2 = px.scatter(df, x="Alk", y="O2",
                  labels={"Alk": "Alkalinity (uEq/l)", "O2": "Dissolved Oxygen (uM)"},
                  title="Alkalinity vs Dissolved Oxygen")

# Convert all figures to JSON


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
FROM_ADDRESS = "afridiafshan01@gmail.com"
PASSWORD = "pewl ycsq khcf llzf"


@app.route("/", methods=["GET", "POST"])
def home_page():
    if request.method == "POST":
        # Handle the form submission (POST request)
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Creating the email message structure
        msg = f"From: {FROM_ADDRESS}\nTo: {email}\nSubject: {subject}\n\n{message}\n\nBest regards,\n{name}"
        # Use logging for production-level output
        logging.debug(f"Name: {name}, Email: {email}, Subject: {subject}, Message: {message}")

        try:
            # Establish a secure SMTP connection
            smtp = smtplib.SMTP("smtp.gmail.com", 587)
            smtp.starttls()  # Secure the connection
            smtp.login(FROM_ADDRESS, PASSWORD)  # Use the app password here

            # Format the email message with subject and body
            msg = f"Subject: {subject}\n\n{message}"

            # Send the email to the recipient
            smtp.sendmail(FROM_ADDRESS, email, msg)
            smtp.quit()

            print("Email sent successfully!")

        except Exception as e:
            print(f"Failed to send email. Error: {str(e)}")
    # Create a list of numeric columns for the dropdown
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_columns.remove('pH')  # Remove pH as it will always be on the y-axis

    # Get the selected parameter from the query string, default to 'Alk'
    selected_param = request.args.get('param', 'Alk')

    # Create the box plot with the selected parameter
    fig3 = px.box(df, x="Station", y="pH", color=selected_param,
                  title=f"pH Distribution Across Stations (Colored by {selected_param})")
    # Convert all figures to JSON
    plot_json1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    plot_json2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    plot_json3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    # Render the HTML form (GET request)
    return render_template("index.html", plot_json1=plot_json1, plot_json2=plot_json2,
                           plot_json3=plot_json3, numeric_columns=numeric_columns,
                           selected_param=selected_param)



@app.route("/download_data")
def download_data():
    output = io.BytesIO()

    # Write the data dictionary first
    output.write(b"Data Dictionary:\n")
    data_dict.to_csv(output, index=False)

    # Add a separator
    output.write(b"\n\nMain Data:\n")

    # Write the main data
    df.to_csv(output, index=False)

    output.seek(0)
    return send_file(output,
                     mimetype='text/csv',
                     download_name='water_quality_data_with_dictionary.csv',
                     as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
