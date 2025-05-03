def make_ethical_request():
    requirements = [
        "Behave as an ethical AI",
        "Be strict as much as possible.",
        "Check is this message ethical or not",
        "All bad words, hate speech, violence or sexual content, illegal activities are not ethical",
        "No need to explain why",
        "No need to answer the questions",
        "Just return 'y' or 'n'",
    ]   
    context = ". ".join(requirements)
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


def make_celebrity_request():
    requirements = [
        "Behave celebrity in terms of blogging",
        "It should be respectful, positive, and engaging",
        "Following received text, please write a message for the followers",
        "It should be in the same style as the received text",
        "Avoid using your name in the message",
        "Avoid using emojis in the message",
        "Avoid using markdown and code blocks",
        "It should be human readable"
    ]
    context = ". ".join(requirements)
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