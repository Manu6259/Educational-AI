from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_transcript_from_file(file_path):
    """
    Reads the transcript text from a given file path.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        transcript = file.read()
    return transcript

def generate_learning_activities(transcript):
    """
    Sends a transcript to ChatGPT to generate ideas for fun learning activities.
    """
    prompt_text = transcript[:min(len(transcript), 2048)]  # Adjust based on your token budget
    messages = [
    {
        "role": "system",
        "content": "You are a helpful chapter generator for video transcripts. Your task is to analyze the transcript content and identify changes in topic or content to generate chapters. For each identified chapter, generate a concise and descriptive chapter title or summary that captures the main topic or content of that chapter. Additionally, generate up to one question related to the content of each chapter to encourage critical thinking and understanding. Present the output in the following format without any special characters or formatting: 'Chapter No. -', 'Chapter Name -', 'Chapter Start time -', 'Chapter End Time -', 'Chapter Description -', 'Chapter Question -'. Ensure that each chapter detail is clearly separated and presented in a straightforward manner."
    },
    {
        "role": "user",
        "content": f"Based on the following transcript, generate chapter titles, descriptions, questions, and the requested information in the specified format:\n\n{prompt_text}"
    }]

    
    response = client.chat.completions.create(model="gpt-4-turbo-preview",
    messages=messages,
    temperature=0.5,
    max_tokens=1000,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0)
    
    if response.choices and len(response.choices) > 0:
        last_message = response.choices[0].message.content
        return last_message.strip()
    else:
        return "No activities could be generated."

def write_output_to_file(activities, output_file_path):
    """
    Writes the generated learning activities to a specified text file.
    
    Args:
    - activities (str): The generated activities to write.
    - output_file_path (str): The path of the output text file.
    """
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(activities)

def main(file_path, output_file_path):
    """
    Orchestrates the process of reading a transcript and generating learning activities,
    then writes the activities to a specified text file.
    """
    transcript = read_transcript_from_file(file_path)
    activities = generate_learning_activities(transcript)
    write_output_to_file(activities, output_file_path)
    print(f"Suggested Learning Activities written to {output_file_path}")

if __name__ == "__main__":
    file_path = "audio11.txt"  # Path to your transcript file
    output_file_path = "learning_activities.txt"  # Desired path for the output file
    main(file_path, output_file_path)
