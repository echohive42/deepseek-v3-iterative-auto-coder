import os
from openai import OpenAI
from termcolor import termcolor

# Constants
USER_PROMPT = "a pygame tower defense game with only in game assets"  # Default empty string for user input
SYSTEM_PROMPT = """You are a Python code generator. Return all code in between <code> and </code> tags.
Make sure the code is well-documented, follows best practices, and is ready to use. You must return the code in between <code> and </code> tags. do not use ```python or ```"""
MODEL = "deepseek/deepseek-chat"
OUTPUT_DIR = "generated_code"

try:
    # Initialize OpenAI client
    print(termcolor.colored("Initializing OpenAI client...", "cyan"))
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(termcolor.colored(f"Created output directory: {OUTPUT_DIR}", "green"))

    def extract_code(response_text):
        """Extract code from between <code> and </code> tags."""
        try:
            start_tag = "<code>"
            end_tag = "</code>"
            start_index = response_text.find(start_tag) + len(start_tag)
            end_index = response_text.find(end_tag)
            
            if start_index == -1 or end_index == -1:
                raise ValueError("Code tags not found in response")
                
            return response_text[start_index:end_index].strip()
        except Exception as e:
            print(termcolor.colored(f"Error extracting code: {str(e)}", "red"))
            return None

    def generate_code(prompt):
        """Generate code using the DeepSeek model with streaming response."""
        try:
            print(termcolor.colored("Generating code...", "yellow"))
            print(termcolor.colored(f"Using prompt: {prompt}", "cyan"))
            stream = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            
            # Collect the full response while streaming
            full_response = ""
            print(termcolor.colored("\nStreaming response:", "cyan"))
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            print("\n")  # New line after streaming
            code = extract_code(full_response)
            
            if code:
                # Save the code to a file
                filename = f"{OUTPUT_DIR}/generated_code_{len(os.listdir(OUTPUT_DIR)) + 1}.py"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(code)
                print(termcolor.colored(f"Code successfully generated and saved to: {filename}", "green"))
                return code
            else:
                print(termcolor.colored("No code was found in the response", "red"))
                return None
                
        except Exception as e:
            print(termcolor.colored(f"Error generating code: {str(e)}", "red"))
            return None

    if __name__ == "__main__":
        print(termcolor.colored(f"Using prompt: {USER_PROMPT}", "cyan"))
        generated_code = generate_code(USER_PROMPT)
        
        if generated_code:
            print(termcolor.colored("\nExtracted Code:", "green"))
            print(generated_code)

except Exception as e:
    print(termcolor.colored(f"Initialization error: {str(e)}", "red")) 