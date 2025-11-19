# Imports 
import pandas as pd
import numpy as np
import nltk 
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
import matplotlib.pyplot as plt

# Function to load data
def update_data(df):
    # Get tokenized, bigrams, trigrams
    df['tokenized'] = df['Description'].apply(lambda x: list(word_tokenize(x.lower()))) # Lower and tokenize
    df['bigrams'] = df['tokenized'].apply(lambda x: list(ngrams(x, 2)))  # Generate bigrams
    df['trigrams'] = df['tokenized'].apply(lambda x: list(ngrams(x, 3)))  # Generate trigrams

    # One hot encode
    df['is_ug'] = df['cat_type'] == 'ug'
    df['is_gr'] = df['cat_type'] == 'gr'
    df['is_both'] = df['cat_type'] == 'both'
    
    return df



# For single keyword 

def summarize_time_series(df, keyword):

    keyword = keyword.lower()

    n = len(keyword.split(' ')) # Find number of words in keyword

    ghost_df = df.copy()

    if n==1:
        ghost_df[keyword + '_present'] = ghost_df['tokenized'].apply(lambda x: keyword in x)
    elif n==2:
        ghost_df[keyword + '_present'] = ghost_df['bigrams'].apply(lambda x: tuple(keyword.split(' ')) in x)
    elif n>2:
        print("Keyword search only supports unigrams and bigrams thus far.")
        return None
    
    keyword_df = ghost_df[ghost_df[keyword + '_present'] == True]

    keyword_df = keyword_df.sort_values(by='start_yr', ascending=True)

    years = list(keyword_df['start_yr'].value_counts().keys())
    years.sort()

    counts = []
    ugs = []
    grs = []
    boths = []


    for year in years:
        keyword_ghost_df = keyword_df[keyword_df['start_yr'] == year]
        total_grad = ghost_df[ghost_df['start_yr'] == year]['is_gr'].sum()
        total_ug = ghost_df[ghost_df['start_yr'] == year]['is_ug'].sum()
        total_both = ghost_df[ghost_df['start_yr'] == year]['is_both'].sum()


        count = len(keyword_ghost_df)
        counts.append(count)
        print(f"Year: {year}, Count: {count}")
        ug_num = keyword_ghost_df['is_ug'].sum() / total_ug if total_ug > 0 else 0
        ugs.append(ug_num)
        gr_num = keyword_ghost_df['is_gr'].sum() / total_grad if total_grad > 0 else 0
        grs.append(gr_num)
        both_num = keyword_ghost_df['is_both'].sum() / total_both if total_both > 0 else 0
        boths.append(both_num)
    
    #plt.plot(years, counts, label=f'Total"')
    plt.plot(years, ugs, label='Undergrad')
    plt.plot(years, grs, label='Grad')
    plt.plot(years, boths, label='Both')
  
    plt.xlabel('Year')
    plt.ylabel('Percent of Courses')
    plt.title(f'Percentage of Courses Over Time with Keyword: "{keyword}"')

    plt.legend()
    plt.show()

# For list of keywords 
def summarize_time_series_list(df,keyword_list):
    ghost_df = df.copy()

    ghost_df['any_keyword_present'] = False

    for keyword in keyword_list:

        n = len(keyword.split(' ')) # Find number of words in keyword
    
        if n==1:
            ghost_df[keyword + '_present'] = ghost_df['tokenized'].apply(lambda x: keyword in x)
        elif n==2:
            ghost_df[keyword + '_present'] = ghost_df['bigrams'].apply(lambda x: tuple(keyword.split(' ')) in x)
        elif n==3:
            ghost_df[keyword + '_present'] = ghost_df['trigrams'].apply(lambda x: tuple(keyword.split(' ')) in x)
        elif n>3:
            print("Keyword search only supports unigrams, bigrams, and trigrams thus far.")
            return None
        
        ghost_df['any_keyword_present'] = ghost_df['any_keyword_present'] | ghost_df[keyword + '_present'] # This will stay positive if any keyword is present

    keyword_df = ghost_df[ghost_df['any_keyword_present'] == True]

    keyword_df = keyword_df.sort_values(by='start_yr', ascending=True)

    years = list(keyword_df['start_yr'].value_counts().keys())
    years.sort()

    counts = []
    ugs = []
    grs = []
    boths = []


    for year in years:
        keyword_ghost_df = keyword_df[keyword_df['start_yr'] == year]
        total_grad = ghost_df[ghost_df['start_yr'] == year]['is_gr'].sum()
        total_ug = ghost_df[ghost_df['start_yr'] == year]['is_ug'].sum()
        total_both = ghost_df[ghost_df['start_yr'] == year]['is_both'].sum()


        count = len(keyword_ghost_df)
        counts.append(count)
        print(f"Year: {year}, Count: {count}")
        ug_num = keyword_ghost_df['is_ug'].sum() / total_ug if total_ug > 0 else 0
        ugs.append(ug_num)
        gr_num = keyword_ghost_df['is_gr'].sum() / total_grad if total_grad > 0 else 0
        grs.append(gr_num)
        both_num = keyword_ghost_df['is_both'].sum() / total_both if total_both > 0 else 0
        boths.append(both_num)
    
    #plt.plot(years, counts, label=f'Total"')
    plt.plot(years, ugs, label='Undergrad')
    plt.plot(years, grs, label='Grad')
    plt.plot(years, boths, label='Both')
  
    plt.xlabel('Year')
    plt.ylabel('Percent of Courses')
    plt.title(f'Percentage of Courses Over Time with Keyword: "{keyword}"')

    plt.legend()
    plt.show()
        
    
            