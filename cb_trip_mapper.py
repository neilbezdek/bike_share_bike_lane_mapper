import os
import googlemaps
import pandas as pd
import polyline
from collections import defaultdict
import cPickle as pickle

def load_raw_trips(filepath):
    df = pd.read_csv(filepath)
    df['start_coords'] = list(zip(df['start station latitude'], df['start station longitude']))
    df['end_coords'] = list(zip(df['end station latitude'], df['end station longitude']))
    return df.where(df['start_coords'] != df['end_coords'])

def raw_trips_to_route_counts(df):
    df_counts = df.groupby(['start_coords','end_coords']).count()['tripduration'].to_frame()
    df_counts.reset_index(inplace=True)
    return df_counts.rename(columns = {'tripduration':'tripcount'}).sort_values('tripcount',ascending=False)

def update_df_with_directions(df):
    df['driving_dir'] = df.apply(lambda row: get_directions(row,'driving'), axis = 1)
    df['biking_dir'] = df.apply(lambda row: get_directions(row,'bicycling'), axis = 1)

def get_directions(row, mode):
    return gmap.directions(row['start_coords'],row['end_coords'],mode = mode, avoid='highways')

def add_polyline_to_segments(segments, line):
    error_counter = 0
    try:
        points = polyline.decode(line)
        legs = zip(points[:-1],points[1:])
        for leg in legs:
            segments[leg]+=1
    except:
        error_counter += 1
        print error_counter

def update_all_segments(df):
    df['driving_dir'].apply(lambda x: add_polyline_to_segments(car_segments, x[0]['overview_polyline']['points']))
    df['biking_dir'].apply(lambda y: add_polyline_to_segments(bike_segments, y[0]['overview_polyline']['points']))



if __name__ == '__main__':

    gmap = googlemaps.Client(key=os.environ['GOOGLE_API_KEY'])

    # create df of raw trips
    filepath = '201609-citibike-tripdata.csv'
    # df = load_raw_trips(filepath)

    #create df of trip counts
    # df_counts = raw_trips_to_route_counts(df)
    # df_counts.to_pickle('df_counts.pkl')
    df_counts = pd.read_pickle('df_counts.pkl')


    #create sample df to test with
    # df_sample = df_counts.iloc[:500].reset_index(drop=True)

    #get driving and biking directions
    # update_df_with_directions(df_sample)
    # df_sample.to_pickle('df_sample.pkl')

    df_sample = pd.read_pickle('df_counts.pkl')
    bike_segments = defaultdict(float)
    car_segments = defaultdict(float)

    update_all_segments(df_sample)


#plotly and mapbox


#df['full_coords'] = list(zip(df['start_coords'], df['end_coords']))


# dirs = gmap.directions(df_sample.ix[0,'start_coords'],df_sample.ix[0,'end_coords'])
