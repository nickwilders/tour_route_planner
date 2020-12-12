import requests as requests
import re
from bs4 import BeautifulSoup
import numpy as np
import datetime
import pandas as pd
import os
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta


# WEB SCRAPE 


def show_details(urls):
    
    if type(urls) == str:
        url_list = [urls]
    else:
        url_list = urls
     
    full_title_list = []
    tour_descript_list = []
    show_type_list = []
    tour_opening_list = []
    tour_closing_list = []
    o_or_r_list = []
    
    
    for url in url_list:       
    
        # WEB SCRAPE
        url_text = requests.get(url)
        soup = BeautifulSoup(url_text.text, 'html5lib')
        
        # SHOW TITLE
        show_title = soup.find_all('h3')[0]
        show_title = str(show_title).split('>')[1].split('<')[0]
        
        # TOUR DESCRIPT
        tour_descript = soup.find_all('div', class_='tag-block-compact')[0]
        tour_descript = str(tour_descript).split('>')[2].split('<')[0]
        tour_descript_list.append(tour_descript)

        # CLARIFYING TITLE 
        full_title = str(show_title + " (" + tour_descript + ")")
        full_title_list.append(full_title)

        # PLAY / MUSICAL
        show_type = soup.find_all('div', class_='tag-block-compact')[1]
        show_type = str(show_type).split('>')[2].split('<')[0]
        show_type_list.append(show_type)

        # TOUR OPENING DATE
        tour_opening = soup.find_all('div', class_='col s6 txt-paddings')
        tour_opening = str(tour_opening).split('>')[2].split('<')[0]
        try:
            tour_opening = datetime.datetime.strptime(tour_opening, '%b %d, %Y')
        except:
            tour_opening = 'N/A'
        tour_opening_list.append(tour_opening)

        # TOUR CLOSING DATE
        tour_closing = soup.find_all('div', class_='col s6 txt-paddings vertical-divider')
        tour_closing = str(tour_closing).split('>')[2].split('<')[0]
        try:
            tour_closing = datetime.datetime.strptime(tour_closing, '%b %d, %Y')
        except:
            tour_closing = 'N/A'
        tour_closing_list.append(tour_closing)

        # ORIGINAL / REVIVAL
        original_or_revival = soup.find('div', class_='col s12 txt-paddings tag-block-compact')
        original_or_revival = soup.find('div', class_= 'col s12 txt-paddings tag-block-compact').find_all('i', text='Original')
        if len(original_or_revival)==1:
            original_or_revival = str(original_or_revival).split('>')[1].split('<')[0]
        else:
            original_or_revival = 'Revival'
        o_or_r_list.append(original_or_revival)
       
        
        # Return progress for reference
        if type(urls) != str:
            progress = round(((len(tour_opening_list) / len(url_list))*100),3)
            print("This script is " + str(progress) + "% complete.")
        
        
    d = {'title': full_title_list, 'tour_descript': tour_descript_list, 'show_type': show_type_list,
        'tour_opening': tour_opening_list, 'tour_closing': tour_closing_list, 'original_or_revival': o_or_r_list,
        'reference_url': url_list}
    df = pd.DataFrame(data=d)

    return df



def show_stops(urls):
    
    if type(urls) == str:
        url_list = [urls]
    else:
        url_list = urls
        
    full_title_list = []
    city_list = []
    date_list = []
    theatre_list = []
       
    
    for url in url_list:
        # WEB SCRAPE
        url_text = requests.get(url)
        soup = BeautifulSoup(url_text.text, 'html5lib')
        
        # SHOW TITLE
        show_title = soup.find_all('h3')[0]
        show_title = str(show_title).split('>')[1].split('<')[0]
        
        # TOUR DESCRIPT
        tour_descript = soup.find_all('div', class_='tag-block-compact')[0]
        tour_descript = str(tour_descript).split('>')[2].split('<')[0]

        # LIST OF CITIES ON TOUR
        cities = soup.find_all('div', class_='col s12 m3 filter-key')
        for city in cities:
            city = str(city).split('>')[1].split('<')[0]
            city_list.append(city)

        # DATES IN TOWN (past, current, and future)
        dates = soup.find_all('div', class_='col s12 m4')
        for date in dates:
            date = str(date).split('>')[1].split('<')[0]
            date_list.append(date)

        # THEATRE NAME
        theatres = soup.find_all('div', class_='col s12 m5')
        for theatre in theatres:
            theatre = str(theatre).split('>')[2].split('<')[0]
            theatre_list.append(theatre)
            
        # CLARIFYING TITLE
        full_title = str(show_title + " (" + tour_descript + ")")
        length = len(theatres)
        full_title_semi_list = [full_title] * length
        for title in full_title_semi_list:
            full_title_list.append(title)
    
    d = {'title': full_title_list, 'city': city_list, 'dates': date_list, 'theatre': theatre_list}
    df = pd.DataFrame(data=d)
    df = df.drop_duplicates().reset_index(drop=True)
    
    return df


def periodic_scrape(completed_list):
    
    full_stops_table = pd.read_csv('data/full_stops_table.csv')
    shows_since_2003 = pd.read_csv('data/open_broadway_data_shows_since_2003.csv')
    
    for i, show in enumerate(shows_since_2003.title):

        full_title = shows_since_2003.tour_descript.iloc[i]

        if show in completed_list or shows_since_2003.tour_descript.iloc[i] in completed_list:
            print(f'{show} has already been collected.')

            show_search_table = pd.DataFrame(data={'frequency': ['already collected'], 
                                                            'isPartial': ['already collected']})
            show_search_table['search_term'] = full_title
            show_search_table['geo_code'] = str('already collected')

        else:
            # Tracking function
            try:
                previous_show = shows_since_2003.title[i-1]
                print("\n- - - - - - - \n" + previous_show + " is complete." + "\n- - - - - - - \n")

            except:
                pass

            # Set iterative values from shows_since_2003 table
            show_title = [show]
            full_title = shows_since_2003.tour_descript.iloc[i]
            nyc_opening = shows_since_2003.opening_date.iloc[i]
            nyc_closing = shows_since_2003.closing_date.iloc[i]
            tour_opening = shows_since_2003.tour_opening.iloc[i]

            city_table = full_stops_table[full_stops_table.tour_descript == full_title]
            city_table = city_table.reset_index(drop=True)

            # Set iterative values for full_stops_table
            for n, city in enumerate(city_table.city_opening_date):
                tour_venue_opening = str(city_table.city_opening_date[n])[:10]
                tour_venue_closing = str(city_table.city_closing_date[n])[:10]
                location_tag = str(city_table.full_code[n])

                # convert opening night value to datetime and go back three months in time
                # code found at https://www.programiz.com/python-programming/datetime/strftime
                datetime_opening = dt.strptime(nyc_opening, '%Y-%m-%d')
                # set relative time delta
                three_mon_rel = relativedelta(months=-3)
                # Back in time! 
                starting_point_dt = datetime_opening + three_mon_rel
                # Reset date to string
                starting_point = starting_point_dt.strftime('%Y-%m-%d')

                # Repeat process for, add one date to end of closing
                datetime_closing = dt.strptime(tour_venue_closing, '%Y-%m-%d')
                one_mon_rel = relativedelta(months=1)
                ending_point_dt = datetime_closing + one_mon_rel
                ending_point = ending_point_dt.strftime('%Y-%m-%d')


                print(location_tag)


                # Search for term in geographic area
                try:
                    pytrend.build_payload(kw_list=show_title, timeframe=f'{starting_point} {ending_point}', geo=f'{location_tag}')
                    # set to table
                    interest_over_time_df = pytrend.interest_over_time()

                    # rename columns for graphing ease - also debug and if there were no search values returned, list an error
                    interest_over_time_df.columns = [ 'frequency', 'isPartial']
                except:
                    interest_over_time_df = pd.DataFrame(data={'frequency': ['collection error'], 
                                                            'isPartial': ['collection error']})

                # add search_term and geo_code for later reference
                interest_over_time_df['search_term'] = full_title
                interest_over_time_df['geo_code'] = location_tag

                if n==0:
                    show_search_table = interest_over_time_df
                else:
                    show_search_table = pd.concat([show_search_table, interest_over_time_df])

                show_progress = round(((n/len(city_table.tour_descript))*100),3)
                print(f"{full_title} is " + str(show_progress) + "% complete.")

        if i==0:
            final_table = show_search_table
        else:
            final_table = pd.concat([final_table, show_search_table])    

        # PROGRESS
        progress = round(((i/len(shows_since_2003.title))*100),3)
        print("\n- - - - - - - \n This script is " + str(progress) + "% complete, with " + str(len(final_table)) + ' entries.\n - - - - - - -\n')

    return final_table



# MODEL DEVELOPMENT

def second_smallest(numbers):
    m1, m2 = float('inf'), float('inf')
    for x in numbers:
        if x < m1:
            m1, m2 = x, m1
        elif x < m2:
            m2 = x
    return m2

def engagement_table(show_and_geo_code_list):
    
    from datetime import datetime as dt
    import numpy as np

    for i, pair in enumerate(show_and_geo_code_list):
        try:
            show = pair[0]
            geo_code = pair[1]


            # necessary imports
            merged_stops_data = pd.read_csv('data/merged_stops_data.csv')
            list_of_cities = pd.read_csv('data/list_of_cities.csv')
            df = pd.read_csv('data/WORKING_scrape_1128.csv')


            # if necessary, clean show title
            entered_show_title = show
            show = show.lower()
            no_parentheses_show=0

            if show[-1:] == ')':
                show.split('(')[0].strip()
            else:
                no_parentheses_show = show

            # set dataframe of interest
            df_over_time = df[df.search_term == show][df.geo_code == geo_code].reset_index(drop=True)
            df_over_time = df_over_time.drop(columns=['Unnamed: 0', 'Unnamed: 0.1', 'Unnamed: 0.1.1', 'Unnamed: 0.1.1.1', 'Unnamed: 0.1.1.1.1'])

            # set df_over_time to shorter timestamp for later processing
            df_over_time.timestamp = [x[:10] for x in df_over_time.timestamp]


            # SET SEARCH_TERM categorical variable
            search_term = show


            # SET GEO_CODE categorical variable
            geo_code = geo_code


            # NYC_CLOSEST

            # find nyc_opening_engagement feature
            df_showstop = merged_stops_data[merged_stops_data['title'] == no_parentheses_show][merged_stops_data['full_code'] == geo_code]
            if len(df_showstop) == 0:
                df_showstop = merged_stops_data[merged_stops_data['tour_descript'] == show][merged_stops_data['full_code'] == geo_code]
            #show_title = df_showstop.title.iloc[0]
            #full_title = df_showstop.tour_descript.iloc[0]
            #tour_opening = df_showstop.tour_opening.iloc[0][:10]
            nyc_opening = df_showstop.opening_date_nyc.iloc[0]

            if type(df_over_time.timestamp[0]) == str:
                df_over_time.timestamp = column_to_datetime(df_over_time.timestamp)
            if df_over_time.timestamp[0] > dt.strptime(nyc_opening, '%Y-%m-%d'):
                nyc_opening = dt.strftime(df_over_time.timestamp[0], '%Y-%m-%d')

            nyc_opening_closest = closest_date(nyc_opening, df_over_time)

            # SET NYC_OPENING_CLOSEST
            nyc_opening_engagement = df_over_time[df_over_time['timestamp'] == nyc_opening_closest].frequency.iloc[0]



            # EVENT_ENGAGEMENT

            from datetime import datetime as dt
            from dateutil.relativedelta import relativedelta

            date_dt = dt.strptime(nyc_opening, '%Y-%m-%d')
            if df_over_time.timestamp[0] > date_dt:
                date_dt = df_over_time.timestamp[0]

            three_months_before = dt.strftime(date_dt - relativedelta(months=3), '%Y-%m-%d')
            three_months_after = dt.strftime(date_dt + relativedelta(months=3), '%Y-%m-%d')
            before_closest = closest_date(three_months_before, df_over_time)
            after_closest = closest_date(three_months_after, df_over_time)
            before_index = df_over_time[df_over_time.timestamp == before_closest].index[0]
            after_index = df_over_time[df_over_time.timestamp == after_closest].index[0]

            # SET EVENT_ENGAGEMENT
            if before_index != after_index:
                event_engagement = df_over_time[before_index:after_index].frequency.mean()
            else:
                event_engagement = df_over_time[before_index].frequency


            # STATIC ENGAGEMENT

            tour_venue_opening = df_showstop.city_opening_date.iloc[0][:10]
            tour_venue_opening_closest = closest_date(tour_venue_opening, df_over_time)
            tour_venue_open_index = df_over_time[df_over_time.timestamp == tour_venue_opening_closest].index[0]

            # SET STATIC_ENGAGEMENT
            if tour_venue_open_index != after_index:
                static_engagement = df_over_time[after_index:tour_venue_open_index].frequency.mean()
            else:
                static_engagement = df_over_time.iloc[tour_venue_open_index.frequency]
                
            if tour_venue_open_index != after_index:
                static_engagement_max = df_over_time[after_index:tour_venue_open_index].frequency.max()
            else:
                static_engagement_max = df_over_time.iloc[tour_venue_open_index.frequency]
                
            # Find trait of if interest hits zero    
            if df_over_time[after_index:tour_venue_open_index].frequency.min() == 0:
                static_hits_zero = True
            else:
                static_hits_zero = False
            
            # Find SECOND SMALLEST VALUE (as smallest is often zero)
            if tour_venue_open_index != after_index:
                static_engagement_min = second_smallest(set(df_over_time[after_index:tour_venue_open_index].frequency))
            else:
                static_engagement_min = df_over_time.iloc[tour_venue_open_index.frequency]
                
            # TOUR OPEN ENGAGEMENT
            tour_open = df_showstop.tour_opening.iloc[0][:10]
            tour_open_closest = closest_date(tour_open, df_over_time)
            tour_open_index = df_over_time[df_over_time.timestamp == tour_open_closest].index[0]            

            # SET TOUR OPEN ENGAGEMENT
            if tour_venue_open_index != tour_open_index:
                tour_open_engagement = df_over_time[tour_open_index:tour_venue_open_index].frequency.mean()
            else:
                in_town_engagement = df_over_time.iloc[tour_venue_open_index].frequency

            # IN TOWN ENGAGEMENT
            tour_venue_closing = df_showstop.city_closing_date.iloc[0][:10]
            tour_venue_closing_closest = closest_date(tour_venue_closing, df_over_time)
            tour_venue_close_index = df_over_time[df_over_time.timestamp == tour_venue_closing_closest].index[0]

            # SET IN_TOWN_ENGAGEMENT
            if tour_venue_open_index != tour_venue_close_index:
                in_town_engagement = df_over_time[tour_venue_open_index:tour_venue_close_index].frequency.mean()
            else:
                in_town_engagement = df_over_time.iloc[tour_venue_open_index].frequency


        except:
            search_term = show
            geo_code = geo_code
            nyc_opening_engagement = 'merge error'
            event_engagement = 'merge error'
            static_engagement = 'merge error'
            static_engagement_max = 'merge error'
            static_engagement_min = 'merge error'
            static_hits_zero = 'merge error'
            tour_open_engagement = 'merge error'
            in_town_engagement = 'merge error'

    # CREATE ROW 

        row_for_df = pd.DataFrame([[search_term, geo_code, nyc_opening_engagement, event_engagement, 
                                    static_engagement, static_engagement_min, static_engagement_max, 
                                    static_hits_zero, tour_open_engagement, in_town_engagement]])
        row_for_df.columns = [['search_term', 'geo_code', 'nyc_opening_engagement', 'event_engagement', 
                               'static_engagement', 'static_engagement_min', 'static_engagement_max', 
                               'static_hits_zero', 'tour_open_engagement', 'in_town_engagement']]
        
        if i == 0:
            final_table = row_for_df
        else:
            final_table = pd.concat([final_table, row_for_df])
            
           
        completion = round(len(final_table) / len(show_and_geo_code_list), 2) * 100
        print(f'\n Job is {completion}% complete.\n')
           
    
    return final_table
    
    





# VISUALIZATION 

def column_to_datetime(column):
    timestamp_list = []
    
    for timestamp in column:
        try:
            date_time = dt.strptime(timestamp[:10], '%Y-%m-%d')
            timestamp_list.append(date_time)
        except:
            timestamp_list.append(timestamp)
    
    return timestamp_list



def clean_show_title(show_title):
    entered_show_title = show_title
    show_title = show_title.lower()
    no_parentheses_show=0

    if show_title[-1:] == ')':
        show_title.split('(')[0].strip()
    else:
        no_parentheses_show = show_title
      
    
    
def closest_date(date, df):
    
    # set date to datetime
    date_dt = dt.strptime(date, '%Y-%m-%d')
    
    # set other dates to datetime
    timestamp_list = column_to_datetime(df.timestamp)
    df.timestamp = timestamp_list
    
    # find minimum
    closest_date_dt = min(df.timestamp, key=lambda x: abs(x-date_dt))
    closest_date = closest_date_dt.strftime('%Y-%m-%d')
    # volume_at_date = df[df == closest_date][0]
    return closest_date



def extract_frequencies(show, geocode):
    
    scraped_data_no_duplicates = pd.read_csv('data/scraped_data_no_duplicates.csv')
    
    show = show.lower()
    data_fn = scraped_data_no_duplicates[scraped_data_no_duplicates['search_term'] == show]
    data_fn_city = data_fn[data_fn['geo_code'] == geocode]
    data_fn_city
    
    data_fn_city.frequency = data_fn_city.frequency.astype(int)
    
    data_fn_city = data_fn_city.reset_index(drop=True)
    
    data_fn_city.timestamp = column_to_datetime(data_fn_city.timestamp)
    
    return data_fn_city



def popularity_graph(show, geotag):
    
    merged_stops_data = pd.read_csv('data/merged_stops_data.csv')
    list_of_cities = pd.read_csv('data/list_of_cities.csv')
    
    entered_show_title = show
    show = show.lower()
    no_parentheses_show=0
    
    if show[-1:] == ')':
        show.split('(')[0].strip()
    else:
        no_parentheses_show = show

    df_showstop = merged_stops_data[merged_stops_data['title'] == no_parentheses_show][merged_stops_data['full_code'] == geotag]

    if len(df_showstop) == 0:
        df_showstop = merged_stops_data[merged_stops_data['tour_descript'] == show][merged_stops_data['full_code'] == geotag]
        
    show_title = df_showstop.title.iloc[0]
    full_title = df_showstop.tour_descript.iloc[0]
    nyc_opening = df_showstop.opening_date_nyc.iloc[0]
    tour_opening = df_showstop.tour_opening.iloc[0][:10]

    tour_venue_opening = df_showstop.city_opening_date.iloc[0]
    tour_venue_closing = df_showstop.city_closing_date.iloc[0]
    location_tag = geotag
    location_name = list_of_cities[list_of_cities.full_code == geotag].metro_area_name.iloc[0]
    #if len(location_name)>1:
    #    location_name = location_name.iloc[0]

    interest_over_time_df = extract_frequencies(show, geotag)
    
    if len(interest_over_time_df) == 0:
        show = str(show + ' (Tour)')
        interest_over_time_df = extract_frequencies(show, geotag)
        
    try:
        tour_closing = df_showstop.tour_closing.iloc[0][:10]
    except: 
        tour_closing = interest_over_time_df.timestamp.iloc[-1]


    nyc_closing = df_showstop.closing_date_nyc.iloc[0]
    
    import math 
    
    try:
        if math.isnan(nyc_closing): 
            nyc_closing = interest_over_time_df.timestamp.iloc[-1]
    except:
        pass
    
    # IMPORT necessary packages
    import seaborn as sns
    import matplotlib.pyplot as plt

    # SET Axis size and xlimits
    graph_lower = interest_over_time_df.timestamp[0]
    graph_upper = tour_venue_closing
    fig, ax = plt.subplots(figsize=(16,10))
    plt.xlim(graph_lower, graph_upper)

    # Use external function to determine nearest date to actual opening
    tour_opening_closest = closest_date(tour_opening, interest_over_time_df)
    nyc_opening_closest = closest_date(nyc_opening, interest_over_time_df)
    tour_venue_opening_closest = closest_date(tour_venue_opening[:10], interest_over_time_df)
    tour_opening_freq = interest_over_time_df[interest_over_time_df.timestamp == tour_opening_closest].frequency.iloc[0]
    nyc_opening_freq = interest_over_time_df[interest_over_time_df.timestamp == nyc_opening_closest].frequency
    tour_venue_opening_freq = interest_over_time_df[interest_over_time_df.timestamp == tour_venue_opening_closest].frequency

    # GRAPH line plot for search data over time period, and points for Tour and Broadway opening
    sns.lineplot(data=interest_over_time_df, x='timestamp', y='frequency', color='darkblue')
    plt.scatter(x=tour_opening, y=tour_opening_freq, s=100, c='black')
    plt.scatter(x=nyc_opening, y=nyc_opening_freq, s=100, c='black')

    # Create labels for Tour and Broadway Opening
    ax.text(tour_opening, tour_opening_freq+5, "Tour Opening", horizontalalignment='center', fontsize=15, color='black', 
            weight='semibold', bbox=dict(facecolor='white', edgecolor='green', boxstyle='round'))
    ax.text(nyc_opening, nyc_opening_freq+5, "Broadway Opening", horizontalalignment='center', fontsize=15, color='black', 
            weight='semibold', bbox=dict(facecolor='white', edgecolor='green', boxstyle='round'))
    ax.text(tour_venue_opening, tour_venue_opening_freq+5, f"Opening in {location_name}", horizontalalignment='center', fontsize=15, color='black', 
            weight='semibold', bbox=dict(facecolor='white', edgecolor='green', boxstyle='round'))

    # Set titles and X/Y labels
    ax.set_title(f'"{entered_show_title}" Search Term Popularity in {location_name}\n', fontsize = 20, weight='bold')
    ax.set_xlabel('\nMonth', fontsize=16)
    ax.set_ylabel('Relative\n Frequency', fontsize=16, rotation=0, labelpad=50)

    # Set vertical lines and highlighted regions corresponding to Broadway and National Tour running dates
    ax.axvline(x=tour_venue_opening, linewidth=1, color='black', alpha=.8, linestyle='--')
    ax.axvline(x=tour_venue_closing, linewidth=1, color='black', alpha=.8, linestyle='--')
    ax.axvspan(tour_venue_opening,tour_venue_closing, color ='green',alpha=.5)
    ax.axvline(x=tour_opening, linewidth=3, color='black', alpha=.8, linestyle='--')
    ax.axvspan(tour_opening,tour_closing, color ='green',alpha=.2)
    ax.axvspan(interest_over_time_df.timestamp[0],nyc_opening, color ='pink',alpha=.2)
    ax.axvline(x=nyc_opening, linewidth=3, color='black', alpha=.8, linestyle='--')

    # If NYC production has closed, include closing date - otherwise, do not include 
    if nyc_closing == 'N/A':
        ax.axvspan(nyc_opening, interest_over_time_df.index[-1], color ='yellow',alpha=.1)
    else:
        ax.axvline(x=nyc_closing, linewidth=3, color='black', alpha=.8, linestyle='--')
        ax.axvspan(nyc_opening, nyc_closing, color ='yellow',alpha=.1)

    # Create legend
    colors = ['lightpink', 'yellow', 'lightgreen', 'green']
    regions = ['Pre-Broadway', 'NYC Production \nRunning ', 'Tour Running', f'Tour in {location_name}']
    handlelist = [plt.plot([], marker="s", ls="", color=color, markeredgewidth=1, 
                           markeredgecolor='black')[0] for color in colors]
    plt.legend(handlelist,regions,loc='best', prop={"size":16}, framealpha=1, facecolor='white')

    # Set tight layout and SAVE 
    plt.tight_layout()
    plt.savefig(f'visualizations/search_term_by_area/{show_title.strip()} {location_tag}'.replace(' ', '_')
                .replace('-','_'));
    
    
    
    
    
    
    
    
def COVID_sentiment_in_DMA(DMA_code):
    import seaborn as sns
    import matplotlib.pyplot as plt
    from matplotlib.dates import MonthLocator
    
    tweets_with_DMA = pd.read_csv('data/tweets_with_DMA.csv')
    tweets_with_DMA.timestamp = pd.to_datetime(tweets_with_DMA.timestamp)

    tweet_amount = len(tweets_with_DMA[tweets_with_DMA.geo_code == DMA_code])
    dma_table = tweets_with_DMA[tweets_with_DMA.geo_code == DMA_code].groupby(['timestamp','DMA_name']).mean().reset_index()
    DMA_name = dma_table.DMA_name.iloc[0]

    fig, ax = plt.subplots(figsize=(13,8))

    sns.lineplot(data = dma_table, x = 'timestamp', y = 'polarity', color='darkblue', linewidth=1)
    
    sns.set_theme(style='whitegrid', font='Georgia')
    ax.grid(False)

    #ax.set(ylim=(dma_table.polarity.min(), dma_table.polarity.max())
    plt.ylim(dma_table.polarity.min(), dma_table.polarity.max())

    fig.tight_layout()
    ax.set_title(f'\n COVID Sentiment over Time in {DMA_name} \n({tweet_amount} Tweets)\n\n', fontsize=20)
    ax.set_xlabel('\nMonth (Year: 2020)', fontsize=16)
    # ax.set_yticklabels(['NEGATIVE -    -0.2', '-0.1', '0', '0.1', '0.2', '0.3', 'POSITIVE -    0.4'], fontsize=10)
    ax.xaxis.set_major_locator(MonthLocator())
    ax.set_xticklabels(['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax.set_ylabel('Tweet Polarity', fontsize=16, rotation = 0, labelpad=70)
    ax.axhline(y=0, linewidth=1, color='black', alpha=.6, linestyle='--')


    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    #ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tight_layout();

    plt.savefig(f'visualizations/covid_sentiment/{DMA_name}_COVID_sentiment')

