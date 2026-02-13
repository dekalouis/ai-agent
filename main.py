import os
import argparse 
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from call_function import available_functions, call_function


load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")


def main():
    # print("Hello from ai-agent!")
    if api_key is None:
        raise RuntimeError('Do not forget to add your API key.')
    client = genai.Client(api_key=api_key)

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    # 1. Start with initial messages
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    # Model calling logic:
    # 2. Loop for a set number of times
    for _ in range(20):
        # 3. Call the model with the current history
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=messages, 
            config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt)
        )
        # 4. Save the model's response to history
        for candidate in response.candidates:
            messages.append(candidate.content)

        if response.usage_metadata is None:
            raise RuntimeError('Failed API request.')

        if args.verbose:
            print(f'User prompt: {args.user_prompt}')
            print(f'Prompt tokens: {response.usage_metadata.prompt_token_count}')
            print(f'Response tokens: {response.usage_metadata.candidates_token_count}')

        function_calls = response.function_calls
        function_results = []

        # 5. Check if the model wants to call tools
        if function_calls:
            # 6. Execute tools and get results
            for function_call in function_calls:
                # print(f"Calling function: {function_call.name}({function_call.args})")
                
                function_call_result = call_function(function_call, args.verbose)

                if not function_call_result.parts:
                    raise Exception('Parts is empty')
                if not function_call_result.parts[0].function_response:
                    raise Exception('Parts is empty')
                if not function_call_result.parts[0].function_response.response:
                    raise Exception('Parts is empty')

                function_results.append(function_call_result.parts[0])

                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
                
            # 7. Add results to history so the model sees them in the next loop
            messages.append(types.Content(
                role="user",
                parts=function_results
            ))

        else:
            # 8. If no tools, we are done!
            print("Final response:")
            print(response.text)
            return response.text
    print('Error: Maximum iterations reached')
    sys.exit(1)


if __name__ == "__main__":
    main()
