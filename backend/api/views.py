from django.http import JsonResponse
import json
import requests
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
headers_post = {
    "Authorization": "Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz",
    "Content-Type": "application/json" 
}

url_get_info = "https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active"
url_login = "https://api.baubuddy.de/index.php/login"
payload = {
    "username": "365",
    "password": "1"
}

def get_info_from_baubuddy(url, headers):
    response = requests.request("GET", url, headers=headers)
    return JsonResponse(response)

@csrf_exempt
def api_csv(request, *args, **kwargs):
    body = request.body
    data = {}
    if body != None:

        csv_data = json.loads(json.loads(body))  # string of json data -> py dict
      
        # TODO: Get all info 
        headers_get = {
            "Content-Type": "application/json"
        }
                    
        login_ = requests.request("POST", url_login, json=payload, headers=headers_post)
        login_ = login_.json()
        access_token = login_['oauth']['access_token']
        headers_get['Authorization']=  f"Bearer {access_token}"
        
        get_all_info = requests.request("GET", url=url_get_info, headers=headers_get)
        get_all_info = get_all_info.json()        
        filtered_info = list(filter(lambda x: x.get('hu') != None, get_all_info))
        
        merged_data = {}
        merged_data['body'] = []
        
        for i in filtered_info:
            merged_dict = None
            matched = 0
            for j in csv_data:  
                if i['kurzname'] == j['kurzname']:
                    merged_dict = {**j, **i}
                    matched += 1
                    if(i['gruppe'] != j['gruppe']):
                        merged_dict['gruppe'] = ' '.join(sorted(f"{j['gruppe']} {i['gruppe']}".split())).replace(' ', ', ')
                    csv_data.remove(j)    
                    break
           
            if merged_dict == None:
                merged_dict = i
            colorCodes = []
            if merged_dict['labelIds'] != '' and merged_dict['labelIds'] != 'None' and merged_dict['labelIds'] != None:
                labelids = merged_dict['labelIds'].split(",")
                for k in labelids:
                    colorcode = requests.request("GET", url=f"https://api.baubuddy.de/dev/index.php/v1/labels/{k}", headers=headers_get)
                    colorcode = colorcode.json()
                  
                    colorCodes.append(colorcode[0]['colorCode'])
            
            merged_dict['colorCode'] = ' '.join(filter(lambda x: len(x) != 0, colorCodes))
            merged_data['body'].append(merged_dict)   
        
        return JsonResponse(merged_data)
    return JsonResponse({'message': 'must give body to request'})