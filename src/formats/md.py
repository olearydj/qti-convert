"""
Markdown format
"""

import re
import string

import html2text
from logzero import logger

import config


def write_file(data, outfile):
    """
    markdown output, handles only standard multiple choice questions now
    image support is untested
    complex question text (e.g. multi-line with code blocks) is not handled
    """
    markdown_list = []
    text_maker = html2text.HTML2Text()

    for assessment in data['assessment']:
        # Adding Title
        assessment_title = f"# {assessment['metadata']['title']}\n"
        logger.info(f"Writing assessment: {repr(assessment_title)}")
        markdown_list.append(assessment_title)
        
        # Adding Description
        description = assessment['metadata'].get('description') or ''

        if description:
            description = text_maker.handle(description).rstrip('\n') + "  \n"
            logger.info(f"  with description: {repr(description)}")
            markdown_list.append(description)
        else:
            logger.debug("  with no description")
        
        # with open('questions.py', 'w') as f:
        #     f.write(json.dumps(assessment['question'], indent=4))

        # rprint(assessment['question'])
        # [
        #     {
        #         'id': 'gf56cf4328c0179fdd7419b86337a9551',
        #         'title': 'Question',
        #         'question_type': 'multiple_choice_question',
        #         'points_possible': '1.0',
        #         'text': '<div>Which code example is an expression?</div>',
        #         'answer': [
        #             {'id': '4346', 'text': '# calculate area', 'correct': False, 'display': True},
        #             {'id': '3471', 'text': 'area = pi * (radius ** 2)', 'correct': False, 'display': True},
        #             {'id': '1385', 'text': 'print(area)', 'correct': False, 'display': True},
        #             {'id': '8820', 'text': 'input("what is the radius?")', 'correct': True, 'display': True}
        #         ]
        #     },
        # ...
        # ]

        for q_num, question in enumerate(assessment['question']):
    
            if question['question_type'] in ["multiple_dropdowns_question", "matching_question", "calculated_question"]:
                logger.warning(f"Question type {question['question_type']} not yet supported")

            else:
                # Adding Question Title
                if 'title' in question:
                    question_title = f"\n## {question['title']} {q_num+1}\n\n" 
                    logger.info(f"Writing question titled: {repr(question_title)}")
                    markdown_list.append(question_title)
                else:
                    logger.debug(f"No title in question {q_num+1}")
                    
                # Adding Images
                if 'image' in question:
                    logger.info(f"Adding images to question {q_num+1}")
                    for img in question['image']:
                        markdown_list.append(f"![Image]({img['href'].replace('%20', ' ')})")
                else:
                    logger.debug(f"No images in question {q_num+1}")
                                
                # Adding Question Text
                if 'text' in question and question['text'] is not None:
                    this_question_text = re.sub('</*tbody>', '', question['text'])  # See https://github.com/pqzx/html2docx/issues/1
                    handled_text = text_maker.handle(this_question_text).strip() + "\n\n"
                    logger.info(f"Adding text to question {q_num+1}: {repr(handled_text)}")
                    markdown_list.append(handled_text)

                    # find correct answer
                    for answer in question['answer']:
                        if 'correct' in answer and answer['correct']:
                            logger.debug(f"contents of correct field: {repr(answer['correct'])}")
                            logger.debug(f"type of correct field: {type(answer['correct'])}")
                            correct_answer_id = answer['id']
                            logger.info(f"Correct answer ({correct_answer_id}): {answer['text']}")
                        else:
                            logger.warning(f"No correct answer found in question {q_num+1}")

                else:
                    logger.debug(f"No text in question {q_num+1}")
                
                if 'answer' in question:
                    """
                    implement `matching_question` next, other types aren't used
                    will need to make sure formatting here matches what is required by text2qti
                    """
                    logger.info(f"Adding answers to question {q_num+1}, type: {question['question_type']}")
                    for index, answer in enumerate(question['answer']):
                        if answer['display']:
                            # For displaying the index and images in Markdown
                            if 'image' in answer:
                                logger.debug(f"Adding images to answer {index+1}")
                                for img in answer['image']:
                                    # Assuming that img['href'] contains the link to the image
                                    markdown_list.append(f"{index+1}. \n![Image]({img['href'].replace('%20', ' ')})")
                            else:
                                logger.debug(f"No images in answer {index+1}")
                            
                            # Add answer index and text
                            if 'text' in answer and answer['text'] is not None:
                                alphabet_index = string.ascii_lowercase[index]
                                text = answer['text']
                                logger.info(f"Answer text: {repr(text)}")

                                handled_text = text_maker.handle(text).strip()
                                logger.info(f"Handled text: {repr(handled_text)}")

                                code_block_pattern = r'`([\s\S]*?)`'
                                cleaned_text = re.sub(code_block_pattern, lambda m: '`' + m.group(1).strip() + '`', handled_text) + "  \n"
                                
                                # flag correct answer choice
                                if answer['id'] == correct_answer_id:
                                    alphabet_index = "*" + alphabet_index
                                logger.info(f"Cleaned text added: {alphabet_index}: {repr(cleaned_text)}")
                                markdown_list.append(f"{alphabet_index}) {cleaned_text}")
                            else:
                                logger.warning(f"No text in answer {alphabet_index}")
                        
                        else:
                            markdown_list.append(config.blanks_replace_str * config.blanks_answer_n)

    # Writing the Generated Markdown to a File
    with open(outfile, 'w') as md_file:
        md_file.write(''.join(markdown_list))

    print("wrote markdown")

    return

    # based on code from docx.py; the following bits are not yet converted
    for assessment in data['assessment']:
        doc.add_heading(assessment['metadata']['title'], 0)
        for question in assessment['question']:
            if 'answer' in question:
                if question['question_type'] == "multiple_dropdowns_question":
                    for aindex, group in enumerate(question['answer']):
                        options = []
                        for option in group['options']:
                            if option['display']:
                                if 'text' in answer and option['text'] != None:
                                    options.append(option['text'])
                                else:
                                    options.append("---")
                        doc.add_paragraph(str(aindex+1) + ": " + ", ".join(map(str, options)))
                elif question['question_type'] == "matching_question":
                    table = doc.add_table(rows=1, cols=2)
                    for index, answer in enumerate(question['answer']):
                        cell_0 = table.cell(0, 0)
                        if 'image' in answer:
                            for img in answer['image']:
                                cell_0.add_picture(img['href'].replace("%20", " "), height=Mm(10))
                        if 'text' in answer and answer['text'] != None:
                            cell_0.text = cell_0.text + ("\n" if cell_0.text != "" else "") + answer['text']
                        if index == 0:
                            cell_1 = table.cell(0, 1)
                            for option in answer['options']:
                                if 'image' in option:
                                    for img in option['image']:
                                        cell_1.add_picture(img['href'].replace("%20", " "), height=Mm(10))
                                if 'text' in option and option['text'] != None:
                                    cell_1.text = cell_1.text + ("\n" if cell_1.text != "" else "") + option['text']
                elif question['question_type'] == "calculated_question":
                    if config.calculated_display_var_set_in_text:
                        doc.add_paragraph(config.blanks_replace_str * config.blanks_answer_n)
                    else:
                        for index, answer in enumerate(question['answer']):
                            if answer['display'] and 'text' in answer and answer['text'] != None:
                                html_parser.add_html_to_document("<p>" + str(index+1) + ". " + answer['text'] + ": " + config.blanks_replace_str * 20 + "</p>", doc)

            doc.add_page_break()
