from flask import Flask, send_file

app = Flask(__name__)


def create_file():
    with open('file.txt', mode='w') as file:
        pass


@app.route('/', methods=['GET'])
def index():
    return "Running..."


@app.route('/download/', methods=['GET'])
def download():
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active

    sheet["A1"] = "Division"
    sheet["B1"] = "Action Items"
    sheet["C1"] = "Deliverables"
    sheet["D1"] = "Development & Assignment of Deliverables"
    sheet["E1"] = "Management Approval"
    sheet["F1"] = "Commissioner's Approval"
    sheet["G1"] = "Published or Completed"
    sheet["H1"] = "Reason for Delay (Divisional)"
    sheet["I1"] = "Presented & Approved at the Commission's Meeting"
    sheet["J1"] = "Finalized at Commission Level"
    sheet["K1"] = "Reason for Delay (Commision)"

    workbook.save(filename="NERC_projects.xlsx")
    return send_file('NERC_projects.xlsx', as_attachment=True)



if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
