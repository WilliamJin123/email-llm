
import json
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
model_name = "Qwen/Qwen3-4B"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    dtype="auto",
    device_map="auto"
)

# prepare the model input
prompt = {"instruction":"You are given a JSON object containing the following information:\n- persona information about the sender and recipient\n- past_emails: a list of previous emails in the thread, each including a summary for context\n- email_summary: a summary of the next email the sender is going to write\n\nThe 'sender' always refers to the sender of the next email, and 'recipient' is the intended recipient.\n\nYour task is to generate the next email in the thread as a JSON object with the following fields:\n1. from: the sender's persona (name and email if available)\n2. to: a list containing the recipient's persona (name and email if available)\n3. subject: the subject line of the email\n4. body: the full email body\n\nUse the information and the past emails with their summaries to write a realistic and contextually appropriate email.\n","input":{"past_emails":[{"body":"Hey Michael,\n\nI hope you're doing well! I've been thinking a lot about the ideas we discussed at the conference and I think I have an idea for our collaboration project. What if we created a virtual field trip that takes students on a journey through different cities around the world, exploring the impacts of climate change on urban environments? \n\nI think this could be a great way to combine our expertise in environmental and urban geography and create an engaging learning experience for our students. Let me know what you think!\n\nBest,\nSarah","from":"Sarah Thompson <sarah.thompson@ridgemontschools.org>","subject":"Virtual Field Trip Collaboration","to":"Michael Chen <michael.chen@oakvilleschools.ca>","summary":"Sarah suggests collaborating on a virtual field trip project that explores the impacts of climate change in urban environments across different cities. She believes this could combine expertise in environmental and urban geography to create an engaging learning experience for students. Sarah is seeking feedback on the idea."},{"body":"Sarah,\n\nThat's a fantastic idea! I love the idea of a virtual field trip that explores the intersection of climate change and urban geography. I think our students would really benefit from seeing the real-world applications of the concepts we teach.\n\nI've been doing some research on cities that would be great case studies for this project. I was thinking we could include cities like Miami, which is dealing with rising sea levels, and Jakarta, which is sinking due to excessive groundwater extraction. What do you think?\n\nI'm also happy to share some of the resources I've been using to teach about urban sustainability. I think they could be really helpful for this project.\n\nLet me know when you're free to chat more about this. I'm excited to get started!\n\nMichael","from":"Michael Chen <michael.chen@oakvilleschools.ca>","subject":"RE: Virtual Field Trip Collaboration","to":"Sarah Thompson <sarah.thompson@ridgemontschools.org>","summary":"Michael is enthusiastic about collaborating on a virtual field trip that explores the intersection of climate change and urban geography. He suggests including cities like Miami, which is dealing with rising sea levels, and Jakarta, which is sinking due to excessive groundwater extraction. Michael also offers to share resources on urban sustainability and is eager to discuss the project further."}],"sender":"A geography teacher or high school educator focused on environmental and climate studies, likely designing a lesson plan or assignment on the human impacts of climate change.","recipient":"A geography teacher or instructor focused on human geography and urban studies, likely at the high school or introductory college level.","next_email_summary":"Sarah is enthusiastic about the collaboration and suggests including Copenhagen as a case study for its sustainable urban planning. She requests to see the resources used for teaching urban sustainability and proposes a video call for Tuesday afternoon to discuss further. Sarah is excited about the project and its educational value."}}
prompt = str(prompt)
print(prompt)
messages = [
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=False # Switches between thinking and non-thinking modes. Default is True.
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

# conduct text completion
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=32768
)
output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

# parsing thinking content
try:
    # rindex finding 151668 (</think>)
    index = len(output_ids) - output_ids[::-1].index(151668)
except ValueError:
    index = 0

thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

print("thinking content:", thinking_content)
print("content:", content)