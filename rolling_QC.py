import argparse
import re
import json
from time import sleep
import gdown
import requests
from pdf2image import convert_from_path
import os
import easyocr
from datetime import datetime, timedelta


today = datetime.now().date()

TestDate_ = today - timedelta(days=1)
TestDate = TestDate_.strftime("%Y-%m-%d")

TRACKING_FILE = 'processed_files.txt'

def get_processed_files():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r') as file:
            return set(file.read().splitlines())
    return set()

def add_to_processed_files(filename):
    with open(TRACKING_FILE, 'a') as file:
        file.write(filename + '\n')


def process_pdf(pdf_path):
    poppler_path = r'D:\iBOS\gdrive_downloads\poppler-23.11.0\Library\bin'  # Update with the correct path
    os.environ["PATH"] += os.pathsep + poppler_path

    images = convert_from_path(pdf_path)

    reader = easyocr.Reader(['en'])

    output_file_path = 'ocr_results.txt'

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for i, image in enumerate(images):
            temp_image_path = f'temp_page_{i+1}.jpg'
            image.save(temp_image_path, 'JPEG')

            results = reader.readtext(temp_image_path)

            output_file.write(f"OCR Results for Page {i+1}:\n")
            for result in results:
                cleaned_text = result[1].replace('\n', ' ')
                output_file.write(cleaned_text + '\n')

            os.remove(temp_image_path)

    output_data_list = []

    with open(output_file_path, 'r', encoding='utf-8') as original_file:
        lines = original_file.readlines()

    criteria_pattern = re.compile(r'[0-9A-Za-z]{7} [0-9A-Za-z]{2}MM')
    criteria_ = [line.strip() for line in lines if re.search(criteria_pattern, line)]
    criteria = criteria_[0]

    # def update_criteria(criteria):
    #     if criteria == 'AKIJ ISPAT BS00DWR 08MM':
    #         criteria = 'AKIJ ISPAT B500DWR 08MM'
    #     return criteria
    #     print(update_criteria(criteria))

    unit_list = ['mm', 'mm', 'kg/m', 'mm', 'mm', '%', '%', 'kN']
    testIngrident = ['Nominal diameter(d)', 'Actual diameter', 'Actual Unit Weight', 'Gauge Length', 'Gauge length after fracture(Lu)', 'Elongation after fracture', 'EMF', 'Yield load']

    for i, testReport_line_number in enumerate(range(34, 42)):
        if 0 < testReport_line_number <= len(lines):
            line_elements = lines[testReport_line_number - 1].split()
            if line_elements:
                output_data = {
                    'secretKey': 'dGFudmlyQGlib3MuaW8=',
                    'allUnitsQcdataId': 0,
                    "BusinessUnitId": 224,
                    'section': '',
                    'TestDate': TestDate,
                    'strShift': "",
                    "machine": "",
                    "productCriteria": 'AKIJ ISPAT B500DWR 08MM',
                    "testFacilities": "",
                    "partyName": "",
                    "operatorName": "",
                    "supervisorName": "",
                    'batchOrGrade': "",
                    "testingTime": '',
                    "testType": "",
                    "testName": "Rolling QC",
                    "testIngridentUoM": unit_list[i],  # Use the corresponding unit from the list
                    "testIngrident": testIngrident[i],  # Use the corresponding testIngrident value from the list
                    "uperLimit": 0,
                    "standard": 0,
                    "lowerLimit": 0,
                    "testReport": float(line_elements[0]),
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

    unit_list = ['MPa', 'kN', 'MPa', 'kN', ' ']
    testIngrident = ['Yield strength (Re)', 'Maximum force (Fm)', 'Tensile strength (Rm)', 'Rupture load', 'TS/YS Ratio']

    for i, testReport_line_number in enumerate(range(57, 62)):
        if 0 < testReport_line_number <= len(lines):
            line_elements = lines[testReport_line_number - 1].split()
            if line_elements:
                output_data = {
                    'secretKey': 'dGFudmlyQGlib3MuaW8=',
                    'allUnitsQcdataId': 0,
                    "BusinessUnitId": 224,
                    'section': '',
                    'TestDate': TestDate,
                    'strShift': "",
                    "machine": "",
                    "productCriteria": 'AKIJ ISPAT B500DWR 08MM',
                    "testFacilities": "",
                    "partyName": "",
                    "operatorName": "",
                    "supervisorName": "",
                    'batchOrGrade': "",
                    "testingTime": '',
                    "testName": "Rolling QC",
                    "testIngridentUoM": unit_list[i],  # Use the corresponding unit from the list
                    "testIngrident": testIngrident[i],  # Use the corresponding testIngrident value from the list
                    "uperLimit": 0,
                    "standard": 0,
                    "lowerLimit": 0,
                    "testReport": float(line_elements[0]),
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

    json_output = json.dumps(output_data_list, indent=4)
    return json_output



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

    google_folder_link = "https://drive.google.com/drive/folders/1lpzxuRIMab4JSayOMIlC9MGZ7U98l2zB?usp=drive_link"
    gdown.download_folder(google_folder_link)
    print("Folder downloaded")

    folder_path = 'Rolling QC'
    processed_files = get_processed_files()

    for file in os.listdir(folder_path):
        if file.endswith('.pdf') and file not in processed_files:
            pdf_path = os.path.join(folder_path, file)
            print("Processing PDF file:", pdf_path)
            json_output = process_pdf(pdf_path)  # Get json_output from the function
            print(json_output)

            # api_url = "https://deverp.ibos.io/mes/QCTest/CreateAllUnitSQcData"
            api_url = "https://erp.ibos.io/mes/QCTest/CreateAllUnitSQcData"
            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(api_url, data=json_output, headers=headers)

            if response.status_code == 200:
                print("POST request successful")
                add_to_processed_files(file)  # Add the processed file to the tracking file
            else:
                print(f"POST request failed with status code {response.status_code}")
                print(response.text)

            sleep(5)