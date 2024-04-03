from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
import pandas as pd
import subprocess
import os
import sys
import csv
import re

def download_media_from_youtube(youtube_url, download_path=".", ffmpeg_path="/usr/bin/ffmpeg"):
    audio_output_file = os.path.join(download_path, "audio11.wav")
    video_output_file = os.path.join(download_path, "video11.mp4")
    
    # Download audio
    audio_command = [
        'yt-dlp',
        '-x',  # Extract audio only
        '--audio-format', 'wav',
        '--ffmpeg-location', ffmpeg_path,
        '-o', audio_output_file,
        youtube_url
    ]
    subprocess.run(audio_command, check=True)
    
    # Download video
    video_command = [
        'yt-dlp',
        '-f', 'best',  # Download the best quality available
        '--ffmpeg-location', ffmpeg_path,
        '-o', video_output_file,
        youtube_url
    ]
    subprocess.run(video_command, check=True)
    
    return audio_output_file, video_output_file

def transcribe_audio_with_whisper(audio_file, model_size="base", language="English"):
    # Command to run Whisper for transcription
    command = [
        'whisper', 
        audio_file, 
        '--language', language, 
        '--model', model_size
    ]
    subprocess.run(command)

def transcription(youtube_url):
    print("Downloading media from YouTube...")
    audio_file, video_file = download_media_from_youtube(youtube_url)

    print(f"Audio File: {audio_file}\nVideo File: {video_file}")

    print("Transcribing audio with Whisper...")
    transcribe_audio_with_whisper(audio_file)

    print("Transcription completed.")

 
def validate_file(file_path):
    """
    Validates if the provided file path is an existing SRT file.
    """
    if not os.path.isfile(file_path):
        print(f"The file {file_path} does not exist.")
        sys.exit(1)
    if not file_path.lower().endswith('.srt'):
        print("The file is not a valid SRT file.")
        sys.exit(1)
 
def read_srt(file_path):
    """
    Reads the content of the SRT file, preserving its structure.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()
 
def write_txt(content, file_path):
    """
    Creates a new TXT file and writes the SRT content to it with the required formatting.
    """
    new_file_path = file_path.rsplit('.', 1)[0] + '.txt'
    with open(new_file_path, 'w', encoding='utf-8') as file:
        entry = []
        for line in content:
            if line.strip().isdigit():
                if entry:
                    file.write('\n'.join(entry) + '\n\n')
                    entry = []
                entry.append(line.strip())
            elif '-->' in line:
                entry.append(line.strip() + ' ')
            else:
                if line.strip():  # This avoids writing blank lines within subtitle entries
                    entry.append(line.strip())
        if entry:  # Write the last entry if the file doesn't end with a newline
            file.write('\n'.join(entry) + '\n')
    return new_file_path

def convert_srt_to_txt(file_path):
    """
    Converts an SRT file to a TXT file, handling errors gracefully.
    """
    try:
        validate_file(file_path)
        content = read_srt(file_path)
        new_file_path = write_txt(content, file_path)
        print(f"Conversion successful. TXT file created at {new_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

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

def summarized_text(file_path, output_file_path):
    """
    Orchestrates the process of reading a transcript and generating learning activities,
    then writes the activities to a specified text file.
    """
    transcript = read_transcript_from_file(file_path)
    activities = generate_learning_activities(transcript)
    write_output_to_file(activities, output_file_path)
    print(f"Suggested Learning Activities written to {output_file_path}")


def parse_chapter_info_from_file(input_file_path):
    # Read the contents of the file
    with open(input_file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Regular expression to capture the relevant chapter details
    chapter_pattern = re.compile(
        r'Chapter (\d+) - (.*?)\s*'  # Capture chapter number and title
        r'Chapter Start time - (.*?)\s*'  # Capture start time
        r'Chapter End Time - (.*?)\s*'  # Capture end time
        r'Chapter Description - (.*?)\s*'  # Capture description
        r'Chapter Question - (.*?)\s*'  # Capture question
        r'(?=Chapter|$)',  # Lookahead for start of next chapter or end of string
        re.DOTALL  # Dot matches newline as well
    )

    return chapter_pattern.findall(text)

def write_to_csv(chapters, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Chapter No.', 'Chapter Name', 'Chapter Start time', 'Chapter End Time', 'Chapter Description', 'Chapter Question']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for chapter in chapters:
            # Dictionary comprehension to convert each tuple to a dictionary with the right keys
            writer.writerow({
                'Chapter No.': chapter[0],
                'Chapter Name': chapter[1],
                'Chapter Start time': chapter[2],
                'Chapter End Time': chapter[3],
                'Chapter Description': chapter[4],
                'Chapter Question': chapter[5]
            })

def main():
    # The path to the input file uploaded by the user
    input_file_path = 'learning_activities.txt'  # This will be replaced by the path of the uploaded file
    
    # Parse the chapter information from the file
    chapters = parse_chapter_info_from_file(input_file_path)
    
    # Specify the path to save the output CSV file
    output_csv_path = 'chapter_details_from_file.csv'
    
    # Write the chapter information to a CSV file
    write_to_csv(chapters, output_csv_path)
    
    # Output the path to the created CSV file
    return output_csv_path

# Run the main function and get the path to the output CSV file


# Read the CSV file



if __name__ == "__main__":
    # Creating the transcript
    youtube_url = input("Enter the YouTube URL: ")
    transcription(youtube_url)

    # Converting .srt to text file
    if len(sys.argv) > 1:
        input_file_path = sys.argv[1]
    else:
        input_file_path = input("Please enter the path to the SRT file: ")
    convert_srt_to_txt(input_file_path)

    #Calling OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    file_path = "audio11.txt"  # Path to your transcript file
    output_file_path = "learning_activities.txt"  # Desired path for the output file
    summarized_text(file_path, output_file_path)

    # Run the main function and get the path to the output CSV file
    output_csv_file_path = main()


    data = pd.read_csv(output_csv_file_path)

    # Define the font and font size
    font = ImageFont.truetype('arial.ttf', 24)

    for index, row in data.iterrows():
        # Define the image size
        width, height = 1500, 1500

        # Create a new image with a white background
        image = Image.new('RGB', (width, height), color='white')

        # Create a draw object
        draw = ImageDraw.Draw(image)

        # Get the data from the CSV row
        chapter_number = row['Chapter No.']
        chapter_name = row['Chapter Name']
        chapter_question = row['Chapter Question']

        # Draw the text on the image
        draw.text((10, 10), f"Chapter {chapter_number}: {chapter_name}", font=font, fill='black')
        draw.text((10, 40), f"Question: {chapter_question}", font=font, fill='black')

        # Save the image
        image.save(f'chapter_{chapter_number}.png')

