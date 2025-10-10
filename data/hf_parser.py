from datasets import load_dataset
import pandas as pd
import numpy as np
from random import randint
pd.options.display.max_rows = 2000
pd.options.display.max_columns = 50

INSTRUCTION =  ("You are given a JSON object containing the following information:\n"
    "- persona information about the sender and recipient\n"
    "- past_emails: a list of previous emails in the thread, each including a summary for context\n"
    "- email_summary: a summary of the next email the sender is going to write\n\n"
    "The 'sender' always refers to the sender of the next email, and 'recipient' is the intended recipient.\n\n"
    "Your task is to generate the next email in the thread as a JSON object with the following fields:\n"
    "1. from: the sender's persona (name and email if available)\n"
    "2. to: the recipient's persona (name and email if available)\n"
    "3. subject: the subject line of the email\n"
    "4. body: the full email body\n\n"
    "Use the information and the past emails with their summaries to write a realistic and contextually appropriate email.\n")

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
        print(thread)
        summary = matched_summaries[-1]
        for j, past_email in enumerate(past_emails):
            past_email["summary"] = matched_summaries[j] if j < len(matched_summaries) else ""
        instr = INSTRUCTION
        
        email_data.append({
            "instruction": INSTRUCTION,
            "input": {
                "past_emails": past_emails,
                "sender": sender,
                "recipient": recipient,
                "next_email_summary": summary,
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