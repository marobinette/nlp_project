### Imports ###

import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import animation

from PIL import Image
from matplotlib.patches import Patch, Circle
import matplotlib
matplotlib.rcParams['animation.embed_limit'] = 25 * 1024 * 1024

# Read and process pickle file, IPEDS lookup table, US Geo Data

# Pickle file

df = pd.read_pickle('../data/cleaned_courses.pkl') 

df['is_ug'] = df['cat_type'] == 'ug'
df['is_gr'] = df['cat_type'] == 'gr'
df['is_both'] = df['cat_type'] == 'both'

df['full_description'] = df['Title'] + ' ' + df['Description']
df['full_description'] = df['full_description'].apply(lambda x: x.lower())

# IPEDS 
ipeds_df = pd.read_csv('../data/ipeds_lookup.csv')

ipeds_df = ipeds_df[['UNITID','INSTNM','ADDR','CITY','STABBR','ZIP', 'COUNTYCD','COUNTYNM', 'LONGITUD','LATITUDE']] # Remove unnecessary columns

# GEO data
counties = gpd.read_file("../data/cb_2018_us_county_500k/")
counties = counties[~counties.STATEFP.isin(["72", "69", "60", "66", "78"])]
counties = counties.set_index("GEOID")

states = gpd.read_file("../data/cb_2018_us_state_500k/")
states = states[~states.STATEFP.isin(["72", "69", "60", "66", "78"])]

counties = counties.to_crs("ESRI:102003")
states = states.to_crs("ESRI:102003")

def translate_geometries(df, x, y, scale, rotate):
    df.loc[:, "geometry"] = df.geometry.translate(yoff=y, xoff=x)
    center = df.dissolve().centroid.iloc[0]
    df.loc[:, "geometry"] = df.geometry.scale(xfact=scale, yfact=scale, origin=center)
    df.loc[:, "geometry"] = df.geometry.rotate(rotate, origin=center)
    return df

def adjust_maps(df):
    df_main_land = df[~df.STATEFP.isin(["02", "15"])]
    df_alaska = df[df.STATEFP == "02"]
    df_hawaii = df[df.STATEFP == "15"]

    df_alaska = translate_geometries(df_alaska, 1300000, -4900000, 0.5, 32)
    df_hawaii = translate_geometries(df_hawaii, 5400000, -1500000, 1, 24)

    return pd.concat([df_main_land, df_alaska, df_hawaii])


counties = adjust_maps(counties)
states = adjust_maps(states)

counties['county_id'] = counties['STATEFP'] + counties['COUNTYFP'] # Use this to match with IPEDS data

# Objects 

class KeyWordSearch:
    def __init__(self, word):
        self.word = word.lower()

        ghost = df.copy()

        ghost[f'is_{self.word}'] = ghost['full_description'].apply(lambda x: self.word in x)

        self.df = ghost[ghost[f'is_{self.word}']].sort_values(by='start_yr', ascending=True)

        pass
    
    def time_series(self, percentage=True, IPEDS='', show=True):
        time_df = self.df.copy()
        years = list(self.df['start_yr'].value_counts().keys())
        years.sort()

        counts = []
        ugs = []
        grs = []
        boths = []

        if IPEDS != '': # If ID is specified, then filter for it 
            time_df = time_df[time_df['ipeds_id']==IPEDS]
            

        if percentage == True:
            metric = 'Percentage'

            for year in years:
                keyword_ghost_df = time_df[time_df['start_yr'] == year]
                total_grad = df[df['start_yr'] == year]['is_gr'].sum()
                total_ug = df[df['start_yr'] == year]['is_ug'].sum()
                total_both = df[df['start_yr'] == year]['is_both'].sum()


                count = len(keyword_ghost_df)
                counts.append(count)
                ug_num = keyword_ghost_df['is_ug'].sum() / total_ug if total_ug > 0 else 0
                ugs.append(ug_num)
                gr_num = keyword_ghost_df['is_gr'].sum() / total_grad if total_grad > 0 else 0
                grs.append(gr_num)
                both_num = keyword_ghost_df['is_both'].sum() / total_both if total_both > 0 else 0
                boths.append(both_num)

        elif percentage==False:
            metric = 'Counts'
            for year in years:
                keyword_ghost_df = time_df[time_df['start_yr'] == year]
                count = len(keyword_ghost_df)
                counts.append(count)
                ug_num = keyword_ghost_df['is_ug'].sum() 
                ugs.append(ug_num)
                gr_num = keyword_ghost_df['is_gr'].sum() 
                grs.append(gr_num)
                both_num = keyword_ghost_df['is_both'].sum()
                boths.append(both_num)

        if show==True: # Plot only if user wants
            
            #plt.plot(years, counts, label=f'Total"')
            plt.plot(years, ugs, label='Undergrad')
            plt.plot(years, grs, label='Grad')
            plt.plot(years, boths, label='Both')
        
            plt.xlabel('Year')
            plt.ylabel(f'{metric} of Courses')
            plt.title(f'{metric} of Courses Over Time with Keyword: "{self.word}"' + str(IPEDS))

            plt.legend()
            plt.show()

        return {'Years':years, 'ug':ugs, 'gr':grs, 'both':boths}

    def merge_to_ipeds(self):
        self.df['ipeds_id'] = self.df['ipeds_id'].astype(int)
        merged = pd.merge(self.df, ipeds_df, how='left',left_on='ipeds_id', right_on='UNITID')

        self.merged = merged

    def diffusion(self):
        self.merge_to_ipeds()
        # Build sorted year list and cumulative sets from self.merged
        years_sorted = sorted(self.merged['start_yr'].dropna().unique())
        cumulative_sets = []
        cum_set = set()
        for y in years_sorted:
            ids = self.merged.loc[self.merged['start_yr'] == y, 'COUNTYCD'].dropna().astype(int).unique().tolist()
            cum_set.update(ids)
            cumulative_sets.append(set(cum_set.copy()))

        # plotting params
        edge_color = "#30011E"
        background_color = "#fafafa"
        default_color = "mistyrose"
        highlight_color = "limegreen"

        fig, ax = plt.subplots(figsize=(14, 9))
        fig.patch.set_facecolor(background_color)
        ax.set_axis_off()

        def draw_frame(frame_idx):
            ax.clear()
            ax.set_axis_off()
            current_set = cumulative_sets[frame_idx]
            # compute color column for this frame
            colors = counties['county_id'].astype(int).apply(lambda cid: highlight_color if cid in current_set else default_color)
            counties.plot(ax=ax, color=colors, edgecolor=edge_color + "55")
            states.plot(ax=ax, edgecolor=edge_color, color="None", linewidth=1)
            ax.set_title(f"Cumulative counties with colleges up to {years_sorted[frame_idx]}", fontsize=16)
            return ax

        def update(frame_idx):
            draw_frame(frame_idx)
            return []

        anim = animation.FuncAnimation(fig, update, frames=len(years_sorted), interval=200, blit=False, repeat=True)

        return anim
    
### Number of courses instead of percentage ###

### Run for all keywords in list ###

class KeyWordListSearch:
    def __init__(self, keywords):
        self.keywords = [x.lower() for x in keywords]

        ghost_df = df.copy()

        ghost_df['any_keyword_present'] = False

        for keyword in self.keywords:

            ghost_df[f'is_{keyword}'] = ghost_df['full_description'].apply(lambda x: keyword in x) # Works for all keywords
            
            ghost_df['any_keyword_present'] = ghost_df['any_keyword_present'] | ghost_df[f'is_{keyword}'] # This will stay positive if any keyword is present

            keyword_df = ghost_df[ghost_df['any_keyword_present'] == True]

        self.df = keyword_df.sort_values(by='start_yr', ascending=True)

        pass
    
    def time_series(self, percentage=True, IPEDS='', show=True, category=''):
        time_df = self.df.copy()
        years = list(self.df['start_yr'].value_counts().keys())
        years.sort()

        counts = []
        ugs = []
        grs = []
        boths = []

        if IPEDS != '': # If ID is specified, then filter for it 
            time_df = time_df[time_df['ipeds_id']==IPEDS]
            

        if percentage == True:
            metric = 'Percentage'

            for year in years:
                keyword_ghost_df = time_df[time_df['start_yr'] == year]
                total_grad = df[df['start_yr'] == year]['is_gr'].sum()
                total_ug = df[df['start_yr'] == year]['is_ug'].sum()
                total_both = df[df['start_yr'] == year]['is_both'].sum()


                count = len(keyword_ghost_df)
                counts.append(count)
                ug_num = keyword_ghost_df['is_ug'].sum() / total_ug if total_ug > 0 else 0
                ugs.append(ug_num)
                gr_num = keyword_ghost_df['is_gr'].sum() / total_grad if total_grad > 0 else 0
                grs.append(gr_num)
                both_num = keyword_ghost_df['is_both'].sum() / total_both if total_both > 0 else 0
                boths.append(both_num)

        elif percentage==False:
            metric = 'Counts'
            for year in years:
                keyword_ghost_df = time_df[time_df['start_yr'] == year]
                count = len(keyword_ghost_df)
                counts.append(count)
                ug_num = keyword_ghost_df['is_ug'].sum() 
                ugs.append(ug_num)
                gr_num = keyword_ghost_df['is_gr'].sum() 
                grs.append(gr_num)
                both_num = keyword_ghost_df['is_both'].sum()
                boths.append(both_num)

        if show==True: # Plot only if user wants
            
            #plt.plot(years, counts, label=f'Total"')
            plt.plot(years, ugs, label='Undergrad')
            plt.plot(years, grs, label='Grad')
            plt.plot(years, boths, label='Both')
        
            plt.xlabel('Year')
            plt.ylabel(f'{metric} of Courses')
            plt.title(f'{metric} of {category} Courses Over Time' + str(IPEDS))

            plt.legend()
            plt.show()

        return {'Years':years, 'ug':ugs, 'gr':grs, 'both':boths}

    def merge_to_ipeds(self):
        self.df['ipeds_id'] = self.df['ipeds_id'].astype(int)
        merged = pd.merge(self.df, ipeds_df, how='left',left_on='ipeds_id', right_on='UNITID')

        self.merged = merged

    def diffusion(self):
        self.merge_to_ipeds()
        # Build sorted year list and cumulative sets from self.merged
        years_sorted = sorted(self.merged['start_yr'].dropna().unique())
        cumulative_sets = []
        cum_set = set()
        for y in years_sorted:
            ids = self.merged.loc[self.merged['start_yr'] == y, 'COUNTYCD'].dropna().astype(int).unique().tolist()
            cum_set.update(ids)
            cumulative_sets.append(set(cum_set.copy()))

        # plotting params
        edge_color = "#30011E"
        background_color = "#fafafa"
        default_color = "mistyrose"
        highlight_color = "limegreen"

        fig, ax = plt.subplots(figsize=(14, 9))
        fig.patch.set_facecolor(background_color)
        ax.set_axis_off()

        def draw_frame(frame_idx):
            ax.clear()
            ax.set_axis_off()
            current_set = cumulative_sets[frame_idx]
            # compute color column for this frame
            colors = counties['county_id'].astype(int).apply(lambda cid: highlight_color if cid in current_set else default_color)
            counties.plot(ax=ax, color=colors, edgecolor=edge_color + "55")
            states.plot(ax=ax, edgecolor=edge_color, color="None", linewidth=1)
            ax.set_title(f"Cumulative counties with colleges up to {years_sorted[frame_idx]}", fontsize=16)
            return ax

        def update(frame_idx):
            draw_frame(frame_idx)
            return []

        anim = animation.FuncAnimation(fig, update, frames=len(years_sorted), interval=200, blit=False, repeat=True)

        return anim

### UCLA, UVM, UND ###

