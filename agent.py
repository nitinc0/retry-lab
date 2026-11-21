import json

from openai import OpenAI

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



def main():
    messages = [
        {
            "role": "system",
            "content": (
                "You investigate payment incidents. "
                "Use database tools to find evidence. "
                "Never invent charge records."
            )
        },
        {
            "role": "user",
            "content": "Did order_agent_2 get charged twice?"
        }
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools
    )

    message = response.choices[0].message

    if message.tool_calls:
        for call in message.tool_calls:
            print("Tool requested:", call.function.name)
            print("Arguments:", json.loads(call.function.arguments))
    else:
        print("Model answered without a tool:", message.content)

    print(message)


if __name__ == "__main__":
    main()