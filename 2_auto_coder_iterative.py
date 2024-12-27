import os
import subprocess
import time
from openai import OpenAI
from termcolor import colored

# Constants
USER_PROMPT = "a pygame tower defense game with only in game assets"  # Default empty string for user input
SYSTEM_PROMPT_GENERATE = """You are a Python code generator. Return all code in between <code> and </code> tags.
Make sure the code is well-documented, follows best practices, and is ready to use. You must return the code in between <code> and </code> tags. do not use ```python or ```"""
SYSTEM_PROMPT_FIX = """You are a Python code error fixer. Analyze the error output and fix the code. Return the fixed code between <code> and </code> tags.
Do not refer to previous conversations or context. Focus only on fixing the current error."""
SYSTEM_PROMPT_IMPROVE = """You are a Python code improver. Analyze the working code and add more features or improvements. Return the improved code between <code> and </code> tags.
Do not refer to previous conversations or context. Focus only on improving the current code with new features."""
MODEL = "deepseek/deepseek-chat"
OUTPUT_DIR = "generated_code"
MAX_ITERATIONS = 5  # Maximum number of improvement iterations
EXECUTION_TIMEOUT = 5  # Maximum execution time in seconds

try:
    # Initialize OpenAI client
    print(colored("Initializing OpenAI client...", "cyan"))
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(colored(f"Created output directory: {OUTPUT_DIR}", "green"))

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
            print(colored(f"Error extracting code: {str(e)}", "red"))
            return None

    def execute_code(filename):
        """Execute the generated code with timeout and capture output."""
        try:
            print(colored(f"\nExecuting {filename}...", "yellow"))
            process = subprocess.Popen(
                ["python", filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=EXECUTION_TIMEOUT)
                
                # Print raw output first
                print(colored("\nRaw subprocess output:", "cyan"))
                print("=" * 50)
                if stdout:
                    print(stdout, end="")
                if stderr:
                    print(stderr, end="")
                print("=" * 50)
                
                # Format output for model consumption
                execution_output = "=" * 50 + "\n"
                if stdout.strip():
                    execution_output += colored("STDOUT:", "cyan") + "\n" + stdout + "\n"
                if stderr.strip():
                    execution_output += colored("STDERR:", "red") + "\n" + stderr + "\n"
                execution_output += "=" * 50
                
                # Only consider actual errors, not timeouts
                has_errors = bool(stderr.strip()) or "error" in stdout.lower() or "exception" in stdout.lower()
                return execution_output, has_errors
                
            except subprocess.TimeoutExpired:
                process.kill()
                msg = f"Code execution timed out after {EXECUTION_TIMEOUT} seconds (this is not considered an error)"
                print(colored(msg, "yellow"))
                # Return timeout message but has_errors=False since timeouts are not errors
                return msg, False
                
        except Exception as e:
            error_msg = f"Error executing code: {str(e)}"
            print(colored(error_msg, "red"))
            return error_msg, True

    def generate_initial_code(prompt):
        """Generate initial code using the DeepSeek model."""
        try:
            print(colored("\nGenerating initial code...", "yellow"))
            stream = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_GENERATE},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            
            full_response = ""
            print(colored("\nStreaming response:", "cyan"))
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            print("\n")  # New line after streaming
            return extract_code(full_response)
                
        except Exception as e:
            print(colored(f"Error generating initial code: {str(e)}", "red"))
            return None

    def fix_code(code, error_output):
        """Fix code errors using a fresh API call."""
        try:
            print(colored("\nFixing code errors...", "yellow"))
            stream = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_FIX},
                    {"role": "user", "content": f"Here is the code with errors:\n{code}\n\nError output:\n{error_output}\n\nPlease fix the code."}
                ],
                stream=True
            )
            
            full_response = ""
            print(colored("\nStreaming response:", "cyan"))
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            print("\n")  # New line after streaming
            return extract_code(full_response)
                
        except Exception as e:
            print(colored(f"Error fixing code: {str(e)}", "red"))
            return None

    def improve_code(code):
        """Improve working code using a fresh API call."""
        try:
            print(colored("\nImproving code...", "yellow"))
            stream = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_IMPROVE},
                    {"role": "user", "content": f"Here is the working code to improve:\n{code}\n\nPlease add more features or improvements."}
                ],
                stream=True
            )
            
            full_response = ""
            print(colored("\nStreaming response:", "cyan"))
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            print("\n")  # New line after streaming
            return extract_code(full_response)
                
        except Exception as e:
            print(colored(f"Error improving code: {str(e)}", "red"))
            return None

    def save_code(code, iteration):
        """Save code to a file."""
        try:
            filename = f"{OUTPUT_DIR}/generated_code_{iteration}.py"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code)
            print(colored(f"Code saved to: {filename}", "green"))
            return filename
        except Exception as e:
            print(colored(f"Error saving code: {str(e)}", "red"))
            return None

    def iterative_code_generation(prompt):
        """Run the iterative code generation process with separate API calls for fixes and improvements."""
        iteration = 1
        
        # Generate initial code
        current_code = generate_initial_code(prompt)
        if not current_code:
            return
        
        filename = save_code(current_code, iteration)
        if not filename:
            return
            
        while iteration <= MAX_ITERATIONS:
            print(colored(f"\nIteration {iteration}/{MAX_ITERATIONS}", "yellow"))
            
            # Execute current code
            execution_output, has_errors = execute_code(filename)
            
            # If code timed out but didn't have errors, try to improve it
            if "timed out" in execution_output.lower():
                print(colored("\nCode timed out but no errors found. Attempting to improve efficiency...", "yellow"))
                improved_code = improve_code(current_code)
                
                if improved_code and improved_code != current_code:
                    iteration += 1
                    current_code = improved_code
                    filename = save_code(current_code, iteration)
                    if not filename:
                        break
                else:
                    print(colored("\nNo improvements made for timeout.", "yellow"))
                    break
            
            # If no errors, try to improve the code
            elif not has_errors:
                print(colored("\nNo errors found. Attempting to improve code...", "green"))
                improved_code = improve_code(current_code)
                
                if improved_code and improved_code != current_code:
                    iteration += 1
                    current_code = improved_code
                    filename = save_code(current_code, iteration)
                    if not filename:
                        break
                else:
                    print(colored("\nNo further improvements needed.", "green"))
                    break
            
            # If there are errors, try to fix them
            else:
                print(colored("\nErrors found. Attempting to fix code...", "yellow"))
                fixed_code = fix_code(current_code, execution_output)
                
                if fixed_code:
                    iteration += 1
                    current_code = fixed_code
                    filename = save_code(current_code, iteration)
                    if not filename:
                        break
                else:
                    print(colored("Failed to fix code. Stopping iterations.", "red"))
                    break
            
            if iteration > MAX_ITERATIONS:
                print(colored(f"\nReached maximum iterations ({MAX_ITERATIONS})", "yellow"))
                break

    if __name__ == "__main__":
        print(colored(f"Using prompt: {USER_PROMPT}", "cyan"))
        iterative_code_generation(USER_PROMPT)

except Exception as e:
    print(colored(f"Initialization error: {str(e)}", "red")) 