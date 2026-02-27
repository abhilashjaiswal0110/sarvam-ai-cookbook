# Import necessary libraries
import argparse  # This is for parsing command-line arguments (like your API key).
import os
import requests  # This is for making HTTP requests to the Sarvam AI API.

# This function sends your message to the Sarvam AI API and gets a response.
def get_chat_response(api_key, user_input):
    """
    Get a response from the Sarvam AI Chat Completions API.
    """
    # These are the headers for the API request, including your API key for authorization.
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    # This is the data payload for the API request.
    data = {
        "model": "sarvam-m",  # Specifies the model to use.
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},  # System message to guide the bot's behavior.
            {"role": "user", "content": user_input},  # Your question.
        ],
        "temperature": 0.7,  # Controls the creativity of the response.
    }
    # This sends the request to the Sarvam AI API.
    response = requests.post(
        "https://api.sarvam.ai/v1/chat/completions", headers=headers, json=data
    )
    response.raise_for_status()  # This will raise an error if the request fails.
    # This extracts the bot's message from the JSON response.
    return response.json()["choices"][0]["message"]["content"]


def get_chat_response_azure(user_input):
    """
    Get a response using Azure OpenAI.
    Reads credentials from environment variables:
      AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT,
      AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION (optional).
    """
    try:
        from openai import AzureOpenAI
    except ImportError:
        raise ImportError("Install the openai package: pip install openai")

    client = AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
    )
    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content


# This is the main function that runs when you execute the script.
def main():
    # This sets up the command-line argument parser to accept your API key.
    parser = argparse.ArgumentParser(description="Basic Sarvam AI Chatbot")
    parser.add_argument("--api-key", help="Your Sarvam AI API key.")
    parser.add_argument(
        "--use-azure",
        action="store_true",
        help=(
            "Use Azure OpenAI instead of Sarvam. "
            "Requires AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT and "
            "AZURE_OPENAI_DEPLOYMENT environment variables."
        ),
    )
    args = parser.parse_args()

    # This prompts you to enter your question.
    print("Chatbot initialized. Enter your question.")
    user_input = input("You: ").strip()

    if user_input:
        try:
            if args.use_azure:
                # Use Azure OpenAI for LLM inference.
                bot_response = get_chat_response_azure(user_input)
            else:
                if not args.api_key:
                    parser.error("--api-key is required when not using --use-azure")
                # This calls the function to get the bot's response.
                bot_response = get_chat_response(args.api_key, user_input)
            # This prints the bot's response.
            print(f"Bot: {bot_response}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

# This ensures that the main() function is called when the script is run directly.
if __name__ == "__main__":
    main()