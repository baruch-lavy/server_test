from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
import string
import json
import time
app = FastAPI()


def load_data(path):
    try:
        with open(path,'r') as f:
            data = json.load(f)
            
    except (json.JSONDecodeError):
        data = []
        
    return data
         
def save_data(path,data_to_save:dict,start,is_update=False):
    if not is_update:
        data = load_data(path)
        data.append(data_to_save)
    else:
        data = load_data(path)
        for route in data:
            if route["url"] == data_to_save["url"]:
                route["stats"][data_to_save["add_to_request"]] += 1
                route["stats"]["avg_handling_time"] = str(time.time() - start)
    with open(path,'w') as f:
        json.dump(data,f,indent=4)

def save_call_stats(url,is_first_time,start):
        if is_first_time:
            save_data('data/endpoints_data.json',{"url": url,"method":"POST","stats":{"total_requests_recieved":1,"avg_handling_time":0}},start)
        else:
            save_data('data/endpoints_data.json',{"url":url,"add_to_request":"total_requests_recieved"},start,True)
        
# base_model classes
class Caesar(BaseModel):
    text:str
    offset:int
    mode:str
    
class FenceDecrypt(BaseModel):
    text:str

# test routes
@app.get("/test")
def test():
    return {"msg":"hi from test"}


@app.get("/test/{name}")
def save_user(name):
    with open("names.txt","a") as f:
        f.write(name + ' ')
    return {"msg": "saved user"}


# caesar route
is_first_time = True
@app.post("/caesar")
def caesar(body:Caesar):
    start = time.time()
    global is_first_time
    if is_first_time:
        save_call_stats("/caesar",True,start)
        is_first_time = False
    else:
        save_call_stats("/caesar",False,start)
       
        
    text = body.text.lower().strip().replace(" ","")
    offset = body.offset
    mode = body.mode
    letters = list(string.ascii_lowercase)
    
    encrypted = ''
    if mode == "encrypt":
        for letter in text:
            index = letters.index(letter)
            encrypt_idx = (index + offset) % len(letters)
            encrypted += letters[encrypt_idx]
        return {"encrypted_text":encrypted}

    elif mode == "decrypt":
        for letter in text:
            index = letters.index(letter)
            encrypt_idx = (index - offset) % len(letters)
            encrypted += letters[encrypt_idx]
        return {"encrypted_text":encrypted}
    
    
#fence routes
is_first_time_fence = True
@app.get("/fence/encrypt")
def fence_encrypt(text:str):
    
    # save stats
    start = time.time()
    global is_first_time_fence
    if is_first_time_fence:
        save_call_stats("/fence_encrypt",True,start)
        is_first_time_fence = False
    else:
        save_call_stats("/fence_encrypt",False,start)
        
    text = text.lower().strip().replace(" ","")
    encrypted = ''
    even = ''
    odd = ''
    for i in range(len(text)):
        if i % 2:
            odd += text[i]
        else:
            even += text[i]
    encrypted = even + odd
    return {"encrypted_text":encrypted,}
    
is_first_time_fence_d = True          
@app.post("/fence/decrypt")
def fence_encrypt(body:FenceDecrypt):
    start = time.time()
    global is_first_time_fence_d
    if is_first_time_fence_d:
        save_call_stats("/fence_decrypt",True,start)
        is_first_time_fence_d = False
    else:
        save_call_stats("/fence_decrypt",False,start)
    
    
    text = body.text
    even = ''
    odd = ''
    
    if len(text) % 2:
        even += text[:len(text)//2 + 1]
        odd += text[len(text)//2 + 1:]
    else:
        even += text[:len(text) //2]
        odd += text[len(text) //2:]
        
    decrypted = ''
   
    for i in range(len(text)):
        if not i % 2:
            decrypted += even[0]
            even = even[1:]
        else:
            decrypted += odd[0]
            odd = odd[1:]
            
    return {"even":even,"odd":odd,"decrypted":decrypted}