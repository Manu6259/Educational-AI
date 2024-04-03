import subprocess
import os

def download_media_from_youtube(youtube_url, download_path=".", ffmpeg_path="C:/ffmpeg/bin"):
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

def main(youtube_url):
    print("Downloading media from YouTube...")
    audio_file, video_file = download_media_from_youtube(youtube_url)

    print(f"Audio File: {audio_file}\nVideo File: {video_file}")

    print("Transcribing audio with Whisper...")
    transcribe_audio_with_whisper(audio_file)

    print("Transcription completed.")

if __name__ == "__main__":
    youtube_url = input("Enter the YouTube URL: ")
    main(youtube_url)
