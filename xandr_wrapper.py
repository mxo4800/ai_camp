import requests
from requests.exceptions import RequestException
import logging
import json

class XandrAPI:
    def __init__(self, username, password, base_url="https://api.appnexus.com"):
        
        self.session = requests.Session()
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None

    def connect(self):
        auth_url = f"{self.base_url}/auth"
        auth_payload = {
            "auth": {
                "username": self.username,
                "password": self.password
            }
        }
        try:
            response = self.session.post(auth_url, json=auth_payload)
            response.raise_for_status()  # This will raise an exception for 4XX and 5XX responses
            self.token = response.json()["response"]["token"]
            self.session.headers.update({'Authorization': self.token})
        except RequestException as e:
            # Log the exception; e.g., print or use a logging framework
            print(f"Failed to connect to Xandr API: {e}")
        except KeyError:
            print("Unexpected response format received from authentication service.")

    # Example of a method making an authenticated API call
    def get_some_resource(self, resource_endpoint):
        try:
            response = self.session.get(f"{self.base_url}/{resource_endpoint}")
            response.raise_for_status()
            return response.json()  # Or handle the response appropriately
        except RequestException as e:
            print(f"Failed to retrieve resource {resource_endpoint}: {e}")
            return None
        

    

class AdvertiserReportAPI:

    def __init__(self, xandr_api: XandrAPI):

        self.xandr_api = xandr_api
        self.url = f"{self.xandr_api.base_url}/report"


    
    def submit_report(self, json_file, advertiser_id):

        url = f"{self.url}?advertiser_id={advertiser_id}"

        response = self.xandr_api.session.post(url, json=json_file)
        
        return response.json()
    

    def download_report(self, report_id):

        # check if report is ready

        report_status = self.check_report_status(report_id=report_id)

        if report_status["response"]['execution_status'] == 'ready':

            url = f"{self.url}-download?id={report_id}"
            response = self.xandr_api.session.get(url)

            return response.content

    def check_report_status(self, report_id):

        url = f"{self.url}?id={report_id}"
        response = self.xandr_api.session.get(url)

        return response.json()
    

class SegmentAPI:

    def __init__(self, xandr_api: XandrAPI):

        self.xandr_api = xandr_api
        self.url = f"{self.xandr_api.base_url}/segment"


    
    def get_segment(self, start_element=0):

        url = f"{self.url}?start_element={start_element}"
        response = self.xandr_api.session.get(url)

        return response
    

class AdvertiserAPI:

    def __init__(self, xandr_api: XandrAPI):

        self.xandr_api = xandr_api
        self.url = f"{self.xandr_api.base_url}/advertiser"

    def get_advertiser(self, advertiser_id):

        url = f"{self.url}?id={advertiser_id}"
        response = self.xandr_api.session.get(url)

        return response
    
    def get_advertiser_name(self, advertiser_id):

        advertiser = self.get_advertiser(advertiser_id=advertiser_id)

        return advertiser.json()["response"]["advertiser"]["name"]

class ProfileAPI:

    def __init__(self, xandr_api: XandrAPI):

        self.xandr_api = xandr_api
        self.url = f"{self.xandr_api.base_url}/profile"    


    def get_profile_item(self, advertiser_id, profile_id, member_id=668):

        url = f"{self.url}?id={profile_id}&advertiser_id={advertiser_id}&member_id={member_id}"
        response = self.xandr_api.session.get(url)

        return response
    
    def create_profile_item(self, advertiser_id, profile_json, member_id=668):


        url = f"{self.url}?advertiser_id={advertiser_id}&member_id={member_id}"

        response = self.xandr_api.session.post(url=url, json=profile_json)

        return response




    

class InsertionOrderAPI:

    def __init__(self, xandr_api: XandrAPI):

        self.xandr_api = xandr_api
        self.url = f"{self.xandr_api.base_url}/insertion-order"


    def get_insertion_order(self, insertion_order_id):

        url = f"{self.url}?id={insertion_order_id}"

        response = self.xandr_api.session.get(url)

        return response.json()["response"]["insertion-order"]
    

    def get_profile_id(self, insertion_order_id):

        response = self.get_insertion_order(insertion_order_id=insertion_order_id)

        profile_id = response.json()['response']['insertion-order']['profile_id']

        return profile_id
    
    def create_insertion_order(self, advertiser_id, insertion_order_name, insertion_order_template):

        insertion_order_template["insertion-order"]["name"] = insertion_order_name
        insertion_order_template["insertion-order"]["advertiser_id"] = advertiser_id

        
        url = f"{self.url}?advertiser_id={advertiser_id}"

        response = self.xandr_api.session.post(url, json=insertion_order_template)

        return response.json()["response"]["insertion-order"]


        
class LineItemAPI:

    def __init__(self, xandr_api: XandrAPI):

        self.xandr_api = xandr_api
        self.url = f"{self.xandr_api.base_url}/line-item" 


    def get_line_item(self, line_item_id):

        url = f"{self.url}?id={line_item_id}"

        response = self.xandr_api.session.get(url)

        return response
    
    def get_profile_id(self, line_item_id):

        response = self.get_line_item(line_item_id)

        profile_id = response.json()['response']['line-item']['profile_id']

        return profile_id
    
    def create_line_item(self, advertiser_name, line_item_template, insertion_order, profile_item):


        profile_id = profile_item.json()["response"]["profile"]["id"]
        advertiser_id = insertion_order['advertiser_id']
        start_date = insertion_order["budget_intervals"][0]["start_date"]
        end_date = insertion_order["budget_intervals"][0]["end_date"]

        line_item_template["line-item"]["advertiser_id"] = advertiser_id
        line_item_template["line-item"]["profile_id"] = profile_id
        line_item_template["line-item"]["advertiser"]["id"] = advertiser_id
        line_item_template["line-item"]["advertiser"]["name"] = advertiser_name
        line_item_template["line-item"]["budget_intervals"][0]["start_date"] = start_date
        line_item_template["line-item"]["budget_intervals"][0]["end_date"] = end_date

        for key in line_item_template["line-item"]["insertion_orders"][0].keys():

            if key in insertion_order.keys():

                line_item_template["line-item"]["insertion_orders"][0][key] = insertion_order[key]


        

        url = f"{self.url}?&advertiser_id={insertion_order["advertiser_id"]}"

        response = self.xandr_api.session.post(url, json=line_item_template)

        return response

        



