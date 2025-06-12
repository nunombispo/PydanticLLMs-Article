# Mistral CSV to Structured Example

This project demonstrates how to use the Mistral API in JSON mode to convert CSV data into structured JSON objects validated by a Pydantic model. It includes robust error handling and retry logic to ensure valid output.

If these scripts were useful to you, consider donating to support the Developer Service Blog: https://buy.stripe.com/bIYdTrggi5lZamkdQW

## Features

- Reads CSV data from a file
- Uses Mistral API to convert CSV to JSON array of objects
- Validates output using a Pydantic model (`Person`)
- Retries with improved prompts if validation fails
- Infers or skips rows with missing/invalid data

## Requirements

- Python 3.8+
- [mistralai](https://pypi.org/project/mistralai/) Python package
- [pydantic](https://pypi.org/project/pydantic/) Python package
- Mistral API key (set as `MISTRAL_API_KEY` environment variable)

## Setup

1. **Install dependencies:**
   ```bash
   pip install mistralai pydantic
   ```
2. **Set your Mistral API key:**
   ```bash
   export MISTRAL_API_KEY=your_api_key_here  # On Windows use 'set' instead of 'export'
   ```
3. **Prepare your CSV file:**
   - Place your CSV data in a file named `example_incomplete.csv` in the project directory.

## Usage

Run the script:

```bash
python mistral_csv_to_structured_example.py
```

The script will:

- Read the CSV file
- Call the Mistral API to convert it to structured JSON
- Validate and print the results
- Retry with improved prompts if needed

## Example

**Input CSV (`example_incomplete.csv`):**

```
name,age,email
Alice,30,alice@example.com
Bob,25,bob@example.com
Charlie,,charlie@example.com
```

**Output:**

```
==================================================
Mistral CSV to Structured Example: Attempt 1
==================================================
Mistral response:
 [ ... JSON array ... ]

Validated people:
   name='Alice' age=30 email='alice@example.com'
   name='Bob' age=25 email='bob@example.com'
   name='Charlie' age=... email='charlie@example.com'
```

## Notes

- The script will attempt up to 10 times to get valid structured data.
- If a row is missing required fields, the script will ask the model to infer or skip it.
- The Pydantic model can be customized in the script for different schemas.

## License

MIT
