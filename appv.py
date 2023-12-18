# First
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv  
import os
from PIL import Image
import numpy as np
from io import BytesIO
from io import StringIO

your_key = st.sidebar.text_input("Your key", type="password")
if not your_key:
    st.info("Please add your key to continue.")
    st.stop()

genai.configure(api_key=your_key)

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  }
]

model = genai.GenerativeModel(model_name="gemini-pro",generation_config=generation_config,safety_settings=safety_settings)

model_v = genai.GenerativeModel(model_name='gemini-pro-vision',generation_config=generation_config)


# LLM




def getAnswer(prompt,image,feedback):
    his_messages=[]
    #his_messages.append(SystemMessage(content=f'''你是一个全能的助手。会全面的回答用户的问题。'''))
    messages=[]
    message=None
    for msg in st.session_state.messages[-20:]:
        if msg["role"]=="user":
            #message=[msg["content"],None]
            his_messages.append({ "role": "user","parts": msg["content"]})
        elif msg is not None and msg["content"] is not None:
            #message[1]=msg["content"]
            his_messages.append({ "role": "model", "parts":msg["content"]})
       
    print(his_messages)  
    if(image is not None):
        prompt_v=""
        for msg in st.session_state.messages[-20:]:
            prompt_v+=f'''{msg["role"]}:{msg["content"]}
'''
        response = model_v.generate_content([prompt_v,image], stream=True)
    else:
        response = model.generate_content(contents=his_messages, stream=True)
    ret=""
    for chunk in response:
        print(chunk.text)
        print("_"*80)
        ret+=chunk.text
        feedback(chunk.text)
    
    return ret


import streamlit as st

if "messages" not in st.session_state:
    st.session_state.messages = []
    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
img=None
img_file_buffer = st.camera_input("Take a picture")

if img_file_buffer is not None:
    # To read image file buffer as a PIL Image:
    img = Image.open(img_file_buffer)
uploaded_file = st.file_uploader("Choose a picture",type=['png', 'jpg','jpeg','gif'] )
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    bytes_io = BytesIO(bytes_data)
    img = Image.open(bytes_io)
    st.image(bytes_io,width=300)
    #t.write(bytes_data)

    
if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
            #stream_handler = StreamHandler(st.empty())
            re = getAnswer(prompt,img,lambda x:st.write(x))
            print(re)
            st.session_state.messages.append({"role": "assistant", "content": re})