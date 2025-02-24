
import pandas as pd


def get_metadata(number):
    metadata_file = "Metadata_Participants.csv"
    meta_df = pd.read_csv(metadata_file)

    filtered_df = meta_df.query('ParticipantID == @number',inplace=False)

    age = filtered_df.at[0,"Age"]
    gender = filtered_df.at[0,"Gender"]
    nd_type = filtered_df.at[0,"Class"]
    score = filtered_df.at[0,"CARS Score"]

    return number, age, gender, nd_type, score


x,y,z,w,p = get_metadata(1)

print(x,y,z,w,p)