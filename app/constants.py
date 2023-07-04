DATE_FORMAT = '%Y-%m-%d'

def create_event_status_css(val):
    if val == "Not Started" or val == False:
        return "danger"

    if val == "In Progress":
        return "warning"

    if val == "Completed" or val == True:
        return "success"
