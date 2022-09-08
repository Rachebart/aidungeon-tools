from cgitb import small
import json
import sys
from typing import List
import pandas as pd

pd.set_option('display.max_rows', None)


if __name__ == "__main__":

    df = pd.read_json('worlds/worldinfo.{}.json'.format(sys.argv[1]))
    df = df[['name','type','description']]

    locs = df.loc[df['type']=='location']
    chars = df.loc[df['type']=='character']
    factions = df.loc[df['type']=='faction']
    classes = df.loc[df['type']=='class']
    vehicles = df.loc[df['type']=='vehicle']

    print("locations: {0}".format(locs.shape[0]))
    print("characters: {0}".format(chars.shape[0]))
    print("factions: {0}".format(factions.shape[0]))
    print("classes: {0}".format(classes.shape[0]))
    print("vehicles: {0}".format(vehicles.shape[0]))

    print(factions)


