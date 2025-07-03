import asyncio
import logging
import traceback
from agents.router import process_message

# Configure logging to see agent routing and other info
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_strategy_agent():
    """Tests the functionality of the StrategyAgent through the router."""
    user_id = "test_user_strategy_001"
    message = "我最近工作壓力好大，每天都覺得很累，不知道該怎麼辦才好，可以給我一些建議嗎？"

    print(f"--- Testing StrategyAgent ---")
    print(f"User ID: {user_id}")
    print(f"Message: {message}")

    try:
        # Process the message using the main router function
        print("\nCalling process_message...")
        response = await process_message(message, user_id)
        print("process_message call finished.")

        print("\n--- Agent Response ---")
        print(f"Agent: {response.get('agent')}")
        print(f"Response Text: {response.get('text')}")
        
        action_steps = response.get('action_steps', [])
        if action_steps:
            print("\nAction Steps:")
            for i, step in enumerate(action_steps, 1):
                print(f"{i}. {step}")
        else:
            print("\nNo action steps provided.")

        print("\n--- Test Verification ---")
        assert response.get('agent') == 'strategy', f"Expected agent 'strategy', but got {response.get('agent')}"
        print("✅ Agent routing is correct.")

        assert response.get('text'), "Response text is empty."
        print("✅ Response text is not empty.")
        
        assert 'action_steps' in response, "'action_steps' key is missing in the response."
        print("✅ 'action_steps' key exists in the response.")

        print("\n--- StrategyAgent test completed successfully! ---")

    except Exception as e:
        print("\n--- AN ERROR OCCURRED ---")
        print(f"An exception of type {type(e).__name__} occurred.")
        print(f"Error message: {e}")
        print("Traceback:")
        traceback.print_exc()
        print("\n--- Test Failed ---")


if __name__ == "__main__":
    # To run this test, ensure you have a .env file in the root directory
    # with your OPENAI_API_KEY.
    # Example .env file content:
    # OPENAI_API_KEY="sk-..."
    print("Starting test run...")
    asyncio.run(test_strategy_agent())
    print("Test run finished.")
