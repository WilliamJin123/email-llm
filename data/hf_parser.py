from datasets import load_dataset
import pandas as pd
import numpy as np
from random import randint
pd.options.display.max_rows = 2000
pd.options.display.max_columns = 50

INSTRUCTION =  """You are an AI assistant specialized in generating realistic emails. Your task is to generate the next email in an ongoing thread. You will be provided with:
1.  **Persona descriptions** for the sender and recipient.
2.  **`past_emails`**: A list of previous emails in the thread, each with a summary, from which you can **extract the sender's and recipient's names and email addresses**.
3.  **`email_summary`**: A concise summary of the specific content and details that *must* be included in the next email.

**Crucially, your generated email MUST meticulously and without exception incorporate every single specific detail mentioned in the `email_summary`. Do not omit, alter, or generalize any information from the `email_summary`.**

The email should be generated as a JSON object with the following fields:
- `from`: The sender's name and email, extracted from `past_emails`.
- `to`: The recipient's name and email, extracted from `past_emails`.
- `subject`: The subject line of the email, maintaining thread continuity.
- `body`: The full text of the email.

Ensure the email sounds natural, follows a conversational flow, and matches the tone and relationship established in the `past_emails` and implied by the sender's persona description."""
TASK = "Generate the next email in the thread as a JSON object, strictly following all details in the email_summary, while maintaining the established tone and persona."

def load_data(offset = 0, train_size = 5000):
    
    ds = load_dataset("argilla/FinePersonas-Synthetic-Email-Conversations", "default", split="train")
    df = ds.to_pandas()
    length = len(df)
    df = df.iloc[::int(length/train_size), :].reset_index(drop=True)
    convo_ids = np.arange(0, length, int(length//train_size))[:len(df)+1]
    return df, convo_ids
def load_summaries(ids):
    ds = load_dataset("argilla/FinePersonas-Conversations-Email-Summaries", "default", split="train")
    df = ds.to_pandas()
    new_ids = []
    current_id = -1
    prev_id = None
    for row in df.itertuples(index = False):
        if row.conversation_id != prev_id:
            current_id += 1
            prev_id = row.conversation_id
        new_ids.append(current_id)
    df["conversation_id"] = new_ids 
    print(df)
    df = df[df['conversation_id'].isin(ids)].reset_index(drop=True)
    return df




def parse_emails(conversations, summaries, convo_ids):
    email_data = []
    for i, row in enumerate(conversations.itertuples(index=False)):
        thread = row.formatted_emails
        if not thread.any():
            print("skipped a row because empty formatted emails")
            continue
        thread_size = len(thread)
        index = randint(0, thread_size-1)
        if index % 2 == 0:
            sender, recipient = row.persona, row.other_persona
        else:
            sender, recipient = row.other_persona, row.persona
        #sender should be the one who sent the first or third email if we are taking first or third email
        #else sender should actually be the recipient of the first email (other persona) who sends the second email
        thread = thread[:(index + 1)] #if i  = 0 we want first email, :1; if i = 1 we want second email :2; 
        past_emails = thread[:-1]
        cur_email = thread[-1]
        
        convo_id = convo_ids[i]
        matched_summaries = summaries[summaries['conversation_id']==convo_id]['summary'].tolist()[:(index+1)]
        # print("step", i)
        # print('selecting email index', index)
        # print('conversation_id', convo_id)
        # print(matched_summaries)
        if not matched_summaries:
            continue
        summary = matched_summaries[-1]
        for j, past_email in enumerate(past_emails):
            past_email["summary"] = matched_summaries[j] if j < len(matched_summaries) else ""
        instr = INSTRUCTION
        
        email_data.append({
            "instruction": INSTRUCTION,
            "input": {
                "task": TASK,
                "past_emails": past_emails.tolist(),
                "sender": sender,
                "recipient": recipient,
                "email_summary": summary,
            },
            "output": cur_email
        })
        
    df = pd.DataFrame(email_data)
    return df

if __name__ == "__main__":
    convos, ids= load_data()
    summs = load_summaries(ids)
    print(convos.columns)
    email_data = parse_emails(convos, summs, ids)

    email_data.to_csv("processed_emails.csv", index=False)
    email_data.to_json("processed_emails.json", orient="records", lines=True)
    email_data.to_parquet("processed_emails.parquet", index=False)