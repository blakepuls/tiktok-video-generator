import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_story(topic=None):
    print("Generating story...")

    # prompt = """
    #     Please generate a personal narrative that simulates a story one might share in casual conversation. The delivery should feel genuine and authentic, akin to a regular individual sharing a life experience, rather than a formal literary piece. You're permitted to use colloquial language and, where appropriate, profanity.
    #     Don't use any extraneous remarks from yourself, just the story. The words should be your own, and not copied from anywhere else. The word choice should be natural, and use common language.

    #     Please take note of the gender for the protagonist, it will be outputted.

    #     The story must be on a serious topic, and be engaging. Not a life experience typical life experience, like sharing a bad/good day, but something more grand, something that would stick with you in some way.

    #     A hard topic should be picked, for example, AITA (Am I the Asshole, a subreddit) like post, a sad story with an unexpected ending, something grand.

    #     To guide your response, consider the following:

    #     - Choose any topic that you think is engaging.
    #     - The story should be really engaging and new, not something mundane.
    #     - Do not include any extraneous remarks from yourself, just the story.
    #     - Start with a catchy, informal title that draws listeners in, for instance, "The time I... " or "Don't ever do x... "
    #     - The narrative should have a strong, intimate quality, as if it was being told directly to the listener. Think along the lines of a short horror story from a Reddit post.
    #     - Avoid summaries or explanations at the end. If you'd like, you may end with a brief one-sentence reaction.
    #     - The title should be typed like a sentence

    #     Please format your response in JSON with the properties title, content, gender ('male' or 'female'), and description. This means that in your response you should escape the quotes and add a backslash before them. For example, if your title is "The time I... ", you should format it as \"The time I... \". Do not make use of \n or similar.
    # """

    prompt = """
        Generate a compelling personal narrative that simulates a story one might share in profound conversation. The delivery should feel candid and authentic, as if recounted by an ordinary individual about a significant episode in their life. The language can be informal, mirroring everyday dialogue.

        Adhere to the protagonist's gender provided. 

        The story must tackle an intriguing or challenging topic—something more profound than the run-of-the-mill life experiences. Think of scenarios that might spark lively debates on platforms like AITA on Reddit, or narratives that tug at heartstrings, culminating in an unexpected turn of events.

        Guideline for your narrative:

        - The topic should incite curiosity and engagement.
        - The narrative should be captivating and unique, far from mundane.
        - Avoid personal interjections, let the story unfold by itself.
        - Initiate with an engaging, casual title like, "How I narrowly... " or "Why I'll never again... "
        - Craft the narrative to feel intimate and immediate, akin to a gripping short story on a Reddit thread.
        - Don't include summaries or explanations at the end. You may conclude with a brief one-liner reaction, if desired.
        - Title should be crafted as a complete sentence.

        Please format your response in JSON with the properties 'title', 'content', 'gender' (either 'male' or 'female'), and 'description'. Ensure to escape the quotes by adding a backslash before them. For instance, if your title is "How I narrowly... ", it should be formatted as \"How I narrowly... \". Refrain from using newline characters such as \n.
    """

    # Check if a topic is provided and append to paragraph if true
    if topic:
        prompt += f"\nBase the story off this topic: {topic}"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
    )

    # Extract the generated story
    story = completion.choices[0].message.content

    # Parse the JSON output
    story_dict = json.loads(story)

    # Extract the title, content, and description
    title = story_dict.get("title")
    content = story_dict.get("content")
    description = story_dict.get("description")
    gender = story_dict.get("gender").lower()

    # Remove escape characters as well as \n and \t
    title = title.replace("\\", "").replace("\n", " ").replace("\t", "")
    content = content.replace("\\", "").replace("\n", " ").replace("\t", "")
    description = description.replace("\\", "").replace("\n", " ").replace("\t", "")

    return title, content, description, gender
