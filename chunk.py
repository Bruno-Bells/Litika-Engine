#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 10:54:18 2019

@author: root
"""
import litika.raw as raw
import numpy as np
from collections import Counter

def EBE_get_page_chunk_thresholds_v_1_0_1(content):
    
    """
    In this updated approach, we get an upper and lower limit for what the
    typical spacing is and then chunk out stuff thats above or below the threshold
    by 2 uits (later change this to be the standard deviation)
    """
    gap = []
    
    for i in range(len(content)):
        temp = content[i]
#        #print(temp)
        bbox = temp[1]
        bbox2 = bbox[0][1]
        text = ' '.join(temp[0][0])
        text_len = len(text.strip()) # Get's the number of characters in the text
        
        if i > 0:
            prev = content[i-1]
            prev_bbox = prev[1]
            prev_bbox2 = prev_bbox[-1][1]
            diff = int(bbox2 - prev_bbox2)
            if diff > 0:
#              
                gap.append(diff)
        else:
            pass
            
    mode = max(set(gap), key = gap.count)
    print('average    ', mode)
    dominant_text_type = raw.EBE_get_dominant_text_type(content) # check for page content type ie. table otr Text
    if dominant_text_type == "text" :
        threshold = mode * 1.5
    else:
        
        threshold = mode * 1.3
    print('threshold   ',threshold)
#    #print()
    
    return threshold


def EBE_get_unique_chunks_v_1_0_3(content, threshold):
    
    # This time we set the threshold to an arbitrary number of 15
    line_chunk_label_list = []
    
    # sets initial value of the chunk to 1, then increases as new chunks are detected based
    # on the chunk threshold
    
    chunk = 1
    
    for i in range(len(content)):
        temp = content[i]
        bbox = temp[1]
        bbox2 = bbox[0][1]
        #print(temp[0][0])
        
        if i > 0:
            prev = content[i-1]
            prev_bbox = prev[1]
            prev_bbox2 = prev_bbox[-1][1]
            diff = bbox2 - prev_bbox2
            if diff > threshold or diff < 0:
                chunk += 1
            line_chunk_label_list.append('Chunk %s' % chunk)
        else:
            line_chunk_label_list.append('Chunk %s' % chunk)
    
    # Get the unique chunks found on the page
    unique_chunks = list(set(line_chunk_label_list))
    
    return unique_chunks, line_chunk_label_list

def EBE_get_chunk_min_start_index_v_1_0_0(chunk):
    """
    
    Functionality to get the bbox[0] value for the first value on every line,
    and then return the minimum
    """
    
    row_start_index = []
    for i in range(len(chunk)):
        temp = chunk[i]
        first_bbox_index = temp[1][0][0]
        row_start_index.append(first_bbox_index)
    
    min_start_index = min(row_start_index)
    
    return min_start_index

def EBE_get_chunk_content_dict_v_1_0_0(content, unique_chunks, line_chunk_label_list):
    # This function splits the page into chunks and stores the content for each
    # chunk
    
    chunk_list_full = []
    for name in unique_chunks:
        
        chunks_list = []
        ### Build function to split the original content list into a list of 'chunk_contents'
        for i in range(len(content)):
            chunk_num = line_chunk_label_list[i]
            if chunk_num == name:
                chunks_list.append(content[i])
        chunk_list_full.append(chunks_list)
    
    
    # Create a dictionary to reference each chunk name and get its content
    chunk_dict = dict(zip(unique_chunks, chunk_list_full))
    
    return chunk_dict

def EBE_get_page_average_start_index(unique_chunks, chunk_dict):
    index_list = []
    for chunks in unique_chunks:
        chunk = chunk_dict[chunks]
        min_start_index = EBE_get_chunk_min_start_index_v_1_0_0(chunk)
        index_list.append(min_start_index)
    return np.average(index_list)


def EBE_get_chunk_average_row_length_v_1_0_0(chunk):
    """
    
    Functionality to get the average row length across the chunk 
    """
    row_len_list = []
    for i in range(len(chunk)):
        temp = chunk[i]  
        raw_text = temp[0][0]
        text_string = ' '.join(temp[0][0])
        row_len_list.append(len(raw_text))
    
    # Get the average rows of content across the chunk
    chunk_average_rows = np.average(row_len_list)
    
    return chunk_average_rows

def EBE_get_text_type_percs_v_1_0_0(text):
    digit_count = 0
    char_count = 0
    other_count = 0
    for t in text:
        if t != ' ':
            if t.isdigit():
                digit_count += 1
            elif t.isalpha():
                char_count += 1
            else:
                other_count += 1
    
    try:
        non_character_perc = int(((digit_count+other_count)/(digit_count + char_count + other_count))*100)
        digit_perc = int((digit_count/(digit_count + char_count + other_count))*100)
    except:
        non_character_perc = 0
        digit_perc = 0
    return non_character_perc, digit_perc


def EBE_get_page_chunk_type_v_1_0_4(chunk_dict, avg_start_index):
    
    """
    The change we have done here is to detect the cases where a chunk appears on its own and is detected as text, but its actually
    part of a table since its start location is in the middle of the page. We are also using the avg_start_index as well
    """
    
    bullet_point_string_list = ['\uf0b7', '•'] # add other formats to this lists based on 
    chunk_type_list = []
    
    ### Build function to detect the chunk types
    for names in chunk_dict.keys():
        
        chunk = chunk_dict[names]
        chunk_len = len(chunk)
        
        #print(names)
        #print(chunk_len)
        if chunk_len == 1:
            pass
#            print(chunk)
    
        # now check if the type of the chunk by determining the length of the text in each line, and the percentage
        # of numerical values to let you know if its a table of text or a table of numbers.
        ## Build functionality to check how many unique bbox1 value each row has and create a flag to indicate if its more than 2...
        
        row_len_list = []
        is_bullet_point = []
        for i in range(len(chunk)):
            temp = chunk[i]  
            bbox = temp[1]
    #            print(len(bbox))
            if len(bbox) > 1:
                box1_list = []
                for box in bbox:
                    box1_list.append(box[1])
                unique_box1 = list(set(box1_list))
            else:
                unique_box1 = [bbox[0][1]]
            raw_text = temp[0][0]
        
            text_string = ' '.join(temp[0][0])
            for strs in bullet_point_string_list:
                if strs in text_string:
                    is_bullet_point.append(1)
                else:
                    is_bullet_point.append(0)
            row_len_list.append(len(raw_text))
        
        #        print()
        #        print()
        # Get the average rows of content across the chunk
        chunk_average_rows = EBE_get_chunk_average_row_length_v_1_0_0(chunk)
        #print(chunk_average_rows)
        #print(unique_box1)
        #print()
        
        """
        ** The current functionality only works for pdfs that are element-by-element
        We are putting in a condition here that states that if the average number of rows in the chunk
        is less than 1.5, then its a text chunk, if not its a table chunk.
        
        Extra things to be done in a future release:
            - ** your chunk sorting functionality may cause problems because of cases where the text is split across
                multiple rows i.e where text is side-by side in the pdf page, instead of across the whole line.
            - detect the sub_type of text chunk (page header, in-body text etc)
            - detect the title of each chunk
            - detect if the chunk is a page header
            - detect if chunk is a table
            - detect if chunk is a table of text of table of numbers
            - detect if there are footnotes in the table chunk and classify accordingly
        """
        
        ## Functionality to detect chunk type
        
        if chunk_average_rows > 1:
            if sum(is_bullet_point) > 0:
                chunk_type = 'Bullet Point'
            elif len(unique_box1) > 2:
                ## This is to deal with issues where you are having a table of text and some chunks may be labelled incorrectly. In
                ## this particular instance the chunk has a length of 1, and row size of 1, but in reality its actually more than that.
                if len(chunk) == 1:
                    bbox = chunk[0][1]
                    bbox1_list = []
                    for box in bbox:
                        bbox1_list.append(int(box[1]))
                    unique = list(set(bbox1_list))
                    
                    if len(unique) != len(bbox1_list): # this means that the row length is not 1. You will need to add functionality to split 
                                                       # the chunk into multiple rows, but let that come later
                        chunk_type = 'Table'
                    else:

                            chunk_type = 'Text'
                else:
                    if chunk_average_rows > 1:
                        chunk_type = 'Table'
                    else:
                        chunk_type = 'Text' # Caused a problem already and you have improved this edge case
            else:
                chunk_type = 'Table'
        else:
            ## This is to deal with issues where you are having a table of text and some chunks may be labelled incorrectly. In
            ## this particular instance the chunk has a length of 1, and row size of 1, but in reality its actually more than that.
            if len(chunk) == 1:
                #print('Digging deeper to see if its a table')
#                print('Current chunk type is %s' % chunk_type)
                bbox = chunk[0][1]
                bbox1_list = []
                for box in bbox:
                    bbox1_list.append(int(box[1]))
                unique = list(set(bbox1_list))
                
                if len(unique) != len(bbox1_list): # this means that the row length is not 1. You will need to add functionality to split 
                                                   # the chunk into multiple rows, but let that come later
                    chunk_type = 'Table'
                else:
                    #print('Looking even further')
                    #print(bbox)
                    #print(avg_start_index)
                    #print()
                    if bbox[0][0] > (avg_start_index + 10): # This deals with the case where you have a standalone text that is part of a table as it starts
                                                     # significantly further away from the avg_start index for the chunks. Example is the table in page 5
                                                     # of elysian under raymond brown
                        #print('This should be a table')
                        chunk_type = 'Table'
                    else:
                        chunk_type = 'Text'
            else:
                chunk_type = 'Text'
        
        ### We only build this case for when the chunk_len is equal to 1 - page 8 of elysian2 ** merge this properly into the function later
        try:
            # this is a bit lazy of you, when you have time later, figure out where things should fit in    
            chunk_text = []
            for i in range(len(chunk)):
                chunk_text.append(chunk[i][0][0][0])
            
            text_string = ' '.join(chunk_text)
            #print(text_string)
            non_character_perc, digit_perc = EBE_get_text_type_percs_v_1_0_0(text_string)
            #print(digit_perc)
            
            if digit_perc > 15:
                if len(chunk_text) > 2:
                    chunk_type = 'Table'
            
            #print(chunk[0][0][0])
            #print(chunk_type)
            
        except Exception as e:
            #print('not able to do the extra check')
            #print(chunk[0][0][0][0])
            #print(e)
            pass
        
        chunk_type_list.append(chunk_type)
        
        chunk_type_dict = dict(zip(chunk_dict.keys(), chunk_type_list))
    
    return chunk_type_dict



def EBE_get_page_chunks_v_1_0_2(content):
    """
    Changes have been made to the get_page_chunk_thresolds functionality
    """
    threshold = EBE_get_page_chunk_thresholds_v_1_0_1(content)
    # Split the data into unique chunks
    unique_chunks, line_chunk_label_list = EBE_get_unique_chunks_v_1_0_3(content, threshold)
    chunk_dict = EBE_get_chunk_content_dict_v_1_0_0(content, unique_chunks, line_chunk_label_list)
    avg_start_index = EBE_get_page_average_start_index(unique_chunks, chunk_dict)
    chunk_type_dict = EBE_get_page_chunk_type_v_1_0_4(chunk_dict, avg_start_index)
    
    return unique_chunks, chunk_dict, chunk_type_dict



def EBE_sort_unique_chunks_v_1_0_0(unique_chunks):
    num_list = []
    for i in range(len(unique_chunks)):
        temp = unique_chunks[i]
        num = [int(s) for s in temp.split() if s.isdigit()]
        num_list.append(num[0])
    
    sorted_chunk_index = [i[0] for i in sorted(enumerate(num_list), key=lambda x:x[1])]
    unique_chunks = [unique_chunks[i] for i in sorted_chunk_index]
    
    return unique_chunks

def EBE_separate_multiple_text_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict):
    """
    The functionality here separates text chunks when we see two section headers
    within a text chunk
    """
    chunk_list = []
    chunk_type_list = []
    
    for chunks in unique_chunks:
        chunk = chunk_dict[chunks]
        chunk_type = chunk_type_dict[chunks]
        if chunk_type == 'Text':
            #print('We have a text chunk and will process to see if it should be divided further')
            if len(chunk) == 1:
                curr_chunk = chunk[0]
                text = curr_chunk[0][0]
                #print(len(text))
                font = curr_chunk[0][1]
                bbox = curr_chunk[1]
                
                bbox_range_list = []
                for i in range(len(bbox)):
                    bbox_range_list.append(bbox[i][2] - bbox[i][0])
                #print(max(bbox_range_list))
                
                width_threshold = 0.5 * max(bbox_range_list) 
                
                count_list = []
                count = 0
                for i in range(len(text)):
                    width = bbox[i][2] - bbox[i][0]
                    #print(width)
                    # makes sure we don't falsely separate the last line on the chunk
                    if i < len(text)-1:
                        if width < width_threshold:
                            count += 1
                            count_list.append(count)
                            #print(text[i])
                        else:
                            count_list.append(count)
                            
                    else:
                        count_list.append(count)
                #print(count_list)
            
                ## Now create 'n' new chunks from the current chunk 
                unique_counts = list(set(count_list))
                if len(unique_counts) > 1:
                    #print('We have found multiple text chunks within this chunk and will be splitting them')
                    #print(chunks)
                    for cnt in unique_counts:
                        text_00 = [] # to store the text
                        text_01 = [] # to store the font names
                        text_02 = [] # to store the font sizes
                        bbox_list = []
                        #print(cnt)
                        indices = [i for i, x in enumerate(count_list) if x == cnt]
                        for ind in indices:
                            text_00.append(chunk[0][0][0][ind])
                            text_01.append(chunk[0][0][1][ind])
                            text_02.append(chunk[0][0][2][ind])
                            bbox_list.append(chunk[0][1][ind])
                        new_line = [[text_00, text_01, text_02], bbox_list]
                        chunk_list.append([new_line])
                        chunk_type_list.append('Text')
                else:
                    chunk_list.append(chunk)
                    chunk_type_list.append(chunk_type)
            else:
                chunk_list.append(chunk)
                chunk_type_list.append(chunk_type)
        else:
            chunk_list.append(chunk)
            chunk_type_list.append(chunk_type)
        #print()
    
    #print(len(chunk_list))
    
    ## Now create a new set of table chunks after doing this cleanup
    chunk_name_list = []
    for i in range(len(chunk_list)):
        temp = i+1
        chunk_name_list.append('Chunk %s' % temp)
    
    chunk_dict = dict(zip(chunk_name_list, chunk_list))
    chunk_type_dict = dict(zip(chunk_name_list, chunk_type_list))
    #print(chunk_type_dict)
    
    return chunk_name_list, chunk_dict, chunk_type_dict


def EBE_find_text_between_two_table_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict):
    """
    This function identifies a text chunk thats within two tables, increases the length
    by padding it with empty values and then converts to a table chunk
    """
    
    chunk_list = []
    chunk_type_list = []
    
    for i in range(len(unique_chunks)):
        
        chunk = chunk_dict[unique_chunks[i]]
        chunk_type = chunk_type_dict[unique_chunks[i]]
        
        if i > 0:
            
            if chunk_type == 'Text':
                #print(unique_chunks[i])
                #print('We have a text chunk and will process to see if it should be divided further')
                if len(chunk) == 1:
                    #print('We have a single line chunk and will be checking if its inbetween two tables')
                    try:
                        prev_chunk_type = chunk_type_dict[unique_chunks[i-1]]
                        next_chunk_type = chunk_type_dict[unique_chunks[i+1]]
                    except:
                        prev_chunk_type = 'NA'
                        next_chunk_type = 'NA'
                    if prev_chunk_type == 'Table' and next_chunk_type == 'Table':
                        #print('We have seen a text chunk sandwiched between two tables and will be doing some cleanups')
                        # Get the row columns of the previous chunk
                        prev_row_len = EBE_get_chunk_average_row_length_v_1_0_0(chunk_dict[unique_chunks[i-1]])
                        # Get the row columns of the next chunk
                        next_row_len = EBE_get_chunk_average_row_length_v_1_0_0(chunk_dict[unique_chunks[i+1]])
                        expected_row_len = max(prev_row_len, next_row_len)
                        curr_row_len = EBE_get_chunk_average_row_length_v_1_0_0(chunk_dict[unique_chunks[i]])
                        deficit = int(expected_row_len - curr_row_len)
                        
                        ## Now create a new chunk that creates blank variables to deal with the mismatch
                        text_00 = [] # to store the text
                        text_01 = [] # to store the font names
                        text_02 = [] # to store the font sizes
                        bbox_list = []
                        
                        # Add the current chunk values
                        text_00.append(chunk[0][0][0][0])
                        text_01.append(chunk[0][0][1][0])
                        text_02.append(chunk[0][0][2][0])
                        bbox_list.append(chunk[0][1][0])
        
                        for i in range(deficit):
                            text_00.append(' ')
                            text_01.append(' ')
                            text_02.append(' ')
                            bbox_list.append((0,0,0,0))
                        new_line = [[text_00, text_01, text_02], bbox_list]
                        chunk_list.append([new_line])
                        chunk_type_list.append('Table')
                    else:
                        chunk_list.append(chunk)
                        chunk_type_list.append(chunk_type)
                else:
                    chunk_list.append(chunk)
                    chunk_type_list.append(chunk_type)
            else:
                chunk_list.append(chunk)
                chunk_type_list.append(chunk_type)
        
        else:
            chunk_list.append(chunk)
            chunk_type_list.append(chunk_type)
            
    #print(len(chunk_list))
    #print(len(unique_chunks)) 
    
    chunk_dict = dict(zip(unique_chunks, chunk_list))
    chunk_type_dict = dict(zip(unique_chunks, chunk_type_list))
    
    return unique_chunks, chunk_dict, chunk_type_dict


def EBE_fill_missing_row_key_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict):
    """
    This is for situations where a table chunk is split into multiple table chunks, and 
    we have one where the first column aka the row names is blank. We fill it in with the
    row name from the previous column
    """
    
    avg_start_index = EBE_get_page_average_start_index(unique_chunks, chunk_dict)
    page_start_threshold = 2 * avg_start_index # a number to be revised later
    
    chunk_list = []
    chunk_type_list = []
    for i in range(len(unique_chunks)):
        chunk = chunk_dict[unique_chunks[i]]
        chunk_type = chunk_type_dict[unique_chunks[i]]
        min_start_index = EBE_get_chunk_min_start_index_v_1_0_0(chunk)
        if min_start_index > page_start_threshold:
#            print('We need to investigate this chunk further')
            row_len = EBE_get_chunk_average_row_length_v_1_0_0(chunk)
            # if row_len <= 2: add this in later if we start to run into trouble
            prev_chunk_type = chunk_type_dict[unique_chunks[i-1]]
            prev_chunk = chunk_dict[unique_chunks[i-1]]
            prev_chunk_len_list = []
            for ii in range(len(prev_chunk)):
                pren_chunk_len = len(prev_chunk[ii][0][0])
                prev_chunk_len_list.append(pren_chunk_len)
            if prev_chunk_type == 'Table':
                if max(prev_chunk_len_list) == 2: 
#                    #print()
#                    print('This is a table of length 2 and we may go ahead and do the name replacement')
                    # check to make sure its a table of text
                    try:
                        non_character_perc, digit_perc = EBE_get_text_type_percs_v_1_0_0(chunk[1][0][0][0])
#                        print(digit_perc)
                    except:
                        non_character_perc, digit_perc = EBE_get_text_type_percs_v_1_0_0(chunk[0][0][0][0])
#                        print(digit_perc)
                    if digit_perc < 50: # this means that its a table of text and not a table of numbers
                        if len(chunk_dict[unique_chunks[i-1]]) > 1: # Adds this condition so we don't merge names when the previous chunk is singular as well
                            if chunk_dict[unique_chunks[i]][0][0][0][0].strip()[-1] != ":":
                                #print('We will now get the row key from the previous chunk and append to this one')
                    
                                # Create a new chunk by adding the row name from the previous chunk
                                curr_chunk = chunk_dict[unique_chunks[i]]  
                                prev_chunk = chunk_dict[unique_chunks[i-1]]
                                
            
                                new_chunk = []
                                for iii in range(len(curr_chunk)):
                                    text_00 = [] # to store the text
                                    text_01 = [] # to store the font names
                                    text_02 = [] # to store the font sizes
                                    text_list = []
                                    font_list = []
                                    size_list = []
                                    bbox_list = []
                                    if iii == 0:
                                        prev_bbox = prev_chunk[0][1][0]
                                        curr_bbox = curr_chunk[0][1][0]
                                        merged_bbox = (prev_bbox[0],curr_bbox[1],prev_bbox[2],curr_bbox[3])
                                    # Add the row key from the previous chunk to the new chunk
    #                                    print('Adding the row label from the previous chunk')
                                        text_00.append(prev_chunk[0][0][0][0])
                                        text_01.append(prev_chunk[0][0][1][0])
                                        text_02.append(prev_chunk[0][0][2][0])
                                        bbox_list.append(merged_bbox)
            
                                        # Add the values from the current chunk to the new chunk
                                        temp_00 = curr_chunk[iii][0][0]
            #                            print(temp_00)
                                        for temp in temp_00:
                                            text_00.append(temp)
                                            
                                        temp_01 = curr_chunk[iii][0][1]
                                        for temp in temp_01:
                                            text_01.append(temp)
                                            
                                        temp_02 = curr_chunk[iii][0][2]
                                        for temp in temp_02:
                                            text_02.append(temp)
                                            
                                        temp_bbox = curr_chunk[iii][1]
                                        for box in temp_bbox:
                                            bbox_list.append(box)
                                        
                                        new_line = [[text_00, text_01, text_02], bbox_list]
                                        new_chunk.append(new_line)
                                        #print()
                                    else:
    #                                    print('adding the other rows')
                                        # Add the values from the current chunk to the new chunk
                                        temp_00 = curr_chunk[iii][0][0]
            #                            print(temp_00)
                                        for temp in temp_00:
                                            text_00.append(temp)
                                            
                                        temp_01 = curr_chunk[iii][0][1]
                                        for temp in temp_01:
                                            text_01.append(temp)
                                            
                                        temp_02 = curr_chunk[iii][0][2]
                                        for temp in temp_02:
                                            text_02.append(temp)
                                            
                                        temp_bbox = curr_chunk[iii][1]
                                        for box in temp_bbox:
                                            bbox_list.append(box)
                                        
                                        new_line = [[text_00, text_01, text_02], bbox_list]
                                        new_chunk.append(new_line)
                                # add the newly created chunk to our list of chunks        
                                chunk_list.append(new_chunk)
                                chunk_type_list.append('Table')
                            else:
                                chunk_list.append(chunk)
                                chunk_type_list.append(chunk_type)   
                        else:
#                            print('Its a table of numbers so we do nothing')
                            chunk_list.append(chunk)
                            chunk_type_list.append(chunk_type)                            
                    else:
                        chunk_list.append(chunk)
                        chunk_type_list.append(chunk_type)
                else:
                    chunk_list.append(chunk)
                    chunk_type_list.append(chunk_type)
            else:
                chunk_list.append(chunk)
                chunk_type_list.append(chunk_type)
        else:
            chunk_list.append(chunk)
            chunk_type_list.append(chunk_type)
            
    chunk_dict = dict(zip(unique_chunks, chunk_list))
    chunk_type_dict = dict(zip(unique_chunks, chunk_type_list))
        
    return unique_chunks, chunk_dict, chunk_type_dict


def EBE_merge_duplicated_line_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict):
    """
    This deals with situations where you have a chunk line that is split into multiple
    sub-chunks, the function identifies them and merges them into 1 line
    
    A hack has been created where we go through the extra step of looking for the digit perc of the chunk,
    this should be incorporated into the functionality to detect the chunk type instead
    """
    chunk_list = []
    chunk_type_list = []  
    # Now we build functionality to find    
    for chunks in unique_chunks:
        chunk = chunk_dict[chunks]
        chunk_type = chunk_type_dict[chunks]
        chunk_text = []
        
        for i in range(len(chunk)):
            chunk_text.append(chunk[i][0][0][0])
        
        text_string = ' '.join(chunk_text)
        non_character_perc, digit_perc = EBE_get_text_type_percs_v_1_0_0(text_string)
        
        if ((chunk_type == 'Table') or digit_perc > 15):
            #print(chunks)
            #print(chunk_type)
            if len(chunk) > 1:
                unique_box1 = []
                #print('We have a table chunk and will process to see if there are multiple lines that need to be merged into 1 line') 
                for i in range(len(chunk)):
                    temp = chunk[i]
                    text = temp[0]
                    bbox = temp[1]
                    box1_list = []
                    for box in bbox:
                        box1_list.append(int(box[1]))
                    unique_box1.append(list(set(box1_list))[0])
                #print(unique_box1)
                #print(len(list(set(unique_box1))))
                #print(len(unique_box1))
                if len(list(set(unique_box1))) < len(unique_box1):
                    #print('We have a case where we need to merge em together')
                    count_dict = Counter(unique_box1)
#                    print(count_dict)
                    # identify the box1 value to be used for identifying the subchunks to be merged
    
                    chunk_line_list = []
                    for keys in count_dict.keys():
                        #print(keys)
#                        print()
                        text_00 = [] # to store the text
                        text_01 = [] # to store the font names
                        text_02 = [] # to store the font sizes
                        text_list = []
                        font_list = []
                        size_list = []
                        bbox_list = []
                        temp_bbox = []
                        count = count_dict[keys]
                        #print(count)
                        for i in range(len(chunk)):
                            temp = chunk[i]
                            text = temp[0]
                            bbox = temp[1]
                            for ii in range(len(bbox)):
                                diff = abs(bbox[ii][1] - keys)
                                if diff < 5:
                                    pass
                                    #print(diff)
                                if int(bbox[ii][1]) == keys:
                                    #print(text[0][ii])
                                    text_list.append(text[0][ii])
                                    font_list.append(text[1][ii])
                                    try:
                                        size_list.append(text[2][ii][0])
                                    except:
                                        size_list.append(text[2][ii])
                                    temp_bbox.append(bbox[ii])
                                else:
#                                    print('yass_')
                                    text_00.append(text[0][ii])
                                    text_01.append(text[1][ii])
                                    try:
                                        text_02.append(text[2][ii][0])
                                    except:
                                        text_02.append(text[2][ii])
                                    bbox_list.append(bbox[ii])
                            
                        new_line = [[text_list, font_list, size_list], temp_bbox]
                        chunk_line_list.append(new_line)
                    chunk_list.append(chunk_line_list)
                else:
                    chunk_list.append(chunk)
            else:
                chunk_list.append(chunk)
        else:
            chunk_list.append(chunk)
                        
    chunk_dict = dict(zip(unique_chunks, chunk_list))
    
    return unique_chunks, chunk_dict, chunk_type_dict

def EBE_as_range_v_1_0_0(iterable): # not sure how to do this part elegantly
    """
    This function gets the first and last indices of any list of numbers that you pass into it
    """
    l = list(iterable)
    if len(l) > 1:
        return [l[0], l[-1]]
    else:
        return '{0}'.format(l[0])
    
def EBE_remove_incompatible_tables(consecutive_table_chunk, chunk_dict, unique_chunks):
    consecutive_table_chunk = [interval for interval in consecutive_table_chunk if isinstance(interval, list)]
    ranges = [list(range(interval[0], interval[1]+1)) for interval in consecutive_table_chunk]
    differences = []
    intervals = []
    for array in ranges:
        for index in array[1:]:
            prev_bottom = chunk_dict[unique_chunks[index-1]][-1][1][0][3]
            current_top = chunk_dict[unique_chunks[index]][0][1][0][1]
            gap = current_top - prev_bottom
            if gap > 0:
                differences.append(gap)
    avg_gap = np.mean(differences) + 2
    for array in ranges:
        current_interval = []
        for index in array[1:]:
            prev_bottom = chunk_dict[unique_chunks[index-1]][-1][1][0][3]
            current_top = chunk_dict[unique_chunks[index]][0][1][0][1]
            prev_content = chunk_dict[unique_chunks[index-1]][0][0][0]
            current_content = chunk_dict[unique_chunks[index]][0][0][0]
            gap = current_top - prev_bottom
            if 0 < gap and gap <= avg_gap:# and len(prev_content) == len(current_content):
                current_interval.append(index - 1)
                current_interval.append(index)
            else:
                if len(current_interval) > 1:
                    intervals.append([current_interval[0], current_interval[-1]])
                current_interval = []
        if len(current_interval) > 1:
            intervals.append([current_interval[0], current_interval[-1]])
    return intervals


def EBE_create_post_table_merge_chunks_v_1_0_0(interval, unique_chunks, chunk_dict, chunk_type_dict):
    # A function that takes an interval and concatenates the chunks within that interval
    # and then create a new set of chunk and chunk_type dicts
    
    new_unique_chunks = []
    new_chunk_list = []
    new_chunk_type = []
    
    table_chunks = []
    for names in unique_chunks:
        num = [int(s) for s in names.split() if s.isdigit()][0]
        if num-1 < interval[0] or num-1 > interval[1]:
            new_unique_chunks.append(names)
            new_chunk_list.append(chunk_dict[names])
            new_chunk_type.append(chunk_type_dict[names])
        else:
            table_chunks.append(names)
    
    # Now group the chunks tagged for combination into 1:
    chunk_rows = []
    for names in table_chunks:
        chunk = chunk_dict[names]
        for i in range(len(chunk)):
            chunk_rows.append(chunk[i])
    new_unique_chunks.append(table_chunks[0])
    new_chunk_list.append(chunk_rows)
    new_chunk_type.append('Table')
     
    new_chunk_dict = dict(zip(new_unique_chunks, new_chunk_list))
    new_chunk_type_dict = dict(zip(new_unique_chunks, new_chunk_type))
    
    return new_unique_chunks, new_chunk_dict, new_chunk_type_dict


def EBE_merge_consecutive_table_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict):
    
    """
    This funciton deals with situations where a table chunk has been separated into multiple chunks, primarily when the spacing in the page is 
    not standardised. We look for table chunks and then find how many consecutive table chunks follow
    """
    from itertools import groupby, count
    
    ## Build functionality to look for consecutive table chunk and store the start and end indices
    table_chunk_inds = []
    
    for i in range(len(unique_chunks)):
        chunk = chunk_dict[unique_chunks[i]]
        chunk_type = chunk_type_dict[unique_chunks[i]]
        if chunk_type == 'Table':
            table_chunk_inds.append(i)
    # Find the number of instances of consecutive table chunks and 
    consecutive_table_chunks = [EBE_as_range_v_1_0_0(g) for _, g in groupby(table_chunk_inds, key=lambda n, c=count(): n-next(c))]    
    consecutive_table_chunks = EBE_remove_incompatible_tables(consecutive_table_chunks, chunk_dict, unique_chunks)
    # Do this 3 times, i dont really see there being more than 3 tables on a page, and do it via a try/except block
    for interval in consecutive_table_chunks:
        unique_chunks, chunk_dict, chunk_type_dict = EBE_create_post_table_merge_chunks_v_1_0_0(interval, unique_chunks, chunk_dict, chunk_type_dict)
    return unique_chunks, chunk_dict, chunk_type_dict

def EBE_sort_table_by_box1_v_1_0_0(chunk):
    bbox2_list = []
    for i in range(len(chunk)):
        bbox2 = chunk[i][1][0][1]
        bbox2_list.append(bbox2)
    
    sorted_index = [i[0] for i in sorted(enumerate(bbox2_list), key=lambda x:x[1])]
    chunk = [chunk[i] for i in sorted_index]
    
    return chunk

def EBE_sort_table_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict):
    chunk_list = []
    new_unique_chunk = []
    for i in range(len(unique_chunks)):
        try:
            chunk = chunk_dict[unique_chunks[i]]
            chunk_type = chunk_type_dict[unique_chunks[i]]
            if chunk_type == 'Table':
                chunk = EBE_sort_table_by_box1_v_1_0_0(chunk)
            chunk_list.append(chunk)
            new_unique_chunk.append(unique_chunks[i])
        except:
            pass
    chunk_dict = dict(zip(new_unique_chunk, chunk_list))
    return chunk_dict

def EBE_get_chunk_average_row_length_v_1_0_1(chunk):
    """
    We make an improvement to this by looking for the unique box[0] values across the chunk
    """
    row_len_list = []
    for i in range(len(chunk)):
        temp = chunk[i]  
        bbox = temp[1]
        box1_list = []
        for box in bbox:
            box1_list.append(box[0])
        unique = list(set(box1_list))
        row_len_list.append(len(unique))
    
    # Get the average rows of content across the chunk
    chunk_average_rows = np.average(row_len_list)
    
    return chunk_average_rows

def EBE_cleanup_multiple_box0_table_chunks_v_1_0_0(chunk):
    """
    Check for instances where there are multiple instances of a bbox[0] value in a line of a table chunk and concatenate them together, this is another
    table cleanup that you do
    """
    
    from collections import Counter
    
    new_chunk = []
    
    # Get all the bbox[0] values across the chunk
    for i in range(len(chunk)):
        temp = chunk[i]
        text = temp[0]
        bbox = temp[1]
        box0_list = []
        for box in bbox:
            box0_list.append(box[0])
        # Print the list as well as the unique_list
        unique = list(set(box0_list))
        if len(unique) < len(box0_list):
#            print('We have some merging to do')
            count_dict = Counter(box0_list)
            for keys in count_dict.keys():
                count = count_dict[keys]
                if count > 1:
                    text_00 = [] # to store the text
                    text_01 = [] # to store the font names
                    text_02 = [] # to store the font sizes
                    text_list = []
                    font_list = []
                    size_list = []
                    bbox_list = []
                    temp_bbox = []
                    for ii in range(len(bbox)):
                        if bbox[ii][0] == keys:
                            text_list.append(text[0][ii])
                            font_list.append(text[1][ii])
                            try:
                                size_list.append(text[2][ii][0])
                            except:
                                size_list.append(text[2][ii])
                            temp_bbox.append(bbox[ii])
                        else:
                            text_00.append(text[0][ii])
                            text_01.append(text[1][ii])
                            try:
                                text_02.append(text[2][ii][0])
                            except:
                                text_02.append(text[2][ii])
                            bbox_list.append(bbox[ii])
                    text_string = ' \n'.join(text_list)
                    text_00.append(text_string)
                    unique_fonts = list(set(font_list))
                    text_01.append(unique_fonts[0])
                    unique_size = list(set(size_list))
                    text_02.append(unique_size[0])
                    # now deal with the concatenation of multiple bboxes for the text into 1
                    b1 = [box[0] for box in temp_bbox]
                    b2 = [box[1] for box in temp_bbox]
                    b3 = [box[2] for box in temp_bbox]
                    b4 = [box[3] for box in temp_bbox]
                    final_box = (min(b1), min(b2), max(b3), max(b4))
                    bbox_list.append(final_box)
            new_line = [[text_00, text_01, text_02], bbox_list]
            new_chunk.append(new_line)
        else:
            new_chunk.append(temp)
        
    return new_chunk


def EBE_check_for_multiple_box0_table_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict):
    new_chunks = []
    for i in range(len(unique_chunks)):
        name = unique_chunks[i]
        chunk = chunk_dict[name]
        chunk_type = chunk_type_dict[name]
        row_len = EBE_get_chunk_average_row_length_v_1_0_1(chunk)
        if row_len < 2.5:
            if chunk_type == 'Table':
                chunk = EBE_cleanup_multiple_box0_table_chunks_v_1_0_0(chunk)
                new_chunks.append(chunk)
            else:
                new_chunks.append(chunk)
        else:
            new_chunks.append(chunk)
    new_chunk_dict = dict(zip(unique_chunks, new_chunks))
    
    return unique_chunks, new_chunk_dict, chunk_type_dict


def EBE_combine_table_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict):
    """
    This funciton deals with situations where a table chunk has been separated from the table description text above it.
    We look for table chunks and then look for the text above it, if said text has any bold elements, then we assume that this
    is the table name and any text under it (before the table starts) is the table description.
    """
    if len(unique_chunks) > 1:
        combine_chunk_list_inds = []
        for i in range(len(unique_chunks)):
            chunks = unique_chunks[i]
            chunk = chunk_dict[chunks]
            if chunk_type_dict[chunks] == 'Table':
                prev_chunk = chunk_dict[unique_chunks[i-1]]
                prev_chunk_type = chunk_type_dict[unique_chunks[i-1]]
                bold_list = []
                if prev_chunk_type == 'Text':
                    for ii in range(len(prev_chunk)):
                        font = prev_chunk[ii][0][1][0]
                        if 'Bold' in font:
                            bold_list.append(1)
                        else:
                            bold_list.append(0)
                    if sum(bold_list) > 0:
                        combine_chunk_list_inds.append([i-1, i])
        if len(combine_chunk_list_inds) > 0:
            new_unique_chunks = []
            new_chunk_list = []
            new_chunk_type = []
            #print('We will be doing some combining')
#            print(combine_chunk_list_inds)
            comb_inds = combine_chunk_list_inds[0]
#            print(comb_inds)
            comb_names = [unique_chunks[i] for i in comb_inds]
#            print(comb_names)
            for i in range(len(unique_chunks)):
                chunk_name = unique_chunks[i]
                if chunk_name not in comb_names:
                    new_unique_chunks.append(chunk_name)
                    new_chunk_list.append(chunk_dict[chunk_name])
                    new_chunk_type.append(chunk_type_dict[chunk_name])
            
            # Now group the chunks tagged for combination into 1:
            chunk_rows = []
            for names in comb_names:
                chunk = chunk_dict[names]
                for i in range(len(chunk)):
                    chunk_rows.append(chunk[i])
            new_unique_chunks.append(comb_names[0])
            new_chunk_list.append(chunk_rows)
            new_chunk_type.append('Table')
            
            new_chunk_dict = dict(zip(new_unique_chunks, new_chunk_list))
            new_chunk_type_dict = dict(zip(new_unique_chunks, new_chunk_type))
            
            return new_unique_chunks, new_chunk_dict, new_chunk_type_dict
        
        else:
            return unique_chunks, chunk_dict, chunk_type_dict
    else:
        return unique_chunks, chunk_dict, chunk_type_dict


def EBE_clean_close_box1_table_chunk_line_v_1_0_0(chunk):
    ##**** This is a very long-winded function that should definitely be improved upon later
    ## Build functionality to check for cases where the box1 values for a line in a chunk is different by a factor of less than 3, you would then need to merge
    ## them together into a single line
    
    # Get the maximum row len of the chunk
    row_len_list = []
    for i in range(len(chunk)):
        temp = chunk[i]
        row_len_list.append(len(temp[0][0]))
    
    max_row_len = max(row_len_list)
            
    
    diff_list = []
    # Get the average diff across the chunk
    for i in range(len(chunk)):
        if i > 0:
            temp = chunk[i]
#            print(temp[0][0])
            curr_bbox1 = temp[1][0][1]
            prev_bbox1 = chunk[i-1][1][0][1]
            diff = curr_bbox1 - prev_bbox1
#            print(diff)
#            print()
            diff_list.append(diff)
    
    avg_diff_list = np.average(diff_list)
    thresold = 0.5 * avg_diff_list ## An arbitrary value has been set here, you should review this later
#    print(thresold)
    
    merge_index = []
    
    for c in range(len(chunk)):
        if c > 0:
#            print(c)
            temp = chunk[c]
#            print(temp)
#            print(len(temp[0][0]))
#            print(temp[0][0])
            curr_bbox1 = temp[1][0][1]
            prev_bbox1 = chunk[c-1][1][0][1]
            diff = curr_bbox1 - prev_bbox1
#            print(diff)
#            print(thresold)
            if diff < thresold:
                non_key_text = []   
                for c2 in range(len(temp[0][0])):
                    if temp[1][c2][0] > 100: # the aim of this is to only get stuff from the value columns, find a better way of detecting the threshold, maybe get the page min_start_index and add 50 to it
                            non_key_text.append(temp[0][0][c2])
                text_string = ' '.join(non_key_text)
                non_character_perc, digit_perc = EBE_get_text_type_percs_v_1_0_0(text_string)
                non_digit_perc = 100 - digit_perc
#                print(text_string)
#                print(non_digit_perc)
#                print()
#                print()
                prev_len = len(chunk[i-1][0][0])
                curr_len = len(chunk[i][0][0])
#                print(diff)
                
                if non_digit_perc < 50:## we add functionality to not do this merging when the line seems to contain mostly text, which would make it most likely a table column name
                    if prev_len + curr_len <= max_row_len:
#                        print('Should be merged')
#                        print(chunk[i-1][0][0])
#                        print(chunk[i][0][0])
#                        print()
                        merge_index.append([i-1,i])

                else:
                    pass
                    #print('We have seen lines that should be merged, but since it seems to be a table header and not table values we will ignore and move on')

    if len(merge_index) > 0:
        #print('We have seen irregularities in the lining of the table rows and will fix it now')
        merge_list = []
        
        for combs in merge_index:
            merge_list += combs
        
        count_dict = Counter(merge_list)
        
        triple_list = []
        for keys in count_dict.keys():
            if count_dict[keys] > 1:
                triple_list.append(keys)
        
        ## work on the merge indices to accomodate for cases where
        merge_index2 = []
        for inds in triple_list:
            to_be_merged = []
            output = []
            for i in range(len(merge_index)):
                comb = merge_index[i]
                if inds in comb:
                    to_be_merged.append(comb)
            for combs in to_be_merged:
                for ind in combs:
                    if ind not in output:
                        output.append(ind)
            merge_index2.append(output)
        
        reject_ind_list = []
        for combs in merge_index2:
            reject_ind_list += combs
        
        count = 0
        merge_index_final = []
        for combs in merge_index:
            if combs[0] not in reject_ind_list:
                if combs[1] not in reject_ind_list:
                    merge_index_final.append(combs)
        
        for combs in merge_index2:
            merge_index_final.append(combs)
            
        
        ## Now sort the list by the first item
        first_ind_list = []
        for combs in merge_index_final:
            first_ind_list.append(combs[0])
        
        sorted_index = [i[0] for i in sorted(enumerate(first_ind_list), key=lambda x:x[1])]
        merge_combinations = [merge_index_final[i] for i in sorted_index]
        #print(merge_combinations)
        
        comb_indices_list = []
        
        for combs in merge_index:
            comb_indices_list += combs
            
        comb_indices_list_final = list(set(comb_indices_list))
        
                    
        ### Now that you know which ones are to be merged, time to merge them
        chunk_line_list = []
        
        for comb in merge_combinations:
        
            text_00 = [] # to store the text
            text_01 = [] # to store the font names
            text_02 = [] # to store the font sizes
            bbox_list = []
            
            for ind in comb:
                curr_chunk = chunk[ind]
                text = curr_chunk[0][0]
                for ii in range(len(text)):
                    text_00.append(curr_chunk[0][0][ii])
                    text_01.append(curr_chunk[0][1][ii])
                    text_02.append(curr_chunk[0][2][ii])
                    bbox_list.append(curr_chunk[1][ii])
            new_line = [[text_00, text_01, text_02], bbox_list]
            
            # sort the chunks by appearance
            first_bbox_list = []
            line_index = []
            line_text = new_line[0][0]
            
            for i in range(len(line_text)):
                first_bbox_list.append(new_line[1][i][0])
                line_index.append(i)
                
            # make sure the new line is properly sorted
            sorted_index = [i[0] for i in sorted(enumerate(first_bbox_list), key=lambda x:x[1])]
            line_index = [line_index[i] for i in sorted_index]
            
            # Now add them again to make sure its in the right order
            
            text_00 = [] # to store the text
            text_01 = [] # to store the font names
            text_02 = [] # to store the font sizes
            bbox_list = []
            
            for ii in line_index:
                text_00.append(new_line[0][0][ii])
                text_01.append(new_line[0][1][ii])
                text_02.append(new_line[0][2][ii])
                bbox_list.append(new_line[1][ii])
            new_line = [[text_00, text_01, text_02], bbox_list]
        
            chunk_line_list.append(new_line)
        
        
        for i in range(len(chunk)):
            if i not in comb_indices_list_final:
                chunk_line_list.append(chunk[i])
        
        line_list = []
        line_index = []
        for i in range(len(chunk_line_list)):
            line_list.append(chunk_line_list[i][1][0][1])
            line_index.append(i)
            
        # make sure the new line is properly sorted
        sorted_index = [i[0] for i in sorted(enumerate(line_list), key=lambda x:x[1])]
        line_index = [line_index[i] for i in sorted_index]
        #print(line_index)
        
        chunk_line_list = [chunk_line_list[i] for i in line_index]
        
        return chunk_line_list
    else:
        #print('Nothing to change on this chunk')
        return chunk


def EBE_clean_table_row_irregularities_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict):
    """
    This function deals with situations where there are some irregularities in spacing for the
    table chunks, an example is page 7 of the elysian document
    """
    chunk_list = []
    for i in range(len(unique_chunks)):
        chunk_type = chunk_type_dict[unique_chunks[i]]
        #print(chunk_type)
        chunk = chunk_dict[unique_chunks[i]]
        if chunk_type == 'Table':
            chunk = EBE_clean_close_box1_table_chunk_line_v_1_0_0(chunk)
        chunk_list.append(chunk)
    
    chunk_dict = dict(zip(unique_chunks, chunk_list))
    
    return unique_chunks, chunk_dict, chunk_type_dict


def EBE_merge_consecutive_chunks_v_1_0_0(interval, unique_chunks, chunk_dict, chunk_type_dict):
    # A function that takes an interval and concatenates the chunks within that interval
    # and then create a new set of chunk and chunk_type dicts. THis is used to deal with situations like elysian where the table header
    # is separated from the rest of the text
    
    new_unique_chunks = []
    new_chunk_list = []
    new_chunk_type = []
    
    interval_chunks = []
    for names in unique_chunks:
        num = [int(s) for s in names.split() if s.isdigit()][0]
        if num-1 < interval[0] or num-1 > interval[1]:
            new_unique_chunks.append(names)
            new_chunk_list.append(chunk_dict[names])
            new_chunk_type.append(chunk_type_dict[names])
        else:
            interval_chunks.append(names)
    
#    print(len(interval_chunks))
    
    # Now group the chunks tagged for combination into 1:
    chunk_rows = []
    for names in interval_chunks:
        chunk = chunk_dict[names]
        for i in range(len(chunk)):
            chunk_rows.append(chunk[i])
    new_unique_chunks.append(interval_chunks[0])
    new_chunk_list.append(chunk_rows)
    new_chunk_type.append(chunk_type_dict[interval_chunks[1]])
     
    new_chunk_dict = dict(zip(new_unique_chunks, new_chunk_list))
    new_chunk_type_dict = dict(zip(new_unique_chunks, new_chunk_type))
    
    return new_unique_chunks, new_chunk_dict, new_chunk_type_dict


def EBE_merge_section_header_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict):
    """
    This function deals with cases where the page section header is separated from the body of text and merges them back in. We look
    for chunks that occur over only 1 line and then fit other categories and merge those chunks with the next chunk
    """

    merge_list = []
    for i in range(len(unique_chunks)):
        curr_chunk_name = unique_chunks[i]
    #    print(curr_chunk_name)
    #    print()
        chunk = chunk_dict[curr_chunk_name]
        if len(chunk) == 1:
            font = chunk[0][0][1][0]
            text = chunk[0][0][0][0]
            
            if len(text) < 40:
#                print(len(text))
        #        print(font)
        #        if 'bold' in font.lower(): # taken this out to deal with section headers that may not necessarily be in bold, may have to revise this later
                num = [int(s) for s in curr_chunk_name.split() if s.isdigit()][0]
#                print('Chunk %s to be merged with chunk %s' % (num, num+1))
                merge_list.append([num-1, num])
    
#    print(merge_list)


    for i in range(len(merge_list)):
        
        try:
            interval = merge_list[i]
            unique_chunks, chunk_dict, chunk_type_dict = EBE_merge_consecutive_chunks_v_1_0_0(interval, unique_chunks, chunk_dict, chunk_type_dict)
            unique_chunks = EBE_sort_unique_chunks_v_1_0_0(unique_chunks) # This sorts it by chunk number
        except Exception as e:
#            print('Error raised')
#            print(e)
            pass
    
    return unique_chunks, chunk_dict, chunk_type_dict

def EBE_get_table_chunk_type_v_1_0_0(chunk):
    non_key_text = []   
    for i in range(len(chunk)):
        text = chunk[i][0][0]
        bbox = chunk[i][1]
        for ii in range(len(bbox)):
            if bbox[ii][0] > 200: # the aim of this is to only get stuff from the value columns
                non_key_text.append(text[ii])

    len_list = []
    for t in range(len(chunk)):
        len_list.append(len(chunk[t][0][0]))
    max_len = max(len_list)

    non_key_text = ' '.join(non_key_text)       
    non_character_perc, digit_perc = EBE_get_text_type_percs_v_1_0_0(non_key_text)
    
    if digit_perc > 20:
        table_type = 'Numbers'
    else:
        if max_len > 5:
            table_type = 'Numbers'
        else:
            table_type = 'Text'
    
    return table_type


def EBE_get_table_type_dict_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict):
    ## Now build functionality to loop through each chunk and then create a table_type_dict
    ### First build functionality to detect whether its a table of text, or a table of numbers
    ### based on page 2 of the elysian document
    table_chunk_type_list = []
     
    for i in range(len(unique_chunks)):
        curr_chunk_name = unique_chunks[i]
        try:
            chunk = chunk_dict[curr_chunk_name]
            chunk_type = chunk_type_dict[curr_chunk_name]
            if chunk_type == 'Table':
                table_type = EBE_get_table_chunk_type_v_1_0_0(chunk)
            else:
                table_type = 'NA'
                
            table_chunk_type_list.append(table_type)
        except:
            print('For some reason %s is not in the chunk dict anymore' % curr_chunk_name)
        
        table_type_dict = dict(zip(unique_chunks, table_chunk_type_list))
    
    return table_type_dict
