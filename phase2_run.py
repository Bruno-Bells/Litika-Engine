#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 16:17:52 2019

@author: dr_d3mz
"""

"""
Phase 2: Convert raw content into chunks

A lot of the extra functions were actually created because of little niggly issues with the elysian document.
"""

unique_chunks, chunk_dict, chunk_type_dict = pdf_ebe.EBE_get_page_chunks_v_1_0_2(content)
unique_chunks = pdf_ebe.EBE_sort_unique_chunks_v_1_0_0(unique_chunks) # This sorts it by chunk number

#unique_chunks, chunk_dict, chunk_type_dict = pdf_ebe.EBE_separate_multiple_text_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict)
#unique_chunks = pdf_ebe.EBE_sort_unique_chunks_v_1_0_0(unique_chunks) # This sorts it by chunk number
#    
#unique_chunks, chunk_dict, chunk_type_dict = pdf_ebe.EBE_find_text_between_two_table_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict)
#unique_chunks = pdf_ebe.EBE_sort_unique_chunks_v_1_0_0(unique_chunks) # This sorts it by chunk number
#    
## Pause on this one for now   
#unique_chunks, chunk_dict, chunk_type_dict = pdf_ebe.EBE_fill_missing_row_key_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict)
#unique_chunks = pdf_ebe.EBE_sort_unique_chunks_v_1_0_0(unique_chunks) # This sorts it by chunk number    
#  
#    
#unique_chunks, chunk_dict, chunk_type_dict = pdf_ebe.EBE_merge_duplicated_line_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict)
#unique_chunks = pdf_ebe.EBE_sort_unique_chunks_v_1_0_0(unique_chunks) # This sorts it by chunk number   
#
#unique_chunks, chunk_dict, chunk_type_dict = pdf_ebe.EBE_merge_consecutive_table_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict)
#chunk_dict = pdf_ebe.EBE_sort_table_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict)
#unique_chunks = pdf_ebe.EBE_sort_unique_chunks_v_1_0_0(unique_chunks) # This sorts it by chunk number
#
#unique_chunks, chunk_dict, chunk_type_dict = pdf_ebe.EBE_check_for_multiple_box0_table_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict)
#unique_chunks = pdf_ebe.EBE_sort_unique_chunks_v_1_0_0(unique_chunks) # This sorts it by chunk number
# 
#unique_chunks, chunk_dict, chunk_type_dict = pdf_ebe.EBE_combine_table_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict) # merges table description chunk into table chunk
#unique_chunks = pdf_ebe.EBE_sort_unique_chunks_v_1_0_0(unique_chunks) # This sorts it by chunk number
#
#unique_chunks, chunk_dict, chunk_type_dict = pdf_ebe.EBE_clean_table_row_irregularities_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict) 
#unique_chunks = pdf_ebe.EBE_sort_unique_chunks_v_1_0_0(unique_chunks) # This sorts it by chunk number
#
#
#unique_chunks, chunk_dict, chunk_type_dict = pdf_ebe.EBE_merge_section_header_chunks_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict)
#unique_chunks = pdf_ebe.EBE_sort_unique_chunks_v_1_0_0(unique_chunks)
#
#try:
#    ## Merge text to table chunks if they pass the required criteria
#    unique_chunks, chunk_dict, chunk_type_dict = pdf_ebe.EBE_merge_surrounding_table_chunks_v_1_0_0(content, unique_chunks, chunk_dict, chunk_type_dict)
#except:
#    pass

# Get a dictionary of the table types
table_type_dict = pdf_ebe.EBE_get_table_type_dict_v_1_0_0(unique_chunks, chunk_dict, chunk_type_dict)
print(table_type_dict)

for i in range(len(unique_chunks)):
    curr_chunk_name = unique_chunks[i]
    print(curr_chunk_name)
    print()
    chunk = chunk_dict[curr_chunk_name]
    
    for i in range(len(chunk)):
        print(chunk[i][0][0])
        print()
    print()
    print()