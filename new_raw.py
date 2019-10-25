#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 21:06:22 2019

@author: root
"""
import fitz
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import os
import random
from collections import Counter
import numpy as np
import pandas as pd
import time

def EBE_extractDict_v_1_0_0(file):
    """
    This function converts the pdf into a list of dicts and this is the one that we use to parse through and extract the document
    """
    doc = fitz.open(file)
    dict_list = []
    for page in doc:
        t = page.getText('dict')
        dict_list.append(t)
    return dict_list
    
    
def EBE_check_for_pdf_type_v_1_0_0(dict_list):
    """
    This function finds out if the pdf type is line-by-line or element-by-element based on the structure
    of the pdf. If you are having multiple elements across the same line (same bbox[1] values) then you know
    it is element-by-element.... else it is line-by-line. We are yet to see another type of document.
    """
    
    page_type_list = []
    for i in range(len(dict_list)):
        try:
            doc_dict = dict_list[1]
        
            blocks = doc_dict.get('blocks', [])
            
            bbox2_list = []
            
            for block in blocks:
                lines = block.get('lines', [])
            
                for line in lines:
                    bbox = line.get('bbox')
                    spans = line.get('spans', [])
                    bbox2_list.append(bbox[1])
                    
            unique = set(bbox2_list)
            
            # we check if there are bbox2 values being seen across multiple lines, this means that the
            # document isnt split line-by-line but rather element-by-element
            if len(bbox2_list) > len(unique):
                output = 'element_by_element'
            else:
                output = 'line_by_line'
            #print(len(bbox2_list))
            #print(len(unique))
            page_type_list.append(output)
        except:
            continue
    
    #print(list(set(page_type_list)))
        return output
#c = Raw.EBE_extractDict_v_1_0_0(self)
def EBE_get_page_content_by_line_v_1_0_2(doc_dict):
    """
    We have updated the previous version to include the 
    """

    blocks = doc_dict.get('blocks', [])
    
    content = []
    bbox = []
    
    for block in blocks: # I have added an improvement here where I am only saving lines that have some info/text in it
        lines = block.get('lines', [])
        #print(len(lines))
        
        row_vals = []
        row_vals_font = []
        row_vals_size = []
        temp_list = []
        bbox_list_temp = []
        for line in lines:
            #print(line.keys())
            bbox = line.get('bbox')
            spans = line.get('spans', [])
    
                
            text_list = []
            font_list = []
            size_list = []
            for span in spans:
                #print(spans)
                text = span.get('text')
                font = span.get('font')
                size = span.get('size')
                if len(text) > 0:
                    if font not in font_list:
                        font_list.append(font)
                        size_list.append(size)
                text_list.append(text.strip("\n"))
                
                text2 = ' '.join(text_list)
            
            if len(text2) > 0:
                unique_fonts = font
                unique_size = list(set(size_list))
                bbox_list_temp.append(bbox)
                row_vals.append(text2)
                
                ## We are only getting the first font here, later consider an approach that gets all the fonts in the line, but this is fine for now
                row_vals_font.append(unique_fonts)
                row_vals_size.append(unique_size)
    
#                    unique_font = list(set(row_vals_font))
#                    unique_size = list(set(row_vals_size))
        
        ## Update v1.0.2: Updated the previous version to include instances where you have 3 text instances in the list
        if len(row_vals) > 0:
            #print(bbox_list_temp)
            if len(bbox_list_temp) == 2: # you will need to work on this for cases where there are more than 2 and you need to cycle through them... its doable sha
#                print('we have a 2 peat')
#                print(row_vals)
                bbox1 = bbox_list_temp[0][1]
                bbox2 = bbox_list_temp[1][1]
                diff = bbox2 - bbox1
#                print(diff)
                if diff > 5: 
                    # this is a hyperparameter that you may want to tune better later... but for now its fine, was initially 10, and now has been changed to 5
                    # later what we will want to do is write a function to get the average diff of items within a line and get what the average is
                    content.append([[[row_vals[0]], [row_vals_font[0]], [row_vals_size[0]]], [bbox_list_temp[0]]])
                    content.append([[[row_vals[1]], [row_vals_font[1]], [row_vals_size[1]]], [bbox_list_temp[1]]])
#                    print('value inputted')
#                    print()
                else:
#                    print('diff was not large enough')
                    content.append([[row_vals, row_vals_font, row_vals_size], bbox_list_temp])
#                    print()
            elif len(bbox_list_temp) == 3: 
#                print('We have a 3 peat')
#                print(row_vals)
                bbox1 = bbox_list_temp[0][1]
                bbox2 = bbox_list_temp[1][1]
                bbox3 = bbox_list_temp[2][1]
                diff1 = bbox2 - bbox1
                diff2 = bbox3 - bbox2
                if (diff1 > 5 and diff2 > 5): 
                    # this is a hyperparameter that you may want to tune better later... but for now its fine, was initially 10, and now has been changed to 5
                    # later what we will want to do is write a function to get the average diff of items within a line and get what the average is
                    content.append([[[row_vals[0]], [row_vals_font[0]], [row_vals_size[0]]], [bbox_list_temp[0]]])
                    content.append([[[row_vals[1]], [row_vals_font[1]], [row_vals_size[1]]], [bbox_list_temp[1]]])
                    content.append([[[row_vals[2]], [row_vals_font[2]], [row_vals_size[2]]], [bbox_list_temp[2]]])
#                    print('diff 1 and 2 both greater than 5')
                elif (diff1 > 5 and diff2 < 5): 
                    # this is a hyperparameter that you may want to tune better later... but for now its fine, was initially 10, and now has been changed to 5
                    # later what we will want to do is write a function to get the average diff of items within a line and get what the average is
                    content.append([[[row_vals[0]], [row_vals_font[0]], [row_vals_size[0]]], [bbox_list_temp[0]]])
#                    content.append([[[row_vals[1:]], [row_vals_font[1:]], [row_vals_size[1:]]], [bbox_list_temp[1:]]])
                    content.append([[row_vals[1:], row_vals_font[1:], row_vals_size[1:]], bbox_list_temp[1:]])
#                    print('diff 1 is greater than 5 and diff 2 is less than 5')
                elif (diff1 < 5 and diff2 > 5): 
                    # this is a hyperparameter that you may want to tune better later... but for now its fine, was initially 10, and now has been changed to 5
                    # later what we will want to do is write a function to get the average diff of items within a line and get what the average is
#                    content.append([[[row_vals[0:2]], [row_vals_font[0:2]], [row_vals_size[0:2]]], [bbox_list_temp[0:2]]])
                    content.append([[row_vals[0:2], row_vals_font[0:2], row_vals_size[0:2]], bbox_list_temp[0:2]])
                    content.append([[[row_vals[2]], [row_vals_font[2]], [row_vals_size[2]]], [bbox_list_temp[2]]])
#                    print('diff 1 is less than 5 and diff 2 is greater than 5')
                    
                else:
                    content.append([[row_vals, row_vals_font, row_vals_size], bbox_list_temp])
#                    print('diff 1 and 2 both less than 5')
            else:
                content.append([[row_vals, row_vals_font, row_vals_size], bbox_list_temp])

    content = merge_elements_initially(content)
    content = split_elements_initially(content)
    return content

def merge_elements_initially(content):
    # merge
    def merge_words(item): 
        text_array = item[0][0]
        font_style_array = item[0][1]
        font_size_array = item[0][2]
        bbox_array = item[1]
#        print('bbox_array  ',bbox_array)
        new_text = []
        new_font_style = [font_style_array[0]]
        new_font_size = [font_size_array[0]]
        new_bbox = []
        start_bbox = (bbox_array[0][0], bbox_array[0][1])
        joined_text = text_array[0]
        length = len(bbox_array)
        index = 1
        while index < length:
            gap = bbox_array[index][0] - bbox_array[index - 1][2]
            same_y_axis = (bbox_array[index][1] == bbox_array[index - 1][1])
        
            if gap <= 0 and same_y_axis:
                joined_text += text_array[index]
            else:
                new_text.append(joined_text)
                end_bbox = (bbox_array[index - 1][2], bbox_array[index - 1][3])
                bbox = start_bbox + end_bbox
                new_bbox.append(bbox)
                new_font_style.append(font_style_array[index])
                new_font_size.append(font_size_array[index])
                start_bbox = (bbox_array[index][0], bbox_array[index][1])
                joined_text = text_array[index]
            index += 1
        new_text.append(joined_text)
        end_bbox = (bbox_array[index - 1][2], bbox_array[index - 1][3])
        bbox = start_bbox + end_bbox
        new_bbox.append(bbox)
        new_words = [[new_text, new_font_style, new_font_size], new_bbox]
        return new_words
    
    new_content = []
    for item in content:
        result = merge_words(item)
        new_content.append(result)
#    print(new_content)
    return new_content

def split_elements_initially(content):
    def split_elements(item):
        text_array = item[0][0]
        font_style_array = item[0][1]
        font_size_array = item[0][2]
        bbox_array = item[1]
        all_content = []
        new_text = []
        new_font_style = []
        new_font_size = []
        new_bbox = []
        previous_bottom = float('Inf')
        length = len(bbox_array)
        for index in range(length):
            bbox = bbox_array[index]
            text = text_array[index]
            font_style = font_style_array[index]
            font_size = font_size_array[index]
            same_line = bbox[1] <= previous_bottom
            if same_line:
                new_text.append(text)
                new_font_style.append(font_style)
                new_font_size.append(font_size)
                new_bbox.append(bbox)
            else:
                all_content.append([[new_text, new_font_style, new_font_size], 
                                    new_bbox])
                new_text = [text]
                new_font_style = [font_style]
                new_font_size = [font_size]
                new_bbox = [bbox]
            previous_bottom = bbox[3]
        if len(new_bbox) > 0:
            all_content.append([[new_text, new_font_style, new_font_size], new_bbox])
        return all_content
    
    new_content = []
    for item in content:
        result = split_elements(item)
        new_content = new_content + result
#    print(new_content)
    return new_content




def EBE_check_page_type_thresholds_v_1_0_0(content):
    """
    This function checks if the page type is portrait or landscape, and then
    gets a threshold for defining the footer text
    """
    
    bbox3_list = []
    bbox4_list = []
    for i in range(len(content)):
#        text = content[i][0][0]
#        bbox2 = content[i][1][0][1]
        bbox3_list.append(content[i][1][-1][2])
        bbox4_list.append(content[i][1][-1][3])
#        if i < 5 and bbox2 > 700:
#            page_number_list.append(content[i])
#        else:
#            content_list.append(content[i])
    
    max_right = max(bbox3_list)
    max_bottom = max(bbox4_list)
    
    if max_right > max_bottom:
        #print('This is a landscape document')
        threshold = 500
    else:
        #print('This is a portrait document')
        threshold = 780
    
    return threshold

def EBE_get_headers_and_footers(content):
    
    """
    This function goes through the page and checks whether the page is a header, footer or normal content
    """
    
    # Get the footer threshold
    footer_threshold = EBE_check_page_type_thresholds_v_1_0_0(content)
    
    content_list = []
    header_list = []
    footer_list = []
    
    for i in range(len(content)):
        text = content[i][0][0]
        bbox2 = content[i][1][0][1]
        if bbox2 < 80: # checks if the text is at the top and is in bold
            if len(content[i][0][0]) == 1:
                font = content[i][0][1][0]
                if 'bold' in font.lower():
                    header_list.append(content[i])
                else:
                    content_list.append(content[i])
            else:
                content_list.append(content[i])
        elif bbox2 > footer_threshold: # checks if the text is beyond the footer threshold
            footer_list.append(content[i])
        else:
            content_list.append(content[i]) # if none of the two conditions above are satistified then it is classified as normal text

    return content_list, header_list, footer_list



def is_unique(bboxes):
    bboxes1 = [bbox[1] for bbox in bboxes]
    unique_bboxes = set(bboxes1)
    if len(unique_bboxes) == 1:
        return True
    minimum = min(unique_bboxes)
    for bbox in unique_bboxes:
        if bbox - minimum > 5:
            return False
    return True

        

def check_uniqueness(content):
    not_unique_top = 0
    for item in content:
        bboxes = item[1]
#        print(bboxes)
#        print()
        if not is_unique(bboxes):
            not_unique_top += 1
            print(item[1][0][1])
            print(item[0][0][0])
    return not_unique_top



def EBE_seperate_multiline_content_v_1_0_0(content):
    """
    This function was built to deal with situations where multiple content lines are merged into 
    a single content line, it separates them so that we essentially have each line in the page as
    an individual line. 
    
    Change(23/06/2019): added a bit of slack so that it doesn't do the multiline stuff when the difference is below a threshold
    """
    print()
    f_name = EBE_seperate_multiline_content_v_1_0_0.__name__
    print("%s function started with %s errors on Unique bbox1 values "% (f_name, check_uniqueness(content)))
#    print(check_uniqueness(content))
    diff_list = []
    for i in range(len(content)):
        if i > 0:
            
#            print()
#            print('gtgt  ',content[i][1][0][1])
            curr_box1 = content[i][1][0][1]
            prev_box1 = content[i-1][1][0][1]
            diff = abs(curr_box1 - prev_box1)
#            print(diff)
            if diff < 40:
                diff_list.append(diff)
        #    print(content[i][1][0])
#            print()
    
    threshold = 1.05 * min(diff_list) ## change (This has been changed to 0.95 to deal with cases where the in difference is what you actually want to use to separate the lines)


    content_list = []
    ### Build functionality to ensure that the page content is truly split line-by-line
    for i in range(len(content)):
#        print(i)
        #print(content[i])
#        print(content[i][0][0])
        bbox = content[i][1]
        #print()
        
        
        # find the number of unique bboxs and then build on from here
        #**** tweak this part so that it doesnt look for exact matches but looks for values +/- 2 of the previous value
        box1_list = []
        box0_list = []
        for box in bbox:
            box1_list.append(int(box[1]))
            box0_list.append(int(box[0]))
        unique_box1 = list(set(box1_list))
        unique_box0 = list(set(box0_list))
        unique_box1 = sorted(unique_box1)
#        print(box1_list)
#        print(unique_box1)
        
        ## Change(23/06/2019): we put a threshold of 2 before you accept it as being different
        count = 0
        
        if len(box1_list) > 1:
            if len(unique_box0) == 1: ## change 03/07/2019: added functionality to only do the separation when all lines start from the same box0 value
                for ii in range(len(box1_list)):
                    diff = abs(box1_list[ii] - box1_list[ii-1])
                    if diff > threshold: ## change: we have changed this from 2.5 to the minimum line separation found in the original content lines
                        count += 1
            
        if count > 1:
#            print('This is a content line that needs to be split!')
#            print(content[i])
            for box1 in unique_box1:
                text_00 = [] # to store the text
                text_01 = [] # to store the font names
                text_02 = [] # to store the font sizes
                bbox_list = []
#                print(box1)
#                print()
                indices = [i for i, x in enumerate(box1_list) if x == box1]
                for ind in indices:
                    text_00.append(content[i][0][0][ind])
                    text_01.append(content[i][0][1][ind])
                    text_02.append(content[i][0][2][ind])
                    bbox_list.append(content[i][1][ind])
                new_line = [[text_00, text_01, text_02], bbox_list]
#                print(new_line)
#                print()
                content_list.append(new_line)
                
        else:
            content_list.append(content[i])
#        print()
    f_name = EBE_seperate_multiline_content_v_1_0_0.__name__
    print("%s function ended with %s errors on Unique bbox1 values "% (f_name, check_uniqueness(content_list)))
    print()
    return content_list

def get_chunk_min_start_index(chunk):
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


def EBE_remove_merge_sublists_v_1_0_0(merge_combinations):
    """
    This function removes cases where we have sublists in the merge_combinations
    """
    reject_list = []
    for i in range(len(merge_combinations)):
        curr = merge_combinations[i]
        
        count = 0
        # now check if its a sublist of all the other lists
        for combs in merge_combinations:
    #        output = sublist(curr, combs) 
            output =  all(elem in curr  for elem in combs)
            #print(output)
            if output:
                if curr != combs:
                    reject_list.append(combs)
    
    merge_combinations_new = []
    for i in range(len(merge_combinations)):
        if merge_combinations[i] not in reject_list:
            merge_combinations_new.append(merge_combinations[i])
    
    return merge_combinations_new


def EBE_deal_with_line_misalignment_v_1_0_1(content):
    """
    Improvements have been made here to deal with edge cases around dealing with realigments
    """
    f_name = EBE_deal_with_line_misalignment_v_1_0_1.__name__
    print("%s function started with %s errors on Unique bbox1 values "% (f_name, check_uniqueness(content)))
    min_start_index = get_chunk_min_start_index(content)  
        
    ## Build functionality to sort the contents by line
    merge_index = []
    count = 0
    for i in range(len(content)):
        if i > 0:
#            print(content[i][0][0])
#            print()
            curr_box1 = content[i][1][0][1]
            prev_box1 = content[i-1][1][0][1]
            curr_box3 = content[i][1][0][3] # we have added functionality here to look at the minimum diff between the box1 and the box 3
            prev_box3 = content[i-1][1][0][3]
            diff_1 = curr_box1 - prev_box1
            diff_3 = curr_box3 - prev_box3
            diff = min(diff_1, diff_3)
#            print(diff)
#            print()
#            print()
            
            if diff <= 5:
#                print('**********')
#                print(content[i][0][0])
                first = content[i][1][0][0]
#                print(first)
#                print()
                if first > min_start_index + 25:
#                    print('This should be merged in')
#                    print('These are the surrounding text')
                    compare_index = [i-3, i-2, i-1, i+1, i+2]
                    for vals in compare_index:
                        try:
                            start = content[vals][1][0][0]
                            if start < min_start_index + 25:
                                curr_box1 = content[i][1][0][1]
                                prev_box1 = content[vals][1][0][1]
                                curr_box3 = content[i][1][0][3]
                                prev_box3 = content[vals][1][0][3]
                                diff2_1 = curr_box1 - prev_box1
                                diff2_3 = curr_box3 - prev_box3
                                diff2 = min(diff2_1, diff2_3)
                                if abs(diff2) <= 5:
#                                    print(content[vals][0][0])
#                                    print(diff2)
#                                    print('This is a potential merging companion')
#                                    print(vals, i)
                                    merge_index.append([vals, i])
                                    count += 1
                                    break
#                                    print()
                            else:
#                                print('Checking other lines that may not be at the min start index')
                                curr_box1 = content[i][1][0][1]
                                prev_box1 = content[vals][1][0][1]
                                curr_box3 = content[i][1][0][3]
                                prev_box3 = content[vals][1][0][3]
                                diff2_1 = curr_box1 - prev_box1
                                diff2_3 = curr_box3 - prev_box3
                                diff2 = min(diff2_1, diff2_3)
                                if abs(diff2) <= 1:
#                                    print(content[vals][0][0])
#                                    print(diff2)
#                                    print('This is a potential merging companion')
#                                    print(vals, i)
                                    merge_index.append([vals, i])
                                    count += 1
                                    break
#                                    print()
                        except:
#                            print('An error was encountered when looking for %s' % vals)
                            continue
#                    print()
#                    print()
                else:
#                    print('This is the second case')
#                    print()
                    compare_index = [i-3, i-2, i-1, i+1, i+2]
                    for vals in compare_index:
                        if vals < len(content):
                            try:
                                start = content[vals][1][0][0]
                            except:
                                start = content[vals][1][0]
                            if start > min_start_index + 25:
                                curr_box1 = content[i][1][0][1]
                                prev_box1 = content[vals][1][0][1]
                                curr_box3 = content[i][1][0][3]
                                prev_box3 = content[vals][1][0][3]
                                diff2_1 = curr_box1 - prev_box1
                                diff2_3 = curr_box3 - prev_box3
                                diff2 = min(diff2_1, diff2_3)
                                if abs(diff2) <= 5:
    #                                print(content[vals][0][0])
    #                                print(diff2)
    #                                print('This is a potential merging companion')
    #                                print(vals, i)
                                    merge_index.append([vals, i])
                                    count += 1
    #                                print()
                                
#            if count == 0 and diff <= 5:
#                print('_______')
#                print('A pairing was not found for the content below:')
#                print(content[i][0][0])
            
    
    from collections import Counter
    ## Work on the merge list
    if len(merge_index) > 0:
#        print('We have seen irregularities in the lining of the content rows and will fix it now')
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
        merge_combinations = EBE_remove_merge_sublists_v_1_0_0(merge_combinations)
#        print(merge_combinations)
        
        comb_indices_list = []
        
        for combs in merge_index:
            comb_indices_list += combs
            
        comb_indices_list_final = list(set(comb_indices_list))
        
                    
        ### Now that you know which ones are to be merged, time to merge them
        content_line_list = []
        
        for comb in merge_combinations:
        
            text_00 = [] # to store the text
            text_01 = [] # to store the font names
            text_02 = [] # to store the font sizes
            bbox_list = []
            
            for ind in comb:
                curr_content = content[ind]
                text = curr_content[0][0]
                for ii in range(len(text)):
                    temp = curr_content[0][0][ii]
                    if temp != ' ': # this removes cases where its blank, if its blank then we dont save it
                        text2 = curr_content[0][0][ii]
                        text_00.append(text2.strip())
                        text_01.append(curr_content[0][1][ii])
                        text_02.append(curr_content[0][2][ii])
                        bbox_list.append(curr_content[1][ii])
            new_line = [[text_00, text_01, text_02], bbox_list]
#            print(new_line)
#            print()
            
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
        
            content_line_list.append(new_line)
        
        
        for i in range(len(content)):
            if i not in comb_indices_list_final:
                content_line_list.append(content[i])
        
        line_list = []
        line_index = []
        try:
            for i in range(len(content_line_list)):
                line_list.append(content_line_list[i][1][0][1])
                line_index.append(i)
        except:
            content_line_list = content_line_list[1:]
            for i in range(len(content_line_list)):
#                print(content_line_list[i][1])
                line_list.append(content_line_list[i][1][0][1])
                line_index.append(i)
             
            
            
        # make sure the new line is properly sorted
        sorted_index = [i[0] for i in sorted(enumerate(line_list), key=lambda x:x[1])]
        line_index = [line_index[i] for i in sorted_index]
        #print(line_index)
        
        content_line_list = [content_line_list[i] for i in line_index]
        f_name = EBE_deal_with_line_misalignment_v_1_0_1.__name__
        print("%s function Ended with %s errors on Unique bbox1 values "% (f_name, check_uniqueness(content_line_list)))
        print()
        return content_line_list
    
    else:
        f_name = EBE_deal_with_line_misalignment_v_1_0_1.__name__
        print("%s function ended with %s errors on Unique bbox1 values "% (f_name, check_uniqueness(content)))
        print()
        return content
    
    
def EBE_cleanup_content_and_remove_blanks_v_1_0_0(content):
    """
    There are cases (like in page 11 of elysian 2) where a lot of blanks are found in the data,
    probably due to some limitation in how fitz works, this function cleans out the blanks
    """
    f_name = EBE_cleanup_content_and_remove_blanks_v_1_0_0.__name__
    print("%s function Started with %s errors on Unique bbox1 values "% (f_name, check_uniqueness(content)))
    content_line_list = []
    
    for i in range(len(content)):
        if len(content[i][0][0]) > 0:
            text_00 = [] # to store the text
            text_01 = [] # to store the font names
            text_02 = [] # to store the font sizes
            bbox_list = []
            
            curr_content = content[i]
            text = curr_content[0][0]
            for ii in range(len(text)):
                temp = curr_content[0][0][ii]
                if temp != ' ': # this removes cases where its blank, if its blank then we dont save it
                    text_00.append(curr_content[0][0][ii].strip())
                    text_01.append(curr_content[0][1][ii])
                    text_02.append(curr_content[0][2][ii])
                    bbox_list.append(curr_content[1][ii])
            
            if len(text_00) > 0: # change 02/07/2019: deals with issues where the content line is blank
                new_line = [[text_00, text_01, text_02], bbox_list]
                content_line_list.append(new_line)
    f_name = EBE_cleanup_content_and_remove_blanks_v_1_0_0.__name__
    print("%s function Ended with %s errors on Unique bbox1 values "% (f_name, check_uniqueness(content_line_list)))
    print()
    return content_line_list 
    

def EBE_cleanup_large_text_content_line_v_1_0_0(content):
    """
    This function deals with cases like what we see in page 6 Elysian 1 where the entire text block is seen as one line, and our model
    erronously interprets it as a table. We carry out the splitting manually before chunking etc.
    """
    f_name = EBE_cleanup_large_text_content_line_v_1_0_0.__name__
    print("%s function Started with %s errors on Unique bbox1 values "% (f_name, check_uniqueness(content)))
    content_line_list = []
    for i in range(len(content)):
        cont_len = len(content[i][0][0])
        
        
        if cont_len > 20:
            cont = content[i]
#            print('This is a large block of text that has been squashed up for some reason. We will split up the text into individual lines now')
            for i in range(len(cont[0][0])):
                new_line = [[[cont[0][0][i]], [cont[0][1][i]], [cont[0][2][i]]], [cont[1][i]]]
                content_line_list.append(new_line)
        else:
            content_line_list.append(content[i])
    f_name = EBE_cleanup_large_text_content_line_v_1_0_0.__name__
    print("%s function Ended with %s errors on Unique bbox1 values "% (f_name, check_uniqueness(content_line_list)))
    print()
    return content_line_list

def EBE_get_dominant_text_type(content):
    num_table = 0
    num_text = 0
    threshold = 0.5
    for item in content:
        text = item[0]
        if len(text[0]) <= 1:
            num_text += 1
        else:
            num_table += 1
    total = num_text + num_table
    return "text" if (num_text/total) >= threshold else "table"

#
def sort_content_v_1_0_0(content):
    """
    # Build a quick function to sort the order in which things appear on the contents list by the bbox 2 values
    # The bbox2 value is a measure of the vertical distance of a line from the top, so its a good proxy for the spacing
    # between lines in the page of a pdf
    
    ** Something to be cautios of is that this function won't work if you have cases where there are text blocks on multiple lines
      so you may have to consider going to the old approach of finding anomalous chunks and ignoring them, or building a specific 
      rule case that deals with the issue we're seeing here, but thats an issue for later
    """
    dominant_text_type = EBE_get_dominant_text_type(content)
    if dominant_text_type == "text" :
        return EBE_sort_text(content)# if dominant_text_type == "text" else EBE_sort_table(content)
    else:
        return EBE_sort_table(content)

def EBE_sort_text(content):
    bbox2_list = []
    difference = 70
    minimum = min(content, key=lambda x: x[1][0][0])[1][0][0]
    for i in range(len(content)):
        temp = content[i]
        bbox = temp[1]
        left = bbox[0][0] if bbox[0][0] > difference else minimum
        bbox2 = (bbox[0][1], left) #this gets the bbox2 value for every line in the contents (top, left)
        bbox2_list.append(bbox2)
    
    sorted_bbox_index = [i[0] for i in sorted(enumerate(bbox2_list), key=lambda x:(x[1][0] + x[1][1]**2))]
#    print('sorted_bbox_index   ',sorted_bbox_index)
    sorted_content = [content[i] for i in sorted_bbox_index]
#    print('sorted_content   ',sorted_content)
#    sorted_content = sort_text_by_bbox0_2(content)
    return sorted_content

def EBE_sort_table(content):
    bbox2_list = []
    for i in range(len(content)):
        temp = content[i]
        bbox = temp[1]
        bbox2 = bbox[0][1] #this gets the bbox2 value for every line in the contents
        bbox2_list.append(bbox2)
    
    sorted_bbox_index = [i[0] for i in sorted(enumerate(bbox2_list), key=lambda x:x[1])]
    sorted_content = [content[i] for i in sorted_bbox_index]
    
    return sorted_content


        

def check_sort_double_column_text(content):
    new_c = content
    # This funtion deals with 2-columns page and sorting them accordingly
    f_name = check_sort_double_column_text.__name__
    print("%s function Started with %s errors on Unique bbox1 values "% (f_name, check_uniqueness(content)))
    new_content = []
    dominant_text_type = EBE_get_dominant_text_type(content) # check for page content type ie. table otr Text
    is_table_in_page = False
    is_Appendix = False
    is_table = []
    Appendix = []
    for i in range(len(content)): # if there are multiple text and small table
        text = content[i][0][0]
        print(len(text))
        for i in text:
            if not i.isdigit() and len(text) == 2 and len(text) > 2:
                Appendix.append(text)
        if len(text) > 2:
            hh = []
            for i in text:
                for ii in i:
                    if ii.isdigit() and len(text) > 3:
                        hh.append(i)
                        
                    
            is_table.append(hh)
                
    if len(is_table) > 3: # check if its actually a table 
        for i in is_table:
            if len(i) > 3:
                is_table_in_page = True
    
#    print('Appendix   ',Appendix)
    if len(Appendix) > 17:
        is_Appendix = True
#        print('OLOLOLOLOLOLOLOLOLOLOLOLOLOLOLOLOLO')
#        
    if dominant_text_type == "text" and is_table_in_page:
#        print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK")
        new_content = new_c            
    elif not is_table_in_page and dominant_text_type == "text" and not is_Appendix:
#        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        #        check if there is a 2-column format in a text page
        double_column = False    
        for i, j in enumerate(content):
            bbox0 = content[i][1][0][0]
            if bbox0 > 280:
                double_column = True  
        new_content1 = []
        new_content2 = []
        if double_column:
            for i in range(len(content)):
                bbox_0 = content[i][1][0][0]
                if bbox_0 < 190:
                    new_content1.append(content[i])
                else:
                    new_content2.append(content[i])
        else:
            new_content = content   #.sort(key=lambda x: x[0][1][0][1])
        
        if new_content1 and new_content2:
            new_content1.sort(key=lambda x: x[1][0][1])
            new_content2.sort(key=lambda x: x[1][0][1])
        
            new_content.extend(new_content1)
            new_content.extend(new_content2)
        else:
            new_content = content   #.sort(key=lambda x: x[0][1][0][1])
    
    elif is_Appendix: #check if its 2-column table
#        print('CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC')
        content.sort(key=lambda x: x[1][0][1])
        new_content = content
    else:
        check_if_no_2_column_in_page = False # this is to deal with pages with both tables and two column text
        for i, j in enumerate(content):
            text = content[i][0][0]
            bbox0 = content[i][1][0][0]
            bbox1 = content[i][1][0][1]
            if bbox0 > 280:
                if '\uf0b7' in text:
                    check_if_no_2_column_in_page = True
        if check_if_no_2_column_in_page:
            new_content = new_c
        else:
            print("UIUIUIUIUIUIUIUIUIIIIIIIIIIIIIIIIIIII")
            content.sort(key=lambda x: x[1][0][1])
            new_content = content
    f_name = check_sort_double_column_text.__name__
    print("%s function Ended with %s errors on Unique bbox1 values "% (f_name, check_uniqueness(content)))
    return new_content


def EBE_check_bbox1_misalignment(content):
    new_content = []
    indx = []
    for i, j in enumerate(content):
        cuur_content = content[i]
        prev_content = content[i-1]
        curr_bbox1 = content[i][1][0][1]
        prev_bbox2 = content[i-1][1][0][1]
        calc = int(curr_bbox1) - int(prev_bbox2)
#        print('calc =  ',calc)
        check = False
        if calc > -2 and calc < 5: # check if there are close bbox 1 that are meant to be on same line
            check = True
        
        
        if int(curr_bbox1) != int(prev_bbox2) and calc > 5 or len(content) < 5:  # check if we had bbox that look alike in integer ie. the first digit before the decimal point
            new_content.append(content[i])
        elif int(curr_bbox1) == int(prev_bbox2):
            line_number = content.index(prev_content)
            indx.append(line_number) # get the index of the previous content containing the first of the identical bbox 1
            curr_text = cuur_content[0][0] # current text
            prev_text = prev_content[0][0] # previous text
            
            curr_font = cuur_content[0][1] # current font
            prev_font = prev_content[0][1] # previous font
            
            curr_font_size = cuur_content[0][2] # current font size
            prev_font_size = prev_content[0][2] # previous font size
            
            curr_bbox = cuur_content[1] # current bbox
            prev_bbox = prev_content[1] # previous bbox
            
            if prev_bbox2 < curr_bbox1: # check which bbox 1 is less and append the other
                new_text =  prev_text + curr_text # merge current and previous text
                new_font =  prev_font + curr_font # merge current and previous font
                new_font_size = prev_font_size + curr_font_size # merge current and previous font size
                new_bbox = prev_bbox + curr_bbox # merge current and previous bbox
            else:
                new_text = curr_text + prev_text # merge current and previous text
                new_font = curr_font + prev_font # merge current and previous font
                new_font_size = curr_font_size + prev_font_size # merge current and previous font size
                new_bbox = curr_bbox + prev_bbox # merge current and previous bbox
            
            new_line = [[new_text, new_font, new_font_size], new_bbox] # create a new line
            new_content.append(new_line) # adding the new line to the content
        elif int(curr_bbox1) != int(prev_bbox2) and check:
#            pass
            line_number = content.index(prev_content)
            indx.append(line_number) # get the index of the previous content containing the first of the identical bbox 1
            curr_text = cuur_content[0][0] # current text
            prev_text = prev_content[0][0] # previous text
            
            curr_font = cuur_content[0][1] # current font
            prev_font = prev_content[0][1] # previous font
            
            curr_font_size = cuur_content[0][2] # current font size
            prev_font_size = prev_content[0][2] # previous font size
            
            curr_bbox = cuur_content[1] # current bbox
            prev_bbox = prev_content[1] # previous bbox
            
            if prev_bbox2 < curr_bbox1: # check which bbox 1 is less and append the other
                new_text =  prev_text + curr_text # merge current and previous text
                new_font =  prev_font + curr_font # merge current and previous font
                new_font_size = prev_font_size + curr_font_size # merge current and previous font size
                new_bbox = prev_bbox + curr_bbox # merge current and previous bbox
            else:
                new_text = curr_text + prev_text # merge current and previous text
                new_font = curr_font + prev_font # merge current and previous font
                new_font_size = curr_font_size + prev_font_size # merge current and previous font size
                new_bbox = curr_bbox + prev_bbox # merge current and previous bbox
            
            new_line = [[new_text, new_font, new_font_size], new_bbox] # create a new line
            new_content.append(new_line) # adding the new line to the content
            
        else:
             new_content.append(content[i])
#            pass
    if len(indx) == 1:
        del new_content[indx[0]] # delete the previous line, if we successfully created one
    elif len(indx) > 1: # check if there are multi line with same issue and delete them as well
        for ind in sorted(indx, reverse=True):
            del new_content[ind]
    return new_content

