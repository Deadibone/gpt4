from gradio_client import Client
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
import time

def format_context(context):
    """Formats the previous conversation into a structured string for context awareness."""
    return ' '.join(f"**You**: {turn[0]}\n**Bot**: {turn[1]}" for turn in context)

# Initialize the client with the specific model's endpoint
client = Client("yuntian-deng/ChatGPT4Turbo")

# Initialize conversation parameters
chat_counter = 0
chatbot_context = []
console = Console()

# Display welcome message only once
welcome_message = Markdown("### ChatGPT4 Turbo, client by yuntian-deng. Platform by Relboss(aka Deadibone)\nType 'exit' to end the chat.")
console.print(welcome_message)

try:
    while True:
        # Capture user input
        user_input = input("\nYou: ").strip()

        # End the chat loop
        if user_input.lower() == 'exit':
            confirm_exit = input("Are you sure you want to exit? (yes/no): ").strip().lower()
            if confirm_exit == 'yes':
                break
            else:
                continue
        
        if not user_input:
            console.print(Panel("Please enter a valid message.", title="Error", border_style="red"))
            continue

        # Add timeout/retry logic
        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                # Prepare input context
                input_context = format_context(chatbot_context)
                full_input = f"{input_context}\n**You**: {user_input}"
                
                # Make the predict API call
                response = client.predict(
                    inputs=full_input,
                    top_p=1.0,
                    temperature=1.0,
                    chat_counter=chat_counter + 1,
                    chatbot=[],
                    api_name="/predict_1"
                )

                # Extract response components
                chatbot_responses, chat_counter, status_code, meta_info = response

                # Process the response safely
                if (chatbot_responses and isinstance(chatbot_responses, list) 
                    and len(chatbot_responses[-1]) > 1):
                    main_response = chatbot_responses[-1][1]
                    
                    # Update chat context
                    chatbot_context.append((user_input, main_response))

                # Clear the console and print the entire chat history again
                console.clear()
                console.print(welcome_message)
                
                # Print all previous messages except the last input and response
                for user_msg, bot_msg in chatbot_context[:-1]:  # Exclude the last message
                    console.print(Panel(f"{user_msg}", title="Your Input", border_style="green"))
                    console.print(Panel(Markdown(f"{bot_msg}"), title="Bot Response", border_style="cyan"))

                # Print the latest user input and bot response
                console.print(Panel(f"{user_input}", title="Your Input", border_style="green"))
                console.print(Panel(Markdown(f"{main_response}"), title="Bot Response", border_style="cyan"))

                break  # Exit retry loop on success
        
            except Exception as e:
                console.print(Panel(f"Attempt {attempt + 1} failed with error: {e}", title="Error", border_style="red"))
                if attempt < retry_attempts - 1:
                    time.sleep(1)  # Wait before retrying

except Exception as e:
    console.print(Panel(f"An error occurred: {e}", title="Error", border_style="red"))
    input("Press Enter to exit...")  # Pause to view the error

finally:
    console.print(Panel("Chatbot session ended, bye!", title="Session End", border_style="red"))