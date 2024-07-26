import streamlit as st
import io
import csv
import google.generativeai as genai

new_chat = st.button("New Chat")
if new_chat:
     st.session_state.messages = []

def download_prompts_csv():
  """Downloads the assistant prompts as a CSV file."""
  # Extract prompts from JSON list
  prompts = [item["content"] for item in st.session_state.messages]

  csv_file = io.StringIO()
  writer = csv.writer(csv_file)
  writer.writerow(["Assistant Prompt"])
  writer.writerows([[prompt] for prompt in prompts])  # Wrap each prompt in a list
  csv_file.seek(0)
  return csv_file.getvalue(), "assistant_prompts.csv", "text/csv"

def proceededQuery(prompt:str):
    genai.configure(api_key = st.secrets['API'])
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    safety_settings = [
        {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        safety_settings=safety_settings,
        generation_config=generation_config,
        system_instruction=  """Imagine your a tutor, tutoring kids of all age group, from pre-school to colleges. The main job for you is to answer all the doubts and tutor them. Your main goal is divided in parts:

    Firstly you need to understand what the user is asking, the doubt they ask is directly related to their age. For example; if user prompted what is 2+2 then they might me small kids belonging to pre-school group, so answer the question according to the age group they belong to. You no need to continue, just for that specific question

    Secondly as you're tutor, your core responsibility is provide the guidance and make sure they understand your solution. There is no specific kind of subject you will be handing, the doubts may arise from any subject or may related to anything make sure you're ready for everything.

    Thirdly they might need in detail deep answer, so dive deep into the users doubt; refine and give a optimal yet a bit detailed answer 

    Note: Follow the instruction strictly, being a "tutor" you have to be calm and be able to communicate to them as soft as possible and for the better understanding refer the previous doubts and br revelant. The refering of pervious doubt is to just create a converstion between you and the user"""
        )

    chat_session = model.start_chat(
        history=[
        ]
    )
    response = chat_session.send_message(f"{prompt}")

    return response
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
            
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
    # Accept user inputstr
if prompt := st.chat_input("What is up?", key = "input"):
    # Display user message in chat message container
    with st.chat_message("user"):
                st.markdown(prompt)
            # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

            
data = proceededQuery(prompt)

        # Display assistant respons\e in chat message container
with st.chat_message("assistant"):
    st.markdown(data.text)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": data.text})  

with st.sidebar:
    csv_data, filename, mimetype = download_prompts_csv()
    st.download_button(label="Download CSV", data=csv_data, file_name=filename, mime=mimetype)
             
                  