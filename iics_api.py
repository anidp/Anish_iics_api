import requests
import json 
import os
import datetime
import time

current_date = datetime.date.today()
indian_current_date=current_date.strftime("%d-%m-%Y")
current_time = datetime.datetime.now().strftime("%I-%M_%p")

source_user = 'anishhdp2'
source_password = 'Anidatap@12345'

# source_user = 'dummyuser123'
# source_password = 'qwerty@12345'

target_user = 'dummyuser123'
target_password = 'qwerty@12345'

tag_name = 'work'
# updated_tag='work2'

iics_url='https://dm-ap.informaticacloud.com/saas/public/core/v3/login'

# Authentication

source_auth_url=f"{iics_url}"
target_auth_url = f"{iics_url}"
source_auth_data = {'username': source_user, 'password': source_password}
target_auth_data = {'username': target_user, 'password': target_password}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}


source_auth_response = requests.post(source_auth_url, data=json.dumps(source_auth_data), headers=headers)
target_auth_response = requests.post(target_auth_url, data=json.dumps(target_auth_data), headers=headers)
print(source_auth_response)


src_login_response=source_auth_response.json()
tgt_login_response=target_auth_response.json()


src_baseApiUrl=src_login_response['products'][0]['baseApiUrl']
tgt_baseApiUrl=tgt_login_response['products'][0]['baseApiUrl']



src_sesh_id=src_login_response['userInfo']['sessionId']
tgt_sesh_id=tgt_login_response['userInfo']['sessionId']


src_main_id=src_login_response ['userInfo']['id']
tgt_main_id=tgt_login_response ['userInfo']['id']


# Get list of mappings with the specified tag from source user
source_mappings_url = f"{src_baseApiUrl}/public/core/v3/objects?q=location=='Default'"  

source_mappings_response = requests.get(source_mappings_url, headers={'INFA-SESSION-ID': src_sesh_id})
src_mappings=source_mappings_response.json()
# print(src_mappings)


#extracting tags into a list
src_tag_list=[tag['tags'] for tag in src_mappings['objects']] #contains null and duplicates

src_tag_list = [tag for tags in src_tag_list for tag in tags] # Flatten the list of lists
src_tag_list = [tag for tag in src_tag_list if tag] # Remove null or empty values
src_tag_list = list(set(src_tag_list)) # Remove duplicate values
# print (src_tag_list)


tagged_mappings=[]

#extracting only mappings with tags
for src_tag in src_tag_list:
    tagged_mappings_url = f"{src_baseApiUrl}/public/core/v3/objects?q=tag=='{src_tag}'"
    tagged_mappings_response=requests.get(tagged_mappings_url,headers={'INFA-SESSION-ID': src_sesh_id})
    json_response=tagged_mappings_response.json()
    tagged_mappings.append(json_response)
# print(tagged_mappings)


#fetch names od tagged mappings
# taggedM_names= []
# for d in tagged_mappings:
#     for obj in d['objects']:
#         t_path = obj['path']
#         # remove 'Default/' from the path
#         t_path=t_path[t_path.rfind('/')+1:]
#         taggedM_names.append(t_path)

# print(taggedM_names)



#fetching tagged ids and tags of tagged mappings
# ids_with_tags = {}
# for obj in tagged_mappings:
#     for item in obj['objects']:
#         ids_with_tags[item['id']] = item['tags']

# # print(ids_with_tags)

#fetching tagged ids, names and tags of tagged mappings
ids_with_tags_names={}
for obj in tagged_mappings:
    for item in obj['objects']:
        path = item['path']
        # idx = path.rfind('/')
        # map_name = path[idx+1:]
        ids_with_tags_names[item['id']] = {'path_name': path, 'tags': item['tags']}
      

#path list

# src_path_list = [path["path"] for path in src_mappings["objects"]]
# print(src_path_list)


# #object list
# src_obj_list = [obj["path"] for obj in src_mappings["objects"]]
# src_trimmed_obj_list=[obj.replace("Default/", "") for obj in src_path_list]
# print(src_trimmed_obj_list)



# #Type list
# src_type_list=[type['type'] for type in src_mappings['objects']]
# print(t_type_list)

#id_list
# src_id_list=[id['id'] for id in src_mappings['objects']]




#export###################

export_data={
    "name" : f"movingjob_{current_date}_{current_time}",
    "objects" :[]
}

new_objects=[]
# print("(Type 'Y' or 'N')")
# param=input("Do you want to include Dependencies: ")

# if param=='Y':
#     for key in ids_with_tags_names:
#          new_object={"id" : key,
#                     "includeDependencies" : true}
#         new_objects.append(new_object)
# else:
#     for key in ids_with_tags_names:
#          new_object={"id" : key,
#                     "includeDependencies" :false}
#         new_objects.append(new_object)

# for key in ids_with_tags_names:
    # new_object={"id" : key,
#     new_objects.append(new_object)    

for key in ids_with_tags_names:
    new_object={"id" : key}
    new_objects.append(new_object)

export_data["objects"] += new_objects

# print(export_data)



headers_export= {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'INFA-SESSION-ID': src_sesh_id
}

export_response=requests.post(f"{src_baseApiUrl}/public/core/v3/export", headers=headers_export,json=export_data)

export_json=export_response.json()

export_job_id=export_json['id']
# print(export_job_id)
print(f"export response= {export_response}")

#export status############
payload = {}
export_status_response=requests.get(f"{src_baseApiUrl}/public/core/v3/export/{export_job_id}",headers=headers_export,data=payload)
print(f"export status response = {export_status_response}")  


status_response=export_status_response.json()

#download export package##################

headers_export_download = {
  'Content-Type': 'application/zip',
  'Accept': 'application/zip',
  'INFA-SESSION-ID': src_sesh_id
}

download_url=f"{src_baseApiUrl}/public/core/v3/export/{export_job_id}/package"

export_download_response=requests.get(download_url,headers= headers_export_download)


output_dir='D:\IICS_content\exported'  #setting up path for download
export_zip_file_name= f"{export_job_id}_{current_date}_{current_time}.zip"
file_path=os.path.join(output_dir,export_zip_file_name)
with open(file_path, "wb") as f:    
    f.write(export_download_response.content)

print(f"export download response={export_download_response}")

#uploading import package ##########

payload={}
headers_import= {
  'Accept': 'application/json',
  'INFA-SESSION-ID': tgt_sesh_id
}

files=[
  ('package',(export_zip_file_name,open(file_path,'rb'),'application/zip'))
]

import_url=f"{tgt_baseApiUrl}/public/core/v3/import/package"
import_response=requests.post(import_url, headers=headers_import,data=payload,files=files)
print(f"import resposne= {import_response}")

import_json=import_response.json() #fetch jobid of the import job
import_jobId=import_json['jobId']

#import status


payload={}
headers_import_status = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'INFA-SESSION-ID': tgt_sesh_id
}

import_status_url=f"{tgt_baseApiUrl}/public/core/v3/import/{import_jobId}"
import_status_response=requests.get(import_status_url,headers=headers_import_status,data=payload)
print(f"import status response is = {import_status_response}")

import_status=import_status_response.json()

import_job_name=import_status ['name']


#starting import job #########
payload = json.dumps({
  "name": f"{import_job_name}"
})
import_job_response=requests.post(import_status_url,headers= headers_import_status,data=payload)

print(f"import job response= {import_response}")


time.sleep(10)

# Get list of mappings with the specified tag from tgt user
tgt_mappings_url = f"{tgt_baseApiUrl}/public/core/v3/objects?q=location=='Default'"  

tgt_mappings_response = requests.get(tgt_mappings_url, headers={'INFA-SESSION-ID': tgt_sesh_id})
tgt_mappings=tgt_mappings_response.json()
# print(tgt_mappings)

id_tag_mapping = {}

for id, data in ids_with_tags_names.items():
    for obj in tgt_mappings['objects']:
        if obj['path'] == data['path_name']:
            id_tag_mapping[id] = {
                'id': obj['id'],
                'tag': data['tags'][0] if data['tags'] else None
            }
            break
        
# print("id tag mapping:")
# print(id_tag_mapping)
# print("")




#tagging in target org
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
        "tags": [value ['tag']]
    }
    import_jobs_data.append(tag_data)

# print("import jobs data:")
# print(import_jobs_data)

tag_response = requests.post(tgt_tag_url, headers=headers_tag, json=import_jobs_data)
print(f"tag response= {tag_response}")

