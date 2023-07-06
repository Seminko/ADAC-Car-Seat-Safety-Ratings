from datetime import datetime
from tqdm import tqdm
import pandas as pd
import requests
import json
import time
import re

def get_json(response):
    response_text = response.text
    match = re.search("(?<=window\.__APOLLO_STATE__=)\{[^\}]+.*?\}(?=;<\/script)", response_text)
    o_json_text = match[0]
    o_json = json.loads(o_json_text)
    
    return o_json

def get_max_pages(response):
    response_text = response.text
    pagination_match = re.search('totalPages":\s*(\d+)', response_text)
    max_pages = pagination_match[1]
    max_pages = int(max_pages)
    
    return max_pages

def get_page(url):
    response = requests.get(url, timeout=15)
    if not response:
        raise Exception("Invalid response")
    if response.status_code != 200:
        raise Exception(f"Invalid status_code: {response.status_code}")
        
    return response

def get_and_process_page(url, page_number=None, get_max_pages_bool=False):
    if page_number:
        url = url.format(page_number=page_number)
    response = get_page(url)
    o_json = get_json(response)
    
    if get_max_pages_bool:
        max_pages = get_max_pages(response)
        return max_pages, o_json
    
    return o_json

def get_urls():
    url = "https://www.adac.de/rund-ums-fahrzeug/ausstattung-technik-zubehoer/kindersitze/kindersitztest/?isofix=false&resultCount=10&pageNumber={page_number}&showLegacyChildSeats=true&rating.max=5.5&sort=RECENT_FIRST"
    
    product_url_dicts = []
    page_number = 1
    max_pages, result = get_and_process_page(url, page_number, get_max_pages_bool=True)
    product_url_dicts.append(result)
    time.sleep(1)
    pbar = tqdm(range(2, max_pages+1), initial=1, total=max_pages)
    for page_number in pbar:
        pbar.set_description(f"There are {max_pages} pages to be scraped. Scraping page %s" % page_number)
        result = get_and_process_page(url, page_number)
        product_url_dicts.append(result)
        
    return product_url_dicts
    
def process_url_dicts(product_urls_dicts):
    product_urls = [
        f'https://www.adac.de/rund-ums-fahrzeug/ausstattung-technik-zubehoer/kindersitze/kindersitztest/marken/{value["brandSlug"]}/{value["slug"]}'
        for o_json in product_urls_dicts
        for key, value in o_json.items()
        if key in [
            key
            for key in o_json.keys()
            if key.lower().startswith('childseattestsearchitem')
        ]
    ]

    return list(set(product_urls))

def get_products(product_urls):
    time.sleep(1)
    product_dicts = []
    pbar = tqdm(product_urls)
    for idx, product_url in enumerate(pbar):
        pbar.set_description(f"There are {len(product_urls)} products to be scraped. Scraping URL %s" % idx)
        o_json = get_and_process_page(product_url)
        product_dicts.append(o_json)
        
    return product_dicts

def process_product_dicts(product_dicts, export_to_excel=True):
    col_formatting = [
        {'col_name': 'Name', 'col_width': 35},
        {'col_name': 'URL', 'col_width': 20},
        {'col_name': 'Brand', 'col_width': 20},
        {'col_name': 'Model', 'col_width': 20},
        {'col_name': 'Description', 'col_width': 20},
        {'col_name': 'Summary', 'col_width': 20},
        {'col_name': 'Price', 'col_width': 10},
        {'col_name': 'Test Year', 'col_width': 13},
        {'col_name': 'Current', 'col_width': 11},
        {'col_name': 'Full Rating', 'col_width': 15},
        {'col_name': 'Security Rating', 'col_width': 19},
        {'col_name': 'Security Strengths', 'col_width': 25},
        {'col_name': 'Security Weaknesses', 'col_width': 25},
        {'col_name': 'Operation Rating', 'col_width': 19},
        {'col_name': 'Operation Strengths', 'col_width': 25},
        {'col_name': 'Operation Weaknesses', 'col_width': 25},
        {'col_name': 'Ergonomy Rating', 'col_width': 19},
        {'col_name': 'Ergonomy Strengths', 'col_width': 25},
        {'col_name': 'Ergonomy Weaknesses', 'col_width': 25},
        {'col_name': 'Pollutants Rating', 'col_width': 19},
        {'col_name': 'Pollutants Strengths', 'col_width': 25},
        {'col_name': 'Pollutants Weaknesses', 'col_width': 25},
        {'col_name': 'Processing and Cleaning Rating', 'col_width': 19},
        {'col_name': 'Processing and Cleaning Strengths', 'col_width': 25},
        {'col_name': 'Processing and Cleaning Weaknesses', 'col_width': 25},
        {'col_name': 'Age Class', 'col_width': 20},
        {'col_name': 'Approved Child Weight', 'col_width': 26},
        {'col_name': 'Child Height From', 'col_width': 21},
        {'col_name': 'Child Height To', 'col_width': 19},
        {'col_name': 'Backward Facing Option', 'col_width': 27},
        {'col_name': 'Forward Facing Option', 'col_width': 25},
        {'col_name': 'Horizontal Transport', 'col_width': 24},
        {'col_name': 'Isofix', 'col_width': 11},
        {'col_name': 'Impact Shield', 'col_width': 17},
        {'col_name': 'Two-point Belt', 'col_width': 19},
        {'col_name': 'Seat Weight', 'col_width': 16},
        {'col_name': 'Montage Notes', 'col_width': 20},
    ]
    
    products = [
        value
        for o_json in product_dicts
        for key, value in o_json.items()
        if key in [
            key
            for key in o_json.keys()
            if key.lower().startswith('apilchildseat')
        ]
    ]
    
    final_list = []
    for product in products:
        obj = {}
        obj["Name"] = product["childSeatFullName"]
        obj["URL"] = f'https://www.adac.de/rund-ums-fahrzeug/ausstattung-technik-zubehoer/kindersitze/kindersitztest/marken/{product["brandSlug"]}/{product["slug"]}'
        obj["Brand"] = product["manufacturer"]
        obj["Model"] = product["model"]
        obj["Description"] = "\n".join(product["sanitizedDescription"])
        obj["Summary"] = product["sanitizedSummary"]
        obj["Price"] = product["price"]
        obj["Test Year"] = product["testYear"]
        obj["Current"] = product["current"]
        obj["Full Rating"] = product["rating"]
        
        security_dict = next((dct for dct in product["ratings"] if dct["category"] == "Sicherheit"), None)
        if security_dict:
            obj["Security Rating"] = security_dict["rating"]
            obj["Security Strengths"] = "\n".join(security_dict["strengths"])
            obj["Security Weaknesses"] = "\n".join(security_dict["weaknesses"])
        
        operation_dict = next((dct for dct in product["ratings"] if dct["category"] == "Bedienung"), None)
        if operation_dict:
            obj["Operation Rating"] = operation_dict["rating"]
            obj["Operation Strengths"] = "\n".join(operation_dict["strengths"])
            obj["Operation Weaknesses"] = "\n".join(operation_dict["weaknesses"])
        
        ergonomy_dict = next((dct for dct in product["ratings"] if dct["category"] == "Ergonomie"), None)
        if ergonomy_dict:
            obj["Ergonomy Rating"] = ergonomy_dict["rating"]
            obj["Ergonomy Strengths"] = "\n".join(ergonomy_dict["strengths"])
            obj["Ergonomy Weaknesses"] = "\n".join(ergonomy_dict["weaknesses"])
        
        pollutants_dict = next((dct for dct in product["ratings"] if dct["category"] == "Schadstoffe"), None)
        if pollutants_dict:
            obj["Pollutants Rating"] = pollutants_dict["rating"]
            obj["Pollutants Strengths"] = "\n".join(pollutants_dict["strengths"])
            obj["Pollutants Weaknesses"] = "\n".join(pollutants_dict["weaknesses"])
        
        processing_and_cleaning_dict = next((dct for dct in product["ratings"] if dct["category"] == "Verarbeitung und Reinigung"), None)
        if processing_and_cleaning_dict:
            obj["Processing and Cleaning Rating"] = processing_and_cleaning_dict["rating"]
            obj["Processing and Cleaning Strengths"] = "\n".join(processing_and_cleaning_dict["strengths"])
            obj["Processing and Cleaning Weaknesses"] = "\n".join(processing_and_cleaning_dict["weaknesses"])
        
        obj["Age Class"] = product["data"]["ageClass"]
        obj["Approved Child Weight"] = product["data"]["approvedChildWeight"]
        obj["Child Height From"] = product["data"]["dimensionsFrom"]
        obj["Child Height To"] = product["data"]["dimensionsTo"]
        obj["Backward Facing Option"] = product["data"]["backwardFacingOption"]
        obj["Forward Facing Option"] = product["data"]["forwardFacingOption"]
        obj["Horizontal Transport"] = product["data"]["horizontalTransport"]
        obj["Isofix"] = product["data"]["isoFix"]
        obj["Impact Shield"] = product["data"]["body"]
        obj["Two-point Belt"] = product["data"]["twoPointBelt"]
        obj["Seat Weight"] = product["data"]["seatWeight"]
        obj["Montage Notes"] = "\n".join(product["data"]["sanitizedInstallation"])
        
        final_list.append(obj)
        
    df = pd.DataFrame(final_list, columns=[c["col_name"] for c in col_formatting])
    
    if export_to_excel:
        writer = pd.ExcelWriter(f'adac_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                                engine='xlsxwriter',
                                engine_kwargs={
                                    'options': {
                                        'strings_to_numbers': True,
                                        'strings_to_urls': False,
                                        }
                                    }
                                )
        
        df.to_excel(writer, sheet_name="Data", index=False)
        worksheet = writer.sheets["Data"]
        worksheet.autofilter(0, 0, df.shape[0], df.shape[1]-1)
        
        for idx, col in enumerate(df.columns):
            column_format_dict = next(c for c in col_formatting if c["col_name"] == col)
            worksheet.set_column(idx, idx, column_format_dict["col_width"])  # set column width
        
        writer.close()
        
    return df

if __name__ == "__main__":
    product_url_dicts = get_urls()
    product_urls = process_url_dicts(product_url_dicts)
    
    product_dicts = get_products(product_urls)
    df = process_product_dicts(product_dicts, export_to_excel=True)
