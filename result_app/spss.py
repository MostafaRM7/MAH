import requests
import pandas as pd
import pyreadstat

def send_spss_request():
    # URL to send the POST request
    url = "your_url_here"

    # Define the headers
    headers = {
        "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryr8NPmsJm2wjA81KA"
    }

    # Define the body
    body = """
    ------WebKitFormBoundaryr8NPmsJm2wjA81KA
    Content-Disposition: form-data; name="انتخابات مجلسExcelOutput (2).xlsx"; filename="انتخابات مجلسExcelOutput (2).xlsx"
    Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    
    {excel_data_here}
    ------WebKitFormBoundaryr8NPmsJm2wjA81KA
    Content-Disposition: form-data; name="destinationFileName"
    
    انتخابات مجلسExcelOutput (2).sav
    ------WebKitFormBoundaryr8NPmsJm2wjA81KA
    Content-Disposition: form-data; name="sheetID"
    
    rId1
    ------WebKitFormBoundaryr8NPmsJm2wjA81KA--
    """.format(excel_data_here="your_excel_data_here")

    # Send the POST request
    response = requests.post(url, headers=headers, data=body)

    # Check the response
    if response.status_code == 200:
        print("Request successful!")
        # You can access the response content if needed
        print(response.content)
    else:
        print("Request failed with status code:", response.status_code)


# Read Excel file
excel_data = pd.read_excel('انتخابات مجلسExcelOutput (2).xlsx')


# Preprocess column names to adhere to SPSS variable naming conventions
excel_data.columns = excel_data.columns.str.strip()  # Remove leading/trailing whitespaces
excel_data.columns = excel_data.columns.str.replace(' ', '_')  # Replace spaces with underscores
excel_data.columns = excel_data.columns.str.replace('[^\w\s]', '', regex=True)  # Remove non-word characters

# Ensure column names start with a letter
excel_data.columns = [col if col[0].isalpha() else 'X' + col for col in excel_data.columns]

# Truncate column names to 64 characters
excel_data.columns = [col[:20] for col in excel_data.columns]

pyreadstat.write_sav(excel_data, "output.sav")
