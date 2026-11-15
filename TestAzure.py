from openai import OpenAI

client = OpenAI(
    base_url="https://mtaha.azure-api.net/openai/v1",
    api_key="unused",
    default_headers={
        "Ocp-Apim-Subscription-Key": "55cbd69fa11541b8bcdb36a88e7dd1a7"
    },
)


response = client.responses.create(
    model="gpt-6-astra",
    input="What is the capital of France?",

)

print(response.output_text)