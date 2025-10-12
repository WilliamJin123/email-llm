import csv
import re

def format_json_attributes(text):
    """
    Adds newlines after commas that precede JSON attributes.
    
    Pattern explanation:
    , ['"]     - Match a comma followed by space and quote (single or double)
    \w+        - Match one or more word characters (the attribute name)
    ['"]       - Match the closing quote
    \s*:\s*    - Match the colon with optional whitespace around it
    
    The regex finds patterns like:
    - , 'name': 
    - , "email":
    - ,'subject' :
    
    And replaces the comma with comma + newline
    """
    text = text.replace('\\n', '\n')
    pattern = r",(\s+['\"])(\w+)(['\"])\s*:"
    
    bold_pattern = r"(\s*+['\"])(\w+)(['\"])\s*:"
    
   
    formatted = re.sub(pattern, r",\n\1\2\3:", text)
    formatted = re.sub(bold_pattern, r"\1<b>\2</b>\3:", formatted)
    
    return formatted
def csv_to_html_comparison(csv_file, html_file):
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
    
    html = ['<!DOCTYPE html><html><head><meta charset="utf-8"><style>']
    html.append('body { font-family: Arial; margin: 20px; background: #f5f5f5; }')
    html.append('.email-card { background: white; margin-bottom: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }')
    html.append('.header { background: #2196F3; color: white; padding: 15px; border-radius: 8px 8px 0 0; }')
    html.append('.comparison { display: grid; grid-template-columns: 1fr 1fr; gap: 0; }')
    html.append('.column { padding: 20px; border-top: 1px solid #eee; }')
    html.append('.test { background: #e8f5e9; border-right: 2px solid #4CAF50; }')
    html.append('.lora { background: #fff3e0; }')
    html.append('h3 { margin: 0 0 10px 0; color: #333; }')
    html.append('pre { white-space: pre-wrap; word-wrap: break-word; font-family: "Courier New", monospace; font-size: 13px; line-height: 1.5; margin: 0; }')
    html.append('.instruction { padding: 15px; background: #f9f9f9; border-top: 1px solid #eee; font-style: italic; color: #666; }')
    html.append('</style></head><body>')
    html.append('<h1>Email Output Comparison</h1>')
    
    for i, row in enumerate(data):
        html.append(f'<div class="email-card">')
        html.append(f'<div class="header"><h2>Email #{i+1}</h2></div>')
        
        if 'instruction' in row and row['instruction']:
            html.append(f'<div class="instruction"><strong>Instruction:</strong><pre>{format_json_attributes(row["instruction"])}</pre></div>')
        
        
        html.append(f'<div class="instruction"><strong>Input:</strong><pre>{format_json_attributes(row["input"])}</pre></div>')
        
        html.append('<div class="comparison">')
        html.append(f'<div class="column test"><h3>✓ Test Output</h3><pre>{format_json_attributes(row["test_output"])}</pre></div>')
        html.append(f'<div class="column lora"><h3>⚡ LoRA Output</h3><pre>{format_json_attributes(row["lora_output"])[len("<think>\\n</think>\n"):]}</pre></div>')
        html.append('</div>')
        html.append('</div>')
    
    html.append('</body></html>')
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))
    
    print(f"Created {html_file} - open it in your browser!")

if __name__ == "__main__":
    csv_to_html_comparison('./test_outputs.csv', './comparison.html')