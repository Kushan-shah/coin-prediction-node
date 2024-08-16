import os
import requests

inference_address = os.environ["INFERENCE_API_ADDRESS"]
url = f"{inference_address}/update"

print("UPDATING INFERENCE WORKER DATA")

response = requests.get(url)
if response.status_code == 200:
    if response.text == "0":
        print("Response content is '0'")
        exit(0)
    else:
        exit(1)
else:
    print(f"Request failed with status code: {response.status_code}")
    exit(1)
