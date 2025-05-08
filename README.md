# Navigation Robot Memory System with mem0

This repository contains a mem0-based memory system for navigation robots. It provides tools for robots to store and retrieve observations about their environment, detect changes, and build mental maps.

## Overview

The system uses [mem0](https://mem0.ai/) to provide long-term memory capabilities for navigation robots. This allows robots to:

1. **Store observations** about their environment
2. **Retrieve relevant information** using natural language queries  
3. **Detect changes** in previously visited locations
4. **Build mental maps** of their surroundings

## Components

### Python Implementation

- `main.py`: Contains the MCP server and mem0 client tools
  - `store_robot_observation`: Stores observations with location context
  - `search_robot_observations`: Retrieves observations using semantic search
  - `detect_environment_changes`: Compares current and previous observations to detect changes

### Node.js Implementation

- `node/mem0/src/index.ts`: Contains the TypeScript implementation of the memory tools
  - `store-robot-observation`: Stores observations with metadata (location, timestamp, etc.)
  - `search-robot-observations`: Performs semantic search over stored observations
  - `detect-environment-changes`: Identifies differences between observations
  - `build-spatial-map`: Organizes memories by location to create a mental model

### Examples

- `robot_example.py`: Basic example demonstrating observation storage and retrieval
- `robot_navigation.py`: Advanced simulation showing:
  - Recording observations with location context
  - Retrieving memories about objects and locations
  - Change detection in the environment
  - Building mental maps
  - Revisiting locations and handling dynamic environments

## Usage

### Starting the Server

Run the MCP server:

```bash
python main.py --host 0.0.0.0 --port 8080
```

### Running the Examples

```bash
# Simple example
python robot_example.py

# Advanced navigation simulation
python robot_navigation.py
```

### Building Node.js Implementation

```bash
cd node/mem0
npm install
npm run build
```

## Integrating with Your Robot

To use mem0 with your navigation robot:

1. Import the memory functions:
   ```python
   from main import store_robot_observation, search_robot_observations, detect_environment_changes
   ```

2. Store observations when your robot sees something:
   ```python
   result = await store_robot_observation(
       f"I see a table and chair. My location is {location}. Time: {timestamp}"
   )
   ```

3. Retrieve relevant memories:
   ```python
   memories = await search_robot_observations("Where did I see a chair?")
   ```

4. Detect changes when revisiting locations:
   ```python
   changes = await detect_environment_changes(
       "The room now has a plant that wasn't here before", 
       "living_room"
   )
   ```

## NavigationRobot Class

The `NavigationRobot` class in `robot_navigation.py` provides a complete framework for a robot with memory capabilities:

```python
robot = NavigationRobot(robot_id="my_robot")

# Store observations
await robot.observe_environment("kitchen", "I see a refrigerator and table")

# Find objects
await robot.look_for_object("refrigerator")

# Navigate using memories
success = await robot.navigate_to("kitchen")

# Detect changes
changes = await robot.detect_changes("kitchen", "The table now has plates on it")

# Build a mental map
mental_map = await robot.build_mental_map()
```

## Requirements

- Python 3.8+
- Node.js 16+ (for TypeScript implementation)
- mem0 API access
- dotenv for environment variables

## Configuration

Set your mem0 API key in a `.env` file:

```
MEM0_API_KEY=your_api_key_here
```

## License

MIT

