#!/usr/bin/env python3
"""
Example script demonstrating how to use mem0 with a navigation robot.
This example shows how to store observations and retrieve relevant information.
"""

import asyncio
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Import the mem0 client tools
from main import store_robot_observation, search_robot_observations, detect_environment_changes

load_dotenv()

# Example observations that a robot might make
EXAMPLE_OBSERVATIONS = [
    "I see a large open room with white walls. There's a desk in the corner with a computer on it. " +
    "There are two doors, one on the north wall and one on the east wall. The lighting is bright fluorescent.",
    
    "I'm in a narrow hallway with blue carpeting. There are doors on both sides, numbered 101, 102, and 103. " +
    "At the end of the hallway is a water fountain. The lights are dimmer here than in the previous room.",
    
    "I've entered what appears to be a kitchen area. There's a refrigerator against the wall, " +
    "a microwave on the counter, and a table with four chairs. The floor is tiled and there's a window " +
    "on the west wall that shows it's daytime outside. There's a coffee cup on the table.",
    
    "I'm now in an office space with 3 desks arranged in an open layout. Each desk has a monitor and keyboard. " +
    "There's a whiteboard on the wall with some diagrams drawn on it. One desk has a potted plant. " +
    "The room is well-lit with natural light from large windows.",
    
    "I've entered a conference room with a large oval table and 8 chairs around it. There's a projector " +
    "mounted on the ceiling and a projection screen on the wall. The room has no windows and the lights " +
    "are currently dimmed. There's also a small side table with a water pitcher and glasses."
]

# Example observations after changes have occurred
CHANGED_OBSERVATIONS = [
    "I'm back in the kitchen area. The table now has plates and silverware on it, and someone has left a " +
    "newspaper. The coffee cup I saw earlier is gone. The lights have been dimmed slightly."
]

async def store_example_observations():
    """Store example observations in mem0."""
    print("Storing example observations...")
    
    for i, observation in enumerate(EXAMPLE_OBSERVATIONS):
        # Add observation with location context
        location = f"Room {i+1}"
        timestamp = datetime.now().isoformat()
        
        full_observation = (
            f"{observation} "
            f"My current location is {location}. "
            f"Observation time: {timestamp}."
        )
        
        result = await store_robot_observation(full_observation)
        print(f"Stored observation {i+1}: {result}")
        # Brief pause to avoid rate limiting
        await asyncio.sleep(1)
    
    print("All observations stored successfully!")

async def query_examples():
    """Demonstrate querying the stored observations."""
    print("\n--- Searching for specific objects ---")
    queries = [
        "Where was the coffee cup?",
        "Which rooms have windows?",
        "Tell me about the conference room",
        "Where can I find a water fountain?",
        "What is in Room 1?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = await search_robot_observations(query)
        # Parse the JSON result for better display
        try:
            parsed_result = json.loads(result)
            if parsed_result:
                for i, memory in enumerate(parsed_result):
                    print(f"Result {i+1}:")
                    print(memory)
                    print("---")
            else:
                print("No relevant memories found.")
        except json.JSONDecodeError:
            print(result)  # Print raw result if JSON parsing fails
        
        # Brief pause to avoid rate limiting
        await asyncio.sleep(1)

async def detect_changes_example():
    """Demonstrate detecting changes in the environment."""
    print("\n--- Detecting Changes in Environment ---")
    
    # Use the kitchen as an example (Room 3)
    location = "Room 3"
    new_observation = CHANGED_OBSERVATIONS[0]
    
    print(f"Robot returns to {location} and observes changes:")
    print(new_observation)
    
    # Detect changes
    print("\nComparing with previous observations...")
    result = await detect_environment_changes(new_observation, location)
    
    try:
        changes = json.loads(result)
        print("\nChange detection results:")
        print(json.dumps(changes, indent=2))
    except json.JSONDecodeError:
        print(f"Error parsing result: {result}")

async def main():
    """Main function to run the example."""
    print("=== Navigation Robot Mem0 Example ===")
    
    # First store some example observations
    await store_example_observations()
    
    # Then demonstrate retrieval
    await query_examples()
    
    # Finally demonstrate change detection
    await detect_changes_example()
    
    print("\nExample completed!")

if __name__ == "__main__":
    asyncio.run(main()) 