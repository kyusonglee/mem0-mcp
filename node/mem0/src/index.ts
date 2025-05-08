import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { MemoryClient } from 'mem0ai';

const MEM0_API_KEY = process?.env?.MEM0_API_KEY || '';

// Initialize mem0ai client
const memoryClient = new MemoryClient({ apiKey: MEM0_API_KEY });

// Create server instance
const server = new McpServer({
  name: "mem0-robot-navigation",
  version: "1.0.0",
  capabilities: {
    resources: {},
    tools: {},
  },
});

// Default robot user ID
const ROBOT_USER_ID = 'navigation-robot';

// Helper function to add memories
async function addMemory(content: string, userId: string = ROBOT_USER_ID) {
  try {
    const messages = [
      { role: "system", content: "Robot navigation memory system" },
      { role: "user", content }
    ];
    await memoryClient.add(messages, { user_id: userId });
  } catch (error) {
    console.error("Error adding memory:", error);
  }
}

// Helper function to search memories
async function searchMemories(query: string, userId: string = ROBOT_USER_ID) {
  try {
    const results = await memoryClient.search(query, { user_id: userId });
    return results;
  } catch (error) {
    console.error("Error searching memories:", error);
    return [];
  }
}

// Robot observation tools
server.tool(
  "store-robot-observation",
  "Store observations from a navigation robot. This tool captures detailed descriptions of what the robot observes in the real world, including visual information, spatial data, and environmental conditions.",
  {
    observation: z.string().describe("Detailed description of what the robot observes in the environment"),
    metadata: z.object({
      location: z.string().optional().describe("Current location or coordinates"),
      timestamp: z.string().optional().describe("Time of observation"),
      environmentalConditions: z.string().optional().describe("Lighting, weather, etc."),
    }).optional().describe("Additional metadata about the observation"),
    userId: z.string().default(ROBOT_USER_ID).describe("User ID for robot memory storage"),
  },
  async ({ observation, metadata, userId }) => {
    const formattedObservation = metadata 
      ? `Observation: ${observation}\nLocation: ${metadata.location || 'unknown'}\nTimestamp: ${metadata.timestamp || new Date().toISOString()}\nConditions: ${metadata.environmentalConditions || 'not specified'}`
      : observation;
    
    await addMemory(formattedObservation, userId);
    return {
      content: [
        {
          type: "text",
          text: "Robot observation stored successfully",
        },
      ],
    };
  },
);

server.tool(
  "search-robot-observations",
  "Search through stored robot observations. Use this to recall information about the environment, objects, or locations the robot has previously observed.",
  {
    query: z.string().describe("Search query describing what information to retrieve from robot observations"),
    userId: z.string().default(ROBOT_USER_ID).describe("User ID for robot memory storage"),
  },
  async ({ query, userId }) => {
    const results = await searchMemories(query, userId);
    const formattedResults = results.map((result: any) => 
      `Observation: ${result.memory}\nRelevance: ${result.score}\n---`
    ).join("\n");

    return {
      content: [
        {
          type: "text",
          text: formattedResults || "No relevant observations found",
        },
      ],
    };
  },
);

server.tool(
  "detect-environment-changes",
  "Compare current observation with previous observations at the same location to detect changes in the environment.",
  {
    currentObservation: z.string().describe("The current observation to compare against previous ones"),
    location: z.string().describe("The location identifier where this observation was made"),
    userId: z.string().default(ROBOT_USER_ID).describe("User ID for robot memory storage"),
  },
  async ({ currentObservation, location, userId }) => {
    // First store the current observation
    const timestamp = new Date().toISOString();
    const formattedObservation = `Observation: ${currentObservation}\nLocation: ${location}\nTimestamp: ${timestamp}`;
    await addMemory(formattedObservation, userId);
    
    // Then search for previous observations at this location
    const query = `What did I previously observe at location ${location}?`;
    const results = await searchMemories(query, userId);
    
    // Filter out the current observation if it was just added and found
    const previousObservations = results.filter((result: any) => 
      !result.memory.includes(currentObservation.substring(0, 50))
    );
    
    if (previousObservations.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: `No previous observations found at ${location}. This is new territory.`,
          },
        ],
      };
    }
    
    const response = {
      currentObservation,
      location,
      timestamp,
      previousObservations: previousObservations.slice(0, 2).map((result: any) => ({
        observation: result.memory,
        relevance: result.score
      }))
    };
    
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(response, null, 2),
        },
      ],
    };
  },
);

server.tool(
  "build-spatial-map",
  "Build a spatial map from stored observations, organizing memories by location to create a mental model of the environment.",
  {
    userId: z.string().default(ROBOT_USER_ID).describe("User ID for robot memory storage"),
  },
  async ({ userId }) => {
    // Get all memories for this user (would be better with pagination in a real implementation)
    try {
      const allMemories = await memoryClient.get_all({ user_id: userId, page: 1, page_size: 50 });
      
      // Organize memories by location
      const locationMap: Record<string, any[]> = {};
      
      allMemories.results.forEach((memoryItem: any) => {
        const memory = memoryItem.memory;
        
        // Try to extract location from the memory
        let location = 'unknown';
        const locationMatch = memory.match(/Location: ([^\n]+)/i);
        if (locationMatch && locationMatch[1]) {
          location = locationMatch[1];
        }
        
        if (!locationMap[location]) {
          locationMap[location] = [];
        }
        
        locationMap[location].push(memory);
      });
      
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ 
              spatialMap: locationMap,
              locationCount: Object.keys(locationMap).length,
              totalObservations: allMemories.results.length
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      console.error("Error building spatial map:", error);
      return {
        content: [
          {
            type: "text",
            text: "Error building spatial map. Please try again.",
          },
        ],
      };
    }
  },
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Robot Navigation Memory MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});