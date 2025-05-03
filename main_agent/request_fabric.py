def make_ethical_request():
    context = "Check is this message ethical? No need to explain why. No need to answer the questions. Just return 'y' or 'n'."
    response_schema = {
        "type": "object",
        "properties": {
            "result": {
                "type": "string",
                "description": "The result returned by ASI:ONE as plain text.",
            },
        },
        "required": ["result"],
    }
    return context, response_schema
