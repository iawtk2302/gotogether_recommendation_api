import requests
import json
import pandas as pd
# Cấu hình thông tin Firebase
project_id = "gotogether-1b01c"
api_key = "AIzaSyCS3lAxDuaJFeTL5w_VO2JsGrVxvGnmBrE"
collection_name = "Trip"

# Tạo URL cho REST API
url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents:runQuery?key={api_key}"

# Cấu hình truy vấn
query = {
    "structuredQuery": {
        "select": {
            "fields": [
                {"fieldPath": "idTrip"},
                {"fieldPath": "title"},
                {"fieldPath": "description"},
                {"fieldPath": "activities"},
                # Thêm nhiều fields khác nếu muốn
            ]
        },
        "from": [{"collectionId": collection_name}],
        "where": {
            "fieldFilter": {
                "field": {"fieldPath": "status"},
                "op": "EQUAL",
                "value": {"stringValue": "pending"},
            }
        },
        # "orderBy": [{"field": {"fieldPath": "idTrip"}, "direction": "ASCENDING"}],
    }
}

# Thực hiện yêu cầu POST

# Lấy thông tin từ fields và chuyển đổi thành một từ điển mới
def process_value(value):
    if "stringValue" in value:
        return value["stringValue"]
    elif "arrayValue" in value:
        return '|'.join([item["stringValue"] for item in value["arrayValue"]["values"]])
    else:
        return None
    
def getData(name):  
    response = requests.post(url, json=query)

    data_list = json.loads(response.text)
    new_data = []
    for data in data_list:
     fields = data["document"]["fields"]
     new_dict = {key: process_value(value) for key, value in fields.items()}
     new_data.append(new_dict)

# Tải dữ liệu JSON vào danh sách Python
    temp = json.loads(json.dumps(new_data, indent=2))

# Chuyển danh sách thành DataFrame pandas
    data_frame = pd.DataFrame(temp)

# Ghi dữ liệu ra tệp CSV
    data_frame.to_csv(name+".csv", index=False)

# Kiểm tra mã trạng thái và in kết quả
# if response.status_code == 200:
#     # data = json.loads(response.text)
#     # print(json.dumps(data, indent=2))
#     print(json.dumps(new_data, indent=2))
    
# else:
#     print(f"Error {response.status_code}: {response.text}")
