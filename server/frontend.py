from ret import *
def frontendfunction(description, color):
    data=[]
    data,label_to_folder =collect_all_data()
    folders=classify(data,description,label_to_folder)
    top_folder = top(folders)
    trans(top_folder)
    extracted_details = extract_details_advanced(description)
    user_feedback = None  # Placeholder for actual feedback mechanism
    updated_details = collect_feedback(description, extracted_details, user_feedback)
    html_file_path=paths("9")
    readandwrite(html_file_path,updated_details)
    css_files = get_linked_css_files(html_file_path)
    modifyallcss("9",css_files,color)
    