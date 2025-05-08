#!/usr/bin/env python3
"""
Advanced example of a navigation robot that uses mem0 for memory.
This example simulates a robot that navigates through an environment,
records observations, and uses those memories to build a mental map.
"""

import asyncio
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dotenv import load_dotenv

# Import mem0 client tools
from main import store_robot_observation, search_robot_observations, detect_environment_changes

load_dotenv()

class NavigationRobot:
    """A simulated navigation robot that uses mem0 for memory storage and retrieval."""
    
    def __init__(self, robot_id: str = "nav_robot_1"):
        """Initialize the navigation robot.
        
        Args:
            robot_id: Unique identifier for this robot
        """
        self.robot_id = robot_id
        self.current_location: Optional[str] = None
        self.visited_locations: List[str] = []
        self.environment_map: Dict[str, Dict] = {}
        self.detected_changes: Dict[str, List[Dict]] = {}
        
    async def observe_environment(self, location: str, observation: str) -> str:
        """Record an observation at the current location.
        
        Args:
            location: Current location identifier
            observation: The observation text
            
        Returns:
            Result of storing the observation
        """
        self.current_location = location
        if location not in self.visited_locations:
            self.visited_locations.append(location)
            
        # Add metadata to the observation
        timestamp = datetime.now().isoformat()
        full_observation = (
            f"{observation} "
            f"My current location is {location}. "
            f"Observation time: {timestamp}."
        )
        
        # Store observation in mem0
        result = await store_robot_observation(full_observation)
        return result
        
    async def recall_observation(self, query: str) -> List[Dict]:
        """Recall a previous observation based on a query.
        
        Args:
            query: Search query
            
        Returns:
            List of relevant memories
        """
        result = await search_robot_observations(query)
        try:
            memories = json.loads(result)
            return memories
        except json.JSONDecodeError:
            print(f"Error parsing result: {result}")
            return []
    
    async def detect_changes(self, location: str, observation: str) -> Dict[str, Any]:
        """Detect changes in the environment from previous observations.
        
        Args:
            location: Current location identifier
            observation: Current observation text
            
        Returns:
            Dictionary containing change detection results
        """
        result = await detect_environment_changes(observation, location)
        try:
            changes = json.loads(result)
            # Store changes in the robot's memory
            if location not in self.detected_changes:
                self.detected_changes[location] = []
            self.detected_changes[location].append({
                "timestamp": datetime.now().isoformat(),
                "changes": changes
            })
            return changes
        except json.JSONDecodeError:
            print(f"Error parsing change detection result: {result}")
            return {"error": "Failed to parse change detection results"}
    
    async def navigate_to(self, target_location: str) -> bool:
        """Navigate to a specific location.
        
        Args:
            target_location: The location to navigate to
            
        Returns:
            True if navigation was successful
        """
        # Check if we know about this location
        query = f"What do I know about location {target_location}?"
        memories = await self.recall_observation(query)
        
        if not memories:
            print(f"I don't have any memories about {target_location}")
            return False
        
        # Use the memories to navigate
        print(f"Navigating to {target_location} using my memories:")
        for memory in memories[:2]:  # Show just the top 2 relevant memories
            print(f"- Using memory: {memory[:100]}...")
        
        # Update current location
        self.current_location = target_location
        if target_location not in self.visited_locations:
            self.visited_locations.append(target_location)
            
        print(f"Successfully navigated to {target_location}")
        return True
    
    async def look_for_object(self, object_name: str) -> List[Dict]:
        """Search for an object in the robot's memories.
        
        Args:
            object_name: The object to search for
            
        Returns:
            List of memories about the object
        """
        query = f"Where can I find {object_name}?"
        memories = await self.recall_observation(query)
        
        if memories:
            print(f"I found information about {object_name}:")
            for i, memory in enumerate(memories[:3]):  # Show top 3 results
                print(f"{i+1}. {memory}")
        else:
            print(f"I don't have any memories about {object_name}")
            
        return memories
    
    async def build_mental_map(self) -> Dict:
        """Build a mental map from all stored observations.
        
        Returns:
            A dictionary representing the robot's mental map
        """
        # For each visited location, get the most relevant memory
        mental_map = {}
        
        for location in self.visited_locations:
            query = f"What do I know about location {location}?"
            memories = await self.recall_observation(query)
            
            if memories:
                # Use the top memory for this location
                mental_map[location] = {
                    "description": memories[0],
                    "objects": [],
                    "changes_detected": location in self.detected_changes,
                    "visits": self.detected_changes.get(location, [])
                }
                
                # Try to extract objects from the memory
                object_query = f"What objects did I see in {location}?"
                object_memories = await self.recall_observation(object_query)
                
                if object_memories:
                    # Extract object references from the memory
                    mental_map[location]["objects"] = object_memories
        
        return mental_map
    
    def get_status(self) -> Dict:
        """Get the current status of the robot.
        
        Returns:
            Dictionary with robot status information
        """
        return {
            "robot_id": self.robot_id,
            "current_location": self.current_location,
            "visited_locations": self.visited_locations,
            "locations_count": len(self.visited_locations),
            "changes_detected": len(self.detected_changes)
        }


# Example environment for simulation
EXAMPLE_ENVIRONMENT = {
    "Room A": {
        "description": "A large room with white walls. There's a desk in the corner with a computer and some books. There are two doors, one leading north and one east.",
        "objects": ["desk", "computer", "books", "doors"]
    },
    "Room B": {
        "description": "A narrow hallway with blue carpeting. There are doors on both sides with room numbers. At the end is a water fountain.",
        "objects": ["doors", "water fountain", "room numbers"]
    },
    "Room C": {
        "description": "A kitchen area with a refrigerator, microwave, and a table with four chairs. There's a window showing it's daytime outside and a coffee machine on the counter.",
        "objects": ["refrigerator", "microwave", "table", "chairs", "window", "coffee machine"]
    },
    "Room D": {
        "description": "An office space with three desks in an open layout. Each desk has a monitor and keyboard. There's a whiteboard on the wall with some diagrams drawn on it.",
        "objects": ["desks", "monitors", "keyboards", "whiteboard", "diagrams", "potted plant"]
    },
    "Room E": {
        "description": "A conference room with a large oval table and 8 chairs. There's a projector mounted on the ceiling and a projection screen. The room has no windows.",
        "objects": ["table", "chairs", "projector", "screen", "water pitcher"]
    }
}

# Modified environment to simulate changes
CHANGED_ENVIRONMENT = {
    "Room A": {
        "description": "A large room with white walls. There's a desk in the corner with a computer and some books. Someone has added a new chair by the desk. The doors are the same as before.",
        "objects": ["desk", "computer", "books", "doors", "chair"]
    },
    "Room C": {
        "description": "A kitchen area with a refrigerator, microwave, and a table with four chairs. The window shows it's now nighttime outside. The coffee cup that was on the table is now gone, and someone left a newspaper.",
        "objects": ["refrigerator", "microwave", "table", "chairs", "window", "coffee machine", "newspaper"]
    },
    "Room E": {
        "description": "A conference room with a large oval table and 8 chairs. There's a projector mounted on the ceiling and a projection screen. The room has no windows. Someone is having a meeting, with a laptop connected to the projector.",
        "objects": ["table", "chairs", "projector", "screen", "water pitcher", "laptop", "people"]
    }
}

async def run_simulation():
    """Run a simulation of the robot navigating through the environment."""
    robot = NavigationRobot()
    
    print("=== Starting Robot Navigation Simulation ===")
    print("Initializing robot and having it explore the environment...")
    
    # Explore the environment
    for location, info in EXAMPLE_ENVIRONMENT.items():
        print(f"\n> Robot is exploring {location}")
        result = await robot.observe_environment(
            location, 
            info["description"]
        )
        print(f"  Observation stored: {result}")
        await asyncio.sleep(1)  # Pause between observations to avoid rate limiting
    
    print("\n=== Robot has completed its initial exploration ===")
    print(f"Robot status: {robot.get_status()}")
    
    # Test the robot's memory
    print("\n=== Testing Robot's Memory and Navigation ===")
    
    # Look for objects
    objects_to_find = ["coffee machine", "water fountain", "whiteboard", "projector"]
    for obj in objects_to_find:
        print(f"\n> Looking for {obj}...")
        await robot.look_for_object(obj)
        await asyncio.sleep(1)
    
    # Navigate to locations
    locations_to_visit = random.sample(list(EXAMPLE_ENVIRONMENT.keys()), 3)
    for location in locations_to_visit:
        print(f"\n> Attempting to navigate to {location}...")
        success = await robot.navigate_to(location)
        if success:
            print(f"  Current location: {robot.current_location}")
        await asyncio.sleep(1)
    
    # Simulate environment changes and detect them
    print("\n=== Simulating Changes in the Environment ===")
    locations_with_changes = list(CHANGED_ENVIRONMENT.keys())
    for location in locations_with_changes:
        print(f"\n> Robot revisits {location} and notices changes")
        
        # First navigate to the location
        await robot.navigate_to(location)
        
        # Detect changes
        print(f"  Detecting changes in {location}...")
        changes = await robot.detect_changes(
            location,
            CHANGED_ENVIRONMENT[location]["description"]
        )
        
        print(f"  Change detection results for {location}:")
        if "error" in changes:
            print(f"  Error: {changes['error']}")
        elif "previous_observations" in changes and changes["previous_observations"]:
            print(f"  Found differences between current and previous observations")
            
        await asyncio.sleep(1)
    
    # Build a mental map
    print("\n=== Building Mental Map from Memories ===")
    mental_map = await robot.build_mental_map()
    print(f"Mental map contains {len(mental_map)} locations")
    for location, data in mental_map.items():
        print(f"\n{location}:")
        print(f"  Description: {data['description'][:100]}...")
        print(f"  Objects: {', '.join(str(obj) for obj in data['objects'][:3])}" 
              if data['objects'] else "  No objects identified")
        if data["changes_detected"]:
            print(f"  Changes detected: Yes - {len(data['visits'])} observations")
    
    print("\n=== Final Robot Status ===")
    status = robot.get_status()
    print(f"Robot ID: {status['robot_id']}")
    print(f"Current location: {status['current_location']}")
    print(f"Visited locations: {', '.join(status['visited_locations'])}")
    print(f"Total locations visited: {status['locations_count']}")
    print(f"Locations with changes detected: {status['changes_detected']}")
    
    print("\n=== Simulation Complete ===")

if __name__ == "__main__":
    asyncio.run(run_simulation()) 