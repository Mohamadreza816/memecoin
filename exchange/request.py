import requests

endpoint = "http://127.0.0.1:8000/"
# ?abc=12500"

# get_response = requests.get(endpoint)
get_response = requests.post(endpoint,json={"title":"yoho"})

print(get_response.json())


# import requests
#
# endpoint = "http://127.0.0.1:8000/"
#
# access_token = "YOUR_ACCESS_TOKEN_HERE"
#

# headers = {
#     'Authorization': f'Bearer {access_token}'
# }
#
# #
# get_response = requests.post(endpoint, json={"title": "yoho"}, headers=headers)
#
# print(get_response.json())


{
	"username":"samin",
  	"password" : "45"
}

{
  "type":"B",
  "amount":100

}