import requests
import json 
import os
import datetime
import time

# Define functions for repeated tasks

def get_login_response(username, password):
    """Authenticate the user and return the API response"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    url = 'https://dm-ap.informaticacloud.com/saas/public/core/v3/login'
    data = {'username': username, 'password': password}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.json()

def get_tagged_mappings(baseApiUrl, sesh_id, tag):
    """Return a list of mappings with the specified tag"""
    url = f"{baseApiUrl}/public/core/v3/objects?q=tag=='{tag}'"
    response = requests.get(url, headers={'INFA-SESSION-ID': sesh_id})
    return response.json()

def export_mappings(baseApiUrl, sesh_id, export_data):
    """Export the mappings specified in the export_data payload"""
    payload = json.dumps(export_data)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'INFA-SESSION-ID': sesh_id
    }
    response = requests.post(f"{baseApiUrl}/public/core/v3/export", headers=headers, data=payload)
    return response.json()['id']

def get_export_status(baseApiUrl, sesh_id, export_job_id):
    """Return the export status of the specified job"""
    url = f"{baseApiUrl}/public/core/v3/export/{export_job_id}"
    response = requests.get(url, headers={'INFA-SESSION-ID': sesh_id}, data={})
    return response.json()

def export_download(export_job_id):
    headers={
        'Content-Type': 'application/zip',
        'Accept': 'application/zip',
        'INFA-SESSION-ID': src_sesh_id
    }

    download_url=f"{src_baseApiUrl}/public/core/v3/export/{export_job_id}/package"

    export_download_response=requests.get(download_url,headers= headers)
    export_zip_file_name= f"{export_job_id}_{current_date}_{current_time}.zip"
    file_path=os.path.join(output_dir,export_zip_file_name)
    with open(file_path, "wb") as f:    
        f.write(export_download_response.content)
    time.sleep(5)
    return export_zip_file_name

def upload_import_job(export_zip_file_name,file_path):
    payload={}
    headers_imp1= {
        'Accept': 'application/json',
        'INFA-SESSION-ID': tgt_sesh_id
    }

    files=[
    ('package',(export_zip_file_name,open(file_path,'rb'),'application/zip'))
    ]

    import_url=f"{tgt_baseApiUrl}/public/core/v3/import/package"
    import_response=requests.post(import_url, headers=headers_imp1,data=payload,files=files)
    
    print(f"import response= {import_response}")
    import_json=import_response.json() #fetch jobid of the import job
    print("import_json",import_json)
    return import_json['jobId']
    

def import_status(import_jobId):
    payload={}

    import_status_url=f"{tgt_baseApiUrl}/public/core/v3/import/{import_jobId}"
    import_status_response=requests.get(import_status_url,headers=headers_import_status,data=payload)
    print(f"import status response is = {import_status_response}")

    import_status=import_status_response.json()

    return import_status ['name']

def initiate_import_job(import_job_name):
    payload = json.dumps({
        "name": f"{import_job_name}"
    })
    import_job_response=requests.post(f"{tgt_baseApiUrl}/public/core/v3/import/{import_jobId}",headers= headers_import_status,data=payload)

    print(f"import job response= {import_job_response}")
    time.sleep(10)
    
def tagging():
    tgt_tag_url=f"{tgt_baseApiUrl}/public/core/v3/TagObjects"
    import_jobs_data=[]

    headers_tag = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'INFA-SESSION-ID': tgt_sesh_id
    }
    for key , value in id_tag_mapping.items():
        tag_data={
            "id":value['id'],
            "tags": value ['tag']
        }
        import_jobs_data.append(tag_data)

    # print("import jobs data:")
    # print(import_jobs_data)

    tag_response = requests.post(tgt_tag_url, headers=headers_tag, json=import_jobs_data)
    print(f"tag response= {tag_response}")


# Define inputs

current_date = datetime.date.today()
indian_current_date = current_date.strftime("%d-%m-%Y")
current_time = datetime.datetime.now().strftime("%I-%M_%p")

source_user = 'anishhdp2'
source_password = 'Anidatap@12345'
target_user = 'dummyuser123'
target_password = 'qwerty@12345'



# Authenticate users

src_login_response = get_login_response(source_user, source_password)
tgt_login_response = get_login_response(target_user, target_password)
#getting api url
src_baseApiUrl = src_login_response['products'][0]['baseApiUrl']
tgt_baseApiUrl = tgt_login_response['products'][0]['baseApiUrl']
#fetch session id
src_sesh_id = src_login_response['userInfo']['sessionId']
tgt_sesh_id = tgt_login_response['userInfo']['sessionId']

# Define constants
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

output_dir='D:\IICS_content\exported' 

headers_import_status = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'INFA-SESSION-ID': tgt_sesh_id
    }

# Get list of mappings with tags from source user

src_mappings_url = f"{src_baseApiUrl}/public/core/v3/objects?q=location=='Default'"
src_mappings_response = requests.get(src_mappings_url, headers={'INFA-SESSION-ID': src_sesh_id})
src_mappings = src_mappings_response.json()

src_tag_list = list(set([tag for tags in [tag['tags'] for tag in src_mappings['objects']] for tag in tags if tag]))


tagged_mappings = [get_tagged_mappings(src_baseApiUrl, src_sesh_id, tag) for tag in src_tag_list]

ids_with_tags_names = {item['id']: {'map_name': item['path'].split('/')[-1], 'tags': item['tags']} for obj in tagged_mappings for item in obj['objects']}
export_data={
    "name" : f"movingjob_{current_date}_{current_time}",
    "objects" :[]
}

new_objects=[]
while True:
    print("(Type 'Y' or 'N')")
    param=input("Do you want to include Dependencies: ")
    if param=='Y' or  param=='y':
        for key in ids_with_tags_names:
             new_object={"id" : key,
                        "includeDependencies" : True}
             new_objects.append(new_object)
        break
    elif param=='N' or  param=='n':
        print("Prompt: Make Sure that the Target IICS ORG contains neccessary Connections and Agent Group ")
        for key in ids_with_tags_names:
             new_object={"id" : key,
                        "includeDependencies" :False}
             new_objects.append(new_object)
        break
    else:
        print("Invalid input. Please enter 'Y' or 'N' !")


export_data["objects"] += new_objects

export_jobId=export_mappings(src_baseApiUrl, src_sesh_id, export_data)
print(export_jobId)
export_status_response=get_export_status(src_baseApiUrl, src_sesh_id, export_jobId)
print(export_status_response)

file_name=export_download(export_jobId)
file_path=os.path.join(output_dir,file_name)

import_jobId=upload_import_job(file_name,file_path)

import_job_name=import_status(import_jobId)

initiate_import_job(import_job_name)

# Get list of mappings with the specified tag from tgt user
tgt_mappings_url = f"{tgt_baseApiUrl}/public/core/v3/objects?q=location=='Default'"  

tgt_mappings_response = requests.get(tgt_mappings_url, headers={'INFA-SESSION-ID': tgt_sesh_id})
tgt_mappings=tgt_mappings_response.json()

print("")
print(tgt_mappings)

for obj in tgt_mappings['objects']:
    path =  obj ['path']
    idx = path.rfind('/')
    obj['path'] = obj['path'][idx+1:]

# print("updated tgt mappings")
# print(tgt_mappings)

id_tag_mapping = {}
# print("ids with tag and names", ids_with_tags_names)
# print("tgt mappings",tgt_mappings)

for id, data in ids_with_tags_names.items():
    for obj in tgt_mappings['objects']:
        if obj['path'] == data['map_name']:
            id_tag_mapping[id] = {
                'id': obj['id'],
                'tag': data['tags'] 
            }
            break
        
# print("id tag mapping:")
# print(id_tag_mapping)

tagging()


