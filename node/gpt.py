from openai import OpenAI
import json

client = OpenAI()

# given a topic/article as a string, it returns 5 dimensions to rate the topic on in the form of a string array e.g.
# returns ["x","y","z","a","b"]
def getKeys(topic):
    messages = [
        {"role": "system", "content": "You are an analyst that rates subjects on 5 arbitrary dimensions, that you "
                                      "come up with yourself, based on the information provided to you. These 5 "
                                      "dimensions are on a 0-1 scale. The only thing I want returned are the 5 "
                                      "dimension that the topic provided by the user will be rated on. Format it in "
                                      "a JSON array, with only the dimension."},
        {"role": "user", "content": topic}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
    )
    response_message = response.choices[0].message
    return response_message.content


# given 5 dimensions and articles, this function returns the ratings for the dimensions e.g.
# returns {"x": 0.9, "y": 0.8, "z": 0.7, "a": 0.2, "b": 0.85}
def getValues(dimensions, article):
    messages = [
        {"role": "system", "content": 'You are an analyst that rates subjects on 5 dimensions that are provided to you as a string array, with each string being a dimension. The subject that you will be rating will be provided to you. These 5 dimensions are on a 0-1 scale. The only thing I want returned are the 5 dimensions that the topic provided by the user will be rated on and their respective values. Format it as a JSON. The prompt will be of the format: "Dimensions: (the array of strings that are the dimensions), Article: (the subject)"'},
        {"role": "user", "content": f'Dimensions: {dimensions}, Article: {article}'}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
    )
    response_message = response.choices[0].message
    return response_message.content


# THESE TESTS COST MONEY
# keys = ["Sweetness", "Taste", "Flavor variety", "Guilt", "Texture"]
# result = getValues(keys, "I love icecream.")
# print(result)