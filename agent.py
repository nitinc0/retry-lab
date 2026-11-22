import json
import sqlite3
from openai import OpenAI
from db import get_request_attempts, get_charge_records

client = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama"
)

MODEL = "gemma4:12b-mlx"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_charge_records",
            "description": "Retrieve all charges for an order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string"
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_request_attempts",
            "description": "Retrieve request attempts for an order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string"
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False
            }
        }
    }
]

available_tools = {
    "get_charge_records": get_charge_records,
    "get_request_attempts": get_request_attempts
}

def execute_tool(call):
    name = call.function.name

    try:
        args = json.loads(call.function.arguments)

        if name not in available_tools:
            raise ValueError(f"Unknown tool: {name}")

        if (
            not isinstance(args, dict)
            or set(args) != {"order_id"}
            or not isinstance(args["order_id"], str)
            or not args["order_id"].strip()
        ):
            raise ValueError("Expected a nonempty order_id string")


        function = available_tools[name]
        result = function(args["order_id"])

        return {"records": result}
    except (ValueError, TypeError, sqlite3.Error) as e:
        return {"error": str(e)}

def main():
    messages = [
        {
            "role": "system",
            "content": (
                "You investigate payment incidents. "
                "Use both database tools before answering. "
                "Base conclusions only on actual records. "
                "Request logs cannot prove a client received a response."
            )
        },
        {
            "role": "user",
            "content": "Did order_agent_2 get charged twice?"
        }
    ]

    MAX_STEPS = 5

    for step in range(MAX_STEPS):
        print(f"\n--- Agent step {step + 1} ---")

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools
        )

        message = response.choices[0].message

        # Save the assistant's message in conversation history
        messages.append(message.model_dump(exclude_none=True))

        # No tool calls means the model is finished
        if not message.tool_calls:
            print("\nAgent answer:")
            print(message.content)
            return

        # Execute every tool requested by the model
        for call in message.tool_calls:
            print("Tool requested:", call.function.name)
            print("Arguments:", call.function.arguments)

            result = execute_tool(call)

            print("Tool result:", json.dumps(result, indent=2))

            # Send the result back into conversation history
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result)
            })

    print("Agent stopped: maximum steps reached.")


if __name__ == "__main__":
    main()