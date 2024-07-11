def main(): 
    import re
    import stanza
    from util import (
        plural_to_singular,
        enhance_entities,
        process_string,
        get_rid_of,
        extract_relationships,
        associate_entities_attr,
        get_primary_keys,
        merge_db_attr_with_text_attr,
        process_relations,
        add_missing_fk,
        find_and_merge_tuples,
        filtering,
        last_filtering,
        remove_third_element_and_convert_to_set,
        create_django_project,
        predict_entities_and_attributes,
        extract_top_attributes,
        create_database_tables
    )

    nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse')

    description=''' Consider the following set of requirements for a UNIVERSITY database that is used to keep track of students’ transcripts.The university keeps track of each student name, student number, Social Security number, current address and phone number, permanent address , birth date, sex, class, major department, minor department and program . Some user applications need to refer to the city, state, and ZIP Code of the student’s permanent address and to the student’s last name. Both Social Security number and student number have unique values for each student.
    Each department is described by a name, department code, office number and college. Both name and code have unique values for each
    department.
    Each course has a course name, description, course number, number of
    semester hours, level, and offering department. The value of the course number
    is unique for each course.
    Each section has an instructor, semester, year, course, and section number. The
    section number distinguishes sections of the same course that are taught during
    the same semester per year its values are up to the number of sections
    taught during each semester.
    A grade report has a student, section, letter grade, and numeric grade.
    ''' 

    # entities_snake_case,attributes_snake_case=predict_entities_and_attributes(description)

    entities_snake_case= ['university', 'university', 'user_applications', 'student’s_permanent', 'student', 'department', 'both', 'course', 'course_number', 'course', 'section', 'distinguishes_sections', 'sections', 'semester', 'grade_report']
    attributes_snake_case= ['student_name', 'student_number', 'social_security', 'current_address', 'phone_number', 'permanent_address', 'birth_date', 'sex', 'class', 'major_department', 'minor_department', 'program', 'city', 'state', 'zip_code', 'student’s', 'last_name', 'social_security', 'student_number', 'name', 'department_code', 'office_number', 'college', 'name', 'code', 'department', 'course_name', 'description', 'course_number', 'number_of', 'level', 'offering_department', 'instructor', 'semester', 'year', 'course', 'section_number', 'year', 'student', 'section', 'grade']
    
    attributes_final=list(set(attributes_snake_case))
    ent_array_sing = [plural_to_singular(ent) for ent in entities_snake_case]
    ent_array=list(set(ent_array_sing))

    ent_array,attributes_final = enhance_entities(description, ent_array, attributes_final)

    doc = nlp(description)

    nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse',tokenize_pretokenized=True)

    description=description.replace(',',' , ').replace('’s','').replace("'s","").replace("'","")
    description = re.sub(r'\s+', ' ', description)
    desc_sents=description.split('.')
    description=''
    for sent in desc_sents:
        if sent.strip()!='':
            description+=sent.strip()+' .\n'

    doc=nlp(description)

    doc = process_string(doc, ent_array, attributes_final)

    get_rid_of(doc,ent_array)

    relationships = extract_relationships(doc, ent_array)

    entity_attributes_map =extract_top_attributes(ent_array)

    entities_with_attr = associate_entities_attr(doc, ent_array, attributes_final, relationships, entity_attributes_map)

    entities_with_pks,entities_with_attr=get_primary_keys(doc,entities_with_attr,entity_attributes_map)

    merge_db_attr_with_text_attr(entity_attributes_map,entities_with_attr)

    updated_relations = process_relations(relationships)

    all_modified_sentences_relations=add_missing_fk(updated_relations,entities_with_pks)

    one_array_relations= [item for sublist in all_modified_sentences_relations for item in sublist]

    merged_relations = find_and_merge_tuples(one_array_relations)

    merged_relations2 = filtering(merged_relations)

    merged_relations_3 = last_filtering(merged_relations2)

    relationships = remove_third_element_and_convert_to_set(merged_relations_3)

    create_database_tables(entities_with_attr, entities_with_pks, relationships)

    create_django_project()

if __name__ == "__main__":
    main()