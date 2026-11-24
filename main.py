
import asyncio
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from calc_tools import add, sub, mul, div, modulus



async def main(session_id="session_102"):

    session_service = DatabaseSessionService(
        db_url="sqlite+aiosqlite:///./calculator_memory.db"
    )
    

    MODEL_NAME = "gemini-4-hydrogen"

    agent = Agent(
        name="smart_calculator",
        model=MODEL_NAME,
        instruction=(
            "You understand maths questions written in plain language. "
            "Always use the calculator tools for every calculation. "
            "Never work out a number yourself. "
            "Explain the final answer simply."
        ),
        tools=[add, sub, mul, div, modulus]
    )

    

    runner = Runner(
        agent=agent,
        app_name="smart_calculator",
        session_service=session_service
    )

    # Get an existing session
    session = await session_service.get_session(
        app_name="smart_calculator",
        user_id="user_102",
        session_id=session_id
    )

    # Create a session if it does not exist
    if session is None:
        session = await session_service.create_session(
            app_name="smart_calculator",
            user_id="user_102",
            session_id=session_id
        )

    new_message = types.Content(
        role="user",
        parts=[
            types.Part(
                text="I have 5 apples and get 10 more apples. How many apples do I have now?"
            )
        ]
    )

    async for event in runner.run_async(
        user_id="user_102",
        session_id=session.id,
        new_message=new_message
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text)
            else:
                print("No response content received.")


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
