import requests as rq
import os
import json
import time



class ApiResult():
    def result(self,data):
        if data.status_code == 200:
            return data.json()
        elif data.status_code == 401:
            raise Exception("Not authorized")
        elif data.status_code == 400:
            raise Exception("Wrong data was sent\n"+str(data.content))
        elif data.status_code == 403:
            raise Exception("Have not enought permissions")
        else:
            raise Exception("status code  " + str(data.status_code) + '\n' + str(data.content))


class AmoGetAccess():
    def __init__(self, file_name: str, base_URL: str, access_data:dict) -> None:
        self._filename = file_name
        self._base_URL = base_URL


        if not os.path.isfile(self._filename):
            self.get_access_tokens(self._filename, access_data)

        with open(file_name, 'r', encoding='UTF-8') as f:
            data = json.load(f)

        self._acc_token = data['access_token']
        self._ref_token = data['refresh_token']

        if self.get_user_data() == "Not authorized":

            access_data["grant_type"] = "refresh_token"
            access_data["refresh_token"] = self.refresh_token
            del access_data["code"]

            self.get_access_tokens(self._filename, access_data)

            with open(self._filename, 'r', encoding='UTF-8') as f:
                data = json.load(f)

            self._acc_token = data['access_token']
            self._ref_token = data['refresh_token']   


    
    @property
    def access_token(self)->str:
        return self._acc_token

    @property
    def refresh_token(self)->str:
        return self._ref_token

    def get_access_tokens(self, file_name:str, js:dict):
        """  requests access token and refresh token from AmoCRM and dumps them to file  """
        resp = rq.request('POST',f'{self._base_URL}/oauth2/access_token', json=js)

        data = resp.json()
        if resp.status_code > 204:
            raise Exception(data)

        with open(file_name, 'w', encoding='UTF-8') as f:
            json.dump(data,f)


            
    def get_user_data(self):
        headers = { 'Authorization': f'Bearer {self.access_token}' }
        resp = rq.request('GET',f'{self._base_URL}/api/v4/account',headers = headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            return "Not authorized"

class AmoPipeline():
    def __init__(self, token:str, base_URL:str) -> None:
        self._acc_token = token
        self._base_URL = base_URL


    @property
    def access_token(self)->str:
        return self._acc_token

    def get_all_pipelines(self):
        headers = { 'Authorization': f'Bearer {self.access_token}' }
        resp = rq.request('GET',f'{self._base_URL}/api/v4/leads/pipelines',headers = headers)     
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception("Not authorized")

    def get_data_by_id(self, id:int)->str:
        headers = { 'Authorization': f'Bearer {self.access_token}' }
        resp = rq.request('GET',f'{self._base_URL}/api/v4/leads/pipelines/{id}',headers = headers)     
        if resp.status_code == 200:
            return resp.json()
        else:
            return "Not authorized"        

    def get_id_by_name(self,name:str)->int:
        for it in self.get_all_pipelines()['_embedded']['pipelines']:
            if it['name'] == name:
                return int(it['id'])

    def add_pipeline(self, data:list)->str:
        headers = { 'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': "application/json" }
        resp = rq.request('POST',f'{self._base_URL}/api/v4/leads/pipelines', json=data, headers=headers )    
        return ApiResult().result(resp) 
        
    def del_pipeline(self, id:int)->str:
        headers = { 'Authorization': f'Bearer {self.access_token}' }
        resp = rq.request('DELETE',f'{self._base_URL}/api/v4/leads/pipelines/{id}',headers = headers)   
        return ApiResult().result(resp) 

    def add_stage(self,pipeline_id,data:dict)->str:
        """ adds stage to pipeline """
        headers = { 'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': "application/json" }
        resp = rq.request('POST',f'{self._base_URL}/api/v4/leads/pipelines/{pipeline_id}/statuses', json=data, headers=headers )    
        return ApiResult().result(resp)
    
    def get_stages(self,pipeline_id)->str:
        """ returns all stages """
        headers = { 'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': "application/json" }
        resp = rq.request('GET',f'{self._base_URL}/api/v4/leads/pipelines/{pipeline_id}/statuses', headers=headers )    
        return ApiResult().result(resp)         

class AmoLead():
    def __init__(self, token:str, base_URL:str) -> None:
        self._acc_token = token
        self._base_URL = base_URL


    @property
    def access_token(self)->str:
        return self._acc_token

    def add_lead(self, data:list)->int:
        """ adds new lead and returns its id """
        headers = { 'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': "application/json" }
        resp = rq.request('POST',f'{self._base_URL}/api/v4/leads', json=data, headers=headers )    
        return ApiResult().result(resp) 

    def get_all_leads(self)->str:
        """ returns all leads by user """
        headers = { 'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': "application/json" }
        resp = rq.request('GET',f'{self._base_URL}/api/v4/leads', headers=headers )    
        return ApiResult().result(resp) 

    def get_lead_by_id(self, id:int)->str:
        """ returns lead by id """
        headers = { 'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': "application/json" }
        resp = rq.request('GET',f'{self._base_URL}/api/v4/leads/{id}', headers=headers )    
        return ApiResult().result(resp) 

    def get_id_by_name(self,name:str)->int:
        p = self.get_all_leads()
        item = p['_embedded']['leads']
        for it in item:
            if it['name'] == name:
                return int(it['id'])

    def add_custom_fields(self, fields:list):
        """ adds custom fields to lead """
        headers = { 'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': "application/json" }
        resp = rq.request('POST',f'{self._base_URL}/api/v4/leads/custom_fields',json=fields, headers=headers )    
        return ApiResult().result(resp) 

    def del_custom_fields(self,id)->str:
        """ deletes custom field by custom field id """
        headers = { 'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': "application/json" }
        resp = rq.request('DELETE',f'{self._base_URL}/api/v4/leads/custom_fields/{id}', headers=headers )    
        return ApiResult().result(resp) 

    def get_custom_fields(self):
        """ returns custom fields to lead """
        headers = { 'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': "application/json" }
        resp = rq.request('GET',f'{self._base_URL}/api/v4/leads/custom_fields', headers=headers )    
        return ApiResult().result(resp)         

    # def add_client_data(self, id:int, cl_data:list)->str:
    #     """ adds client data to lead """
    #     headers = { 'Authorization': f'Bearer {self.access_token}',
    #                 'Content-Type': "application/json" }
    #     resp = rq.request('PATCH', f'{self._base_URL}/api/v4/leads/{id}', json=cl_data, headers=headers )    
    #     return ApiResult().result(resp)         


class AmoContact():
    def __init__(self, token:str, base_URL:str) -> None:
        self._acc_token = token
        self._base_URL = base_URL

    @property
    def access_token(self)->str:
        return self._acc_token

    def add_contact(self,data:dict)->str:
        """ returns id of created contact """
        headers = { 'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': "application/json" }
        resp = rq.request('POST',f'{self._base_URL}/api/v4/contacts',json=data, headers=headers )  
        return ApiResult().result(resp)         

    def find_contact(self, phone:str)->str:
        """ returns id by contact phone """
        headers = { 'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': "application/json" }
        resp = rq.request('GET',f'{self._base_URL}/api/v4/contacts?query={phone}', headers=headers)
        return ApiResult().result(resp)





file_name = os.path.join(os.path.expanduser('~'),'.amo_api')
base_URL = 'https://zauraznaurov.amocrm.com'

access_data = {  "client_id": "51f8e028-6bdb-4875-8427-845d33bb6c53",
            "client_secret": "OJm06q11MOnLMyGMfenQ3iBULKcnmdt9pEnbvkZwA2658gbP293XdkPLcp1KSMiQ",
            "grant_type": "authorization_code",
            "code": "def50200e8e64336c7f02710a10192318aae87b20c6d66ce484d59ed8f57eb3f9f38bbff6efd338159622b8b4e385738e0b3df2ea625d21862e16b5f32f272ee93c3cf32a5388ed312a2f9f73d9f96cce5d6b132b149caad4ebaeeb8ab747ee99c17388830d25a97363f9ea6b4ea02b6f2ab8189beb4c00211fc4420d65e35e00830239544391afb37589e0eba5ede7b32e0b8b1a7ea06c7ccf59c9c2a2ba509c65bcce721b7a6ad480a04ed832c3c9e948559a8ea65dfbd38726784dec4e72a1948e63c8d88b70498373a3e2ca25733032768647bfebc31b2f439fc11e09fc2e8a66c8533f71174d17287eef2c8355d581619492628a8c9726533d5f347e7f1e03342868e0983e76d6b22e1dc32abca73596b8194445d384b214310283738a9fabfcdb1b7ba2a1960f369f36a1491429a0cfec56cff9dc54b39c704c33c31bd295c0f0f54f7c7d7d49288aa76611682f68b03e60e2ded7222746a900afdfd2a2989d6923ba93c0d8d5ad75c6c3340afbc8d60a91c79315095536965c242d9fa7164f1a818d2b216c814cbcf850e5fa916bfa433d5be06353313081b4a2b8458104115800fad9d5e9ace41ccbd71d2bf1f4f325810ff5845351ae5f582a7d47d05a1326236474641b4",
            "redirect_uri": "https://zauraznaurov.amocrm.com"
        }



if __name__ == '__main__':

    new_pipeline = [{
        "name": "Cleaning orders",
        "is_main": False,
        "is_unsorted_on": True,
        "sort": 30,
        "request_id": "543",
        "_embedded": {
            "statuses": [
                {
                    "name": "Incoming leads",
                    "sort": 10, 
                    "is_editable": False, 
                    "color": "#e6e8ea", 
                    "type": 1
                },
                {
                    "name": "Initial contact", 
                    "sort": 20, 
                    "is_editable": True, 
                    "color": "#98cbff", 
                    "type": 0
                },
                {
                    "name": "Discussions", 
                    "sort": 30, 
                    "is_editable": True, 
                    "color": "#fffd7f", 
                    "type": 0
                },
                {
                    "name": "Decision making", 
                    "sort": 40, 
                    "is_editable": True, 
                    "color": "#ffdc7f", 
                    "type": 0
                },
                {
                    "name": "Contract discussion", 
                    "sort": 50, 
                    "is_editable": True, 
                    "color": "#ffdbdb", 
                    "type": 0
                },
                {
                    "id": 142,
                    "name": "Closed - won", 
                    "sort": 9999, 
                    "is_editable": False,
                    "color": "#deff81", 
                    "type": 0
                },
                {
                    "id": 143,
                    "name": "Closed - lost",
                    "sort": 10000, 
                    "is_editable": False,
                    "color": "#ccc8f9", 
                    "type": 0
                }
            ]
        }
    }]

    new_empty_lead =[
        {
        "name": "Lead num.1",
        "created_by": 0,
        "pipeline_id":4487269,
        "created_at": int(time.time())

    }
    ]




    amo = AmoGetAccess(file_name, base_URL, access_data)

    pipelines = AmoPipeline(amo.access_token, base_URL)

#create new pipeline
    # pipeline_id = pipelines.add_pipeline(new_pipeline)['_embedded']['pipelines'][0]['id']
    # time.sleep(10)
    pipeline_id = 4490965
    for item in pipelines.get_stages(pipeline_id)['_embedded']['statuses']:
        if item['name'] == 'Incoming leads':
            status_id = item['id']

    # https://zauraznaurov.amocrm.com/api/v4/leads/pipelines/4489960/statuses
# create custom fields in leads
    custom_fields = [
        {
            "name": "work address",
            "type": "streetaddress",
            "sort": 511,
            "required_statuses": [
                {
                    "pipeline_id": pipeline_id ,
                    "status_id": status_id
                }
            ]

        },
        {
            "name": "work date and time",
            "type": "date_time",
            "sort": 512,
            "required_statuses": [
                {
                    "pipeline_id":pipeline_id ,
                    "status_id": status_id
                }
            ]

        },        
        {
            "name": "comments",
            "type": "textarea",
            "sort": 513,

        },        
        {
            "name": "Cleaning types",
            "type": "multiselect",
            "sort": 510,
            "required_statuses": [
                {
                    "pipeline_id":pipeline_id,
                    "status_id": status_id
                }
            ],
            "enums": [
                {
                    "value": "mopping (cost 1$/sq feet)",
                    "sort": 1
                },
                {
                    "value": "washing windows (cost 2$/sq feet)",
                    "sort": 2
                },
                {
                    "value": "washing tableware (cost 0.5$/per item)",
                    "sort": 3
                },
                {
                    "value": "dust off the ceiling (cost 1$/sq feet)",
                    "sort": 4
                },
                {
                    "value": "vacuum or wash the walls (cost 1$/sq feet)",
                    "sort": 5
                }
            ]
        }
    ]

    leads = AmoLead(amo.access_token,base_URL)
    # leads.add_custom_fields(custom_fields)

# add 10 test leads with client info
    # contact = AmoClient(amo.access_token, base_URL)

    # for i in range(10):
    #     num = str(i+20)
    #     f_name = "First_name " + num
    #     l_name = "Last name " + num
    #     email = "test-email-"+ num+"@test.com"
    #     phone = "+"+num*5
    #     contact_data = [    {
    #         "first_name": f"{f_name}",
    #         "last_name": f"{l_name}",
    #         "created_at":int(time.time()),
    #         "responsible_user_id":0,
    #         "custom_fields_values": [
    #                     {
    #                      "field_code":"EMAIL",
    #                      "values":[
    #                         {
    #                             "enum_code":"WORK",
    #                             "value":f"{email}"
    #                         }
    #                     ]
    #                     },
    #                     {
    #                         "field_code":"PHONE",
    #                         "values":[
    #                         {
    #                             "enum_code":"WORK",
    #                             "value":f"{phone}"
    #                         }
    #                     ]
    #                     }

    #             ]
    #         }
    #     ]
    #     contact_id = contact.add_contact(contact_data)['_embedded']['contacts'][0]['id']
    #     time.sleep(10)
    #     price = i*22
        # lead_data=[{      
        #     "name": f"Lead num.{num}",
        #     "created_by": 0,
        #     "pipeline_id":pipeline_id,
        #     "created_at": int(time.time()),
        #     "price": price,
        #     "_embedded":{
        #             "contacts":[{
        #                 "id":contact_id
        #             }]
        #     }
        # }]

    #     leads.add_lead(lead_data)


# Create a few lead stages for business processes in a small cleaning company
    # for i in range(3):
    #     num = str(i)  
    #     stage_name = "Stage "+ num
    #     sort_idx = i
    #     stage_color = ('#fff000','#98cbff','#eb93ff')[i%3]
    #     stage = [
    #     {
    #         "name": f"{stage_name}",
    #         "sort": 100+sort_idx,
    #         "color": f"{stage_color}"
    #     },
    #     ]
    #     pipelines.add_stage(pipeline_id,stage)

# Add 2 users    



