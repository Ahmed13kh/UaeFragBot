import json

# Input and output file paths
input_file = "fine_tuning_data.jsonl"
output_file = "fixed_fine_tuning_data.jsonl"

# Open and process the file
with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        data = json.loads(line)
        messages = data.get("messages", [])

        # Extract user and assistant messages
        prompt = next((msg["content"] for msg in messages if msg["role"] == "user"), None)
        completion = next((msg["content"] for msg in messages if msg["role"] == "assistant"), None)

        if prompt and completion:
            # Write in the required format
            formatted_data = {"prompt": prompt, "completion": completion}
            outfile.write(json.dumps(formatted_data) + "\n")

print(f"Fixed data saved to {output_file}")
