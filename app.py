import os
from datetime import time
from time import sleep

import pdfplumber
import re
import json
import gdown
import argparse
import requests

def extract_data_from_pdf(pdf_path, intBusinessUnitId, unique_elements):
    dteDate_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
    testTime_pattern = r'\d{1,2}:\d{2}'
    strHeatNo_pattern = r'[A-Z]{2}-\d{3}'

    output_data_list = []

    with pdfplumber.open(pdf_path) as pdf:
        extracted_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            extracted_text += text

    cleaned_text = extracted_text.replace("< x > (1) ", "")
    cleaned_text = cleaned_text.replace("< ", "")
    lines = cleaned_text.split('\n')
    cleaned_lines = [line for line in lines if not all(perc in line for perc in ["%"] * 8)]
    cleaned_text = '\n'.join(cleaned_lines)

    lines = cleaned_text.split('\n')

    section1 = lines[0:5]
    section2 = lines[5:13]

    section1_text = '\n'.join(section1)
    section2_text = '\n'.join(section2)

    dteDate_match = re.search(dteDate_pattern, section1_text)
    time_match = re.search(testTime_pattern, section1_text)
    strHeatNo_match = re.search(strHeatNo_pattern, section1_text)

    dteDate = dteDate_match.group() if dteDate_match else "Not found"
    testingTime = time_match.group() if dteDate_match else "Not found"
    strHeatNo = strHeatNo_match.group() if strHeatNo_match else "Not found"

    intBusinessUnitId = intBusinessUnitId

    section2_lines = section2_text.split('\n')
    section2_words = [line.split() for line in section2_lines]

    formatted_data = {}

    for i in range(0, len(section2_words), 2):
        for j in range(len(section2_words[i])):
            element = section2_words[i][j]
            value = section2_words[i + 1][j]
            formatted_data[element] = value

    selected_elements = ["C", "Si", "Mn", "P", "S", "Cr", "Cu", "Ni", "Ce"]

    for element in selected_elements:
        if element in formatted_data and element not in unique_elements:
            unique_elements.add(element)

            output_data = {
                'secretKey': 'dGFudmlyQGlib3MuaW8=',
                'allUnitsQcdataId': 0,
                'intBusinessUnitId': intBusinessUnitId,
                'section': '',
                'dteDate': dteDate,
                'strShift': "",
                "machine": "string",
                "productCriteria": "",
                "testFacilities": "",
                "partyName": "",
                "operatorName": "",
                "supervisorName": "",
                'batchOrGrade': strHeatNo,
                "testingTime": testingTime,
                "testName": "",
                "testIngridentUoM": "%",
                "testIngrident": element,
                "uperLimit": 0,
                "standard": 0,
                "lowerLimit": 0,
                "testReport": formatted_data[element],
                "productionUoM": "",
                "productionQty": 0,
                "qcqty": 0,
                "problemQty": 0,
                "problemCategory": "",
                "qcinstructions": "",
                "customerComments": "",
                "insertDate": "2023-11-09T08:33:33.592Z",
                "isActive": True,
                "userIdentity": "tanvir@ibos.io"
            }
            output_data_list.append(output_data)

    return output_data_list

def process_folder(folder_path):
    result = []
    unique_elements = set()

    for root, dirs, files in os.walk(folder_path):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            for file in os.listdir(folder_path):
                if file.endswith('.pdf'):
                    pdf_path = os.path.join(folder_path, file)
                    data = extract_data_from_pdf(pdf_path, folder, unique_elements)
                    result.extend(data)

    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-gfile', '--download_google_file', help="Downloads a Google File")
    args = parser.parse_args()

    if args.download_google_file:
        url = args.download_google_file
        file_id = url.split('/')[-2]

        prefix = 'https://drive.google.com/uc?/export=download&id='
        gdown.download(prefix + file_id)
        print("File downloaded")

    google_folder_link = "https://drive.google.com/drive/folders/1umFRgYxrc-odZ9Jd6nw7Dl6B4QSCJ7Jr?usp=drive_link"

    gdown.download_folder(google_folder_link)
    print("Folder downloaded")

    folder_path = 'QC'

    for root, dirs, files in os.walk(folder_path):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            for file in os.listdir(folder_path):
                if file.endswith('.pdf'):
                    pdf_path = os.path.join(folder_path, file)
                    data = extract_data_from_pdf(pdf_path, folder, set())

                    json_output = json.dumps(data, indent=4)
                    print(json_output)

                    api_url = "https://deverp.ibos.io/mes/QCTest/CreateAllUnitSQcData"
                    headers = {
                        "Content-Type": "application/json"
                    }

                    response = requests.post(api_url, data=json.dumps(data), headers=headers)

                    if response.status_code == 200:
                        print("POST request successful")
                    else:
                        print(f"POST request failed with status code {response.status_code}")
                        print(response.text)

                    sleep(5)  # Use sleep function from the time module
