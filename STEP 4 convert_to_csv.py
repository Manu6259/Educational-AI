import csv
import re

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
output_csv_file_path = main()
output_csv_file_path
