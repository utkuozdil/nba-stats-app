from functools import wraps


def cors(origin="*"):
    def decorator(func):
        @wraps(func)
        def wrapper(event, context):
            # Call the original function
            response = func(event, context)

            # Ensure response is a dictionary
            if not isinstance(response, dict):
                raise TypeError("Response must be a dictionary")

            # Add CORS headers
            headers = response.get("headers", {})
            headers.update({
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            })
            response["headers"] = headers

            # Handle OPTIONS preflight requests
            if event.get("httpMethod") == "OPTIONS":
                response["statusCode"] = 200
                response["body"] = ""

            return response

        return wrapper

    return decorator
