import os
import json
from pydantic import BaseModel, ValidationError
from mistralai import Mistral

# -----------------------------
# Pydantic Model for Validation
# -----------------------------
class Person(BaseModel):
    name: str
    age: int
    email: str

# --------------------------------------
# Function to Call Mistral in JSON Mode
# --------------------------------------
def call_mistral_json_mode(prompt: str, system_message: str = "") -> str:
    """Call the Mistral API with a prompt and optional system message, expecting a JSON object response."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError("Please set the MISTRAL_API_KEY environment variable.")
    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)
    messages = [
        {"role": "user", "content": prompt},
        {"role": "system", "content": system_message},
    ]
    chat_response = client.chat.complete(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
    )
    return chat_response.choices[0].message.content

# -----------------------------
# Read CSV Input from File
# -----------------------------
with open("example_incomplete.csv", "r", encoding="utf-8") as f:
    csv_input = f.read().strip()

# -----------------------------
# Initial Prompt Construction
# -----------------------------
model_json_schema = Person.model_json_schema()
prompt = f"""
            Given the following CSV data, return a JSON array of objects with fields: {Person.model_json_schema()}

            CSV:
            {csv_input}

            Example output:
            [
            {{"name": "Alice", "age": 30, "email": "alice@example.com"}},
            {{"name": "Bob", "age": 25, "email": "bob@example.com"}}
            ]
        """

print("\n" + "="*50)
print("Mistral CSV to Structured Example: Attempt 1")
print("="*50 + "\n")
response = call_mistral_json_mode(prompt)
print("Mistral response:\n", response)

# -----------------------------
# Validation and Retry Loop
# -----------------------------
try:
    data = json.loads(response)
    people = [Person(**item) for item in data if isinstance(item, dict)]
    print("\nValidated people:")
    for person in people:
        print("  ", person)
    skipped = [item for item in data if not isinstance(item, dict)]
    if skipped:
        print("\nWarning: Skipped non-dict items:", skipped)
except (json.JSONDecodeError, ValidationError, TypeError) as e:
    print("\nValidation error on initial attempt:", e)
    attempt = 2
    max_attempts = 10
    last_response = response
    last_error = e
    while attempt <= max_attempts:
        # Improved system message for retries
        system_message = (
            "You are a data cleaning and structuring assistant. "
            f"Your job is to convert CSV data into a JSON array of objects with the fields: {model_json_schema}"
            "If any data is missing or invalid, infer reasonable values or skip the row. "
            "Always return valid JSON. Do not include any explanation, only the JSON array."
        )
        # Improved prompt with actionable instructions
        improved_prompt = f"""
            Given the following CSV data, return a JSON array of objects with fields: {model_json_schema}

            CSV:
            {csv_input}

            Instructions:
            1. For each row, create an object with {model_json_schema}.
            2. If a field is missing or invalid, infer a reasonable value.
            3. Ensure the output is a valid JSON array, with no extra text.
            4. Use the last error and response to determine how to fix the error.
                Last error: {str(last_error)}
                Last response: {last_response}

            Example output:
            [
                {{"name": "Alice", "age": 30, "email": "alice@example.com"}},
                {{"name": "Bob", "age": 25, "email": "bob@example.com"}}
            ]


            """
        print("\n" + "="*50)	
        print(f"Attempt {attempt}: Improved Prompt & System Message")
        print("="*50 + "\n")
        last_response = call_mistral_json_mode(improved_prompt, system_message=system_message)
        print("Mistral response:\n", last_response)
        try:
            improved_data = json.loads(last_response)
            people = [Person(**item) for item in improved_data if isinstance(item, dict)]
            print("\nValidated people:")
            for person in people:
                print("  ", person)
            skipped = [item for item in improved_data if not isinstance(item, dict)]
            if skipped:
                print("\nWarning: Skipped non-dict items:", skipped)
            break
        except (json.JSONDecodeError, ValidationError, TypeError) as e2:
            print(f"\nValidation error on attempt {attempt}:", e2)
            last_error = e2
            last_response = improved_prompt
            attempt += 1
    else:
        print("\nFailed to get valid structured data after multiple attempts.")
        print("Last error:", last_error) 