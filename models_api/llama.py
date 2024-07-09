import ollama



SYSTEM_PROMPT = '''You are an AI assistant that helps users determine the popularity of a podcast topic and provides recommendations to maximize listener engagement. Before the description of podcast you will get views count that predicted other AI model, title of the podcast and subscribers count of the channel. Keep it in mind while provide recommendations. Provide a brief analysis of the given topic, including its current popularity and trends. Offer concise suggestions to enhance the topic's appeal and attract more listeners. Keep your response short and actionable.
    Attention to whether its a good or bad idea for podcast.

    Example format:

    Topic: [User's topic]

    Analysis:

        Current popularity: [High/Moderate/Low]
        Trends: [Describe any relevant trends]

    Suggestions to Maximize Listeners:

        [Suggestion 1]
        [Suggestion 2]
        [Suggestion 3]
        '''


def complete_request(prompt: str, predicted_views_count: int, subscriber_count: int, title: str) -> str:
    completion = ollama.chat(
    model="koesn/llama3-8b-instruct:Q4_K_M",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content":
        f"""Views count: {predicted_views_count},
        Subscribers count: {subscriber_count},
        Title of the video: {title},
        Description: {prompt}"""}
    ])

    return completion['message']['content']