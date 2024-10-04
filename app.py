import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Initialize the current image index
current_image_index = 0

# Path to the input JSON file containing image data
input_json_file_path = 'input_data.json'

# Path to the response JSON file where user responses will be stored
response_json_file_path = 'responses.json'

# Load the image filenames
image_folder = 'static/images'
to_image_folder = 'static/images_done'
image_filenames = os.listdir(image_folder)

@app.route('/')
def index():
    global current_image_index

    # Get the current image filename
    current_image_filename = image_filenames[current_image_index]

    # Load data from the input JSON file
    with open(input_json_file_path, 'r') as json_file:
        data_entries = json.load(json_file)
    
    # Find the corresponding entry for the current image
    paragraphs = {'exp1': '', 'exp2': '', 'exp3': '', 'exp4': ''}
    for entry in data_entries:
        if entry.get('filename') == current_image_filename:
            paragraphs = {
                'exp1': entry.get('exp1', ''),
                'exp2': entry.get('exp2', ''),
                'exp3': entry.get('exp3', ''),
                'exp4': entry.get('exp4', ''),
            }
            break

    return render_template('index.html', image_filename=current_image_filename, paragraphs=paragraphs)

@app.route('/save_data', methods=['POST'])
def save_data():
    global current_image_index

    # Get the form data
    data = {
        # 'paragraph_1': request.form.get('paragraph_1'),
        # 'paragraph_2': request.form.get('paragraph_2'),
        # 'paragraph_3': request.form.get('paragraph_3'),
        # 'paragraph_4': request.form.get('paragraph_4'),
        'filename': request.form.get('image_filename'),  # Store the image filename
        'responses': []  # List to hold question responses
    }

    # Capture Q1 to Q20 responses
    for i in range(1, 21):  # Questions 1 to 20
        question_response = {}
        question_response['question'] = "Question_" + str(i)
        
        if i%5 in (1, 2):
            # For Q1-Q10: 5 radio buttons
            question_response['answer'] = request.form.get(f'q{i}')
        elif i%5 in (3, 4):  
            # For Q11-Q12: 2 radio buttons + textbox
            question_response['answer'] = {
                'response': request.form.get(f'q{i}'),
                'text': request.form.get(f'q{i}_text')
            }
        elif i%5 == 0: 
            # For Q13: 8 radio buttons with multi-select
            question_response['answer'] = request.form.getlist(f'q{i}_options')
        
        data['responses'].append(question_response)

    # Capture Q21 to Q24 responses
    for i in range(21, 25):  # Questions 21 to 24
        question_response = {}
        question_response['question'] = "Question_" + str(i)        
        if i in (21, 22):
            # For Q21-Q22: Ranking options
            question_response['answer'] = request.form.get(f'q{i}_ranking')
        else:
            # For Q23-Q24: Detailed feedback
            question_response['answer'] = request.form.get(f'q{i}_feedback')

        data['responses'].append(question_response)

    # Append the data to the response JSON file
    with open(response_json_file_path, 'a') as json_file:
        json.dump(data, json_file)
        json_file.write('\n')  # New line for each entry

    curr_path = os.path.join(image_folder, image_filenames[current_image_index])
    new_path = os.path.join(to_image_folder, image_filenames[current_image_index])
    os.rename(curr_path, new_path)

    # Move to the next image
    current_image_index = (current_image_index + 1) % len(image_filenames)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
