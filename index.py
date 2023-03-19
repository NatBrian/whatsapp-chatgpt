from flask import Flask, request
import requests
import os
import json

openai_api_key = os.environ.get('OPENAI_API_KEY')
chat_gpt_api_url = os.environ.get('CHATGPT_API_URL')

facebook_version = os.environ.get('FACEBOOK_VERSION')
facebook_phone_number_id = os.environ.get('FACEBOOK_PHONE_NUMBER_ID')
facebook_verify_token = os.environ.get('FACEBOOK_VERIFY_TOKEN')
facebook_access_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')

app = Flask(__name__)

users_chat_history = {}

def chat_completion(message_payload, receiver_number):
    receiver_chat_histroy = users_chat_history[receiver_number]
    request_body = json.loads('{"messages":[]}')
    
    for chat in receiver_chat_histroy:
        request_body["messages"].append({"role":chat["role"], "content":chat["content"]})
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + str(openai_api_key)
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": request_body["messages"]
    }
    
    response = requests.post(str(chat_gpt_api_url), headers=headers, json=data)
    print("chat_gpt_response")
    print(response)
    print()
    
    response_json = response.json()
    content = response_json['choices'][0]['message']['content']
    print(response_json)
    
    return content

# send msg to receiver


def send_msg(msg, receiver_number):
    headers = {
        'Authorization': 'Bearer ' + facebook_access_token,
    }
    json_data = {
        'messaging_product': 'whatsapp',
        'to': receiver_number,
        'type': 'text',
        "text": {
            "body": msg
        }
    }
    response = requests.post(
        'https://graph.facebook.com/' + facebook_version + '/' + facebook_phone_number_id + '/messages', headers=headers, json=json_data)

    print("facebook_response")
    print(response.text)
    print()

@app.route("/", methods=["GET"])
def ping():
    return "pong", 200

@app.route("/users_chat_history", methods=["GET"])
def get_users_chat_history():
    return users_chat_history, 200

@app.route("/users_chat_history", methods=["DELETE"])
def delete_users_chat_history():
    # reset users_chat_history
    global users_chat_history
    users_chat_history = {}
    return users_chat_history, 200

@app.route("/receive_msg", methods=["POST", "GET"])
def webhook_whatsapp():
    # whatsapp webhook verify token
    if request.method == "GET":
        if request.args.get('hub.verify_token') == facebook_verify_token:
            return request.args.get('hub.challenge')
        return "Authentication failed. Invalid Token."

    res = request.get_json()

    # processing chat message

    print("request body")
    print(res)
    print()

    global users_chat_history
    
    try:
        if res['entry'][0]['changes'][0]['value']['messages'][0]['id']:
            chat_gpt_input = res['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
            receiver_number = res['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
            
            if chat_gpt_input.lower() == "reset":
                users_chat_history[receiver_number] = []
                send_msg(assistant_content, receiver_number)
                return "OK", 200
            
            if users_chat_history:
                if receiver_number in users_chat_history:
                    users_chat_history[receiver_number].append({"role": "user", "content": chat_gpt_input})
            else:
                users_chat_history[receiver_number] = []
                users_chat_history[receiver_number].append({"role": "user", "content": chat_gpt_input})

            assistant_content = chat_completion(users_chat_history[receiver_number], receiver_number)

            users_chat_history[receiver_number].append({"role": "assistant", "content": assistant_content})
            
            send_msg(assistant_content, receiver_number)

    except Exception as ex:
        return ex, 500
    
    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True)
