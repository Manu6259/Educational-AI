import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# Read the CSV file
data = pd.read_csv('chapter_details_from_file.csv')

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