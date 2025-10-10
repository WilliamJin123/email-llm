from hf_parser import load_data, load_summaries, parse_emails

if __name__ == "__main__":
    validation_convos, val_ids = load_data(1, 500)
    test_convos, test_ids= load_data(2, 200)
    val_summaries = load_summaries(val_ids)
    test_summaries = load_summaries(test_ids)
    val_data = parse_emails(validation_convos, val_summaries, val_ids)
    test_data = parse_emails(test_convos, test_summaries, test_ids)
    
    test_data.to_csv("test_emails.csv", index=False)
    test_data.to_json("test_emails.json", orient="records", lines=True)
    test_data.to_parquet("test_emails.parquet", index=False)
    
    val_data.to_csv("val_emails.csv", index=False)
    val_data.to_json("val_emails.json", orient="records", lines=True)
    val_data.to_parquet("val_emails.parquet", index=False)  
    