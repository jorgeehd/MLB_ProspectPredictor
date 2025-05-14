
import pandas as pd 
import numpy as np


def obp(hits , bb , hbp, ab ,sf):
    if ab + bb + hbp + sf == 0: 
        print("Error due to division by 0")
    return (hits +  bb + hbp)/(ab + bb + hbp + sf)

def slg(hits  ,b2, b3 , hr , ab): 

    if ab == 0: 
        print("Error due to division by 0")
    
    return (hits - b2 -b3  + 2*b2 +  3*b3 + 4*hr)/(ab)

def ba( hits, ab ) : 

    if ab == 0: 
        print("Error due to division by 0")

    return (hits/ab)


def na_cleaner(df : pd.DataFrame): 


    #Drop unused statistics 
    tmp = df.drop(["IBB" , "GDP" , "OPS" , "TB"], axis= 1)
    
    #Check for na_values
    features_with_nan = na_check(tmp)

    if len(features_with_nan) > 0 :

        obp_nan_mask = tmp["OBP"].isna()
        slg_nan_mask = tmp["SLG"].isna()
        ba_nan_mask = tmp["BA"].isna()

        tmp.loc[obp_nan_mask, "OBP"] = tmp.loc[obp_nan_mask].apply(
        lambda x: obp(x["H"], x["BB"], x["HBP"], x["AB"], x["SF"]),
        axis=1
        )

        tmp.loc[slg_nan_mask, "SLG"] = tmp.loc[slg_nan_mask].apply(
        lambda x: slg(x["H"], x["2B"], x["3B"], x["HR"], x["AB"]),
        axis=1
        )   

        tmp.loc[ba_nan_mask, "BA"] = tmp.loc[ba_nan_mask].apply(
        lambda x: ba(x["H"], x["AB"]),
        axis=1
        )

        features_with_nan =na_check(tmp) #if na, then big L 4 us 

        if (len(features_with_nan) > 0): 
            tmp.fillna(0, inplace=True)

        return tmp
    return tmp


def na_check(df : pd.DataFrame): 

    features_with_nan  = {}
    for feature in df.columns: 
        has_nan = df[feature].isna().any()
        print(f"{feature} has NaN values: {has_nan}")
        if has_nan: 
            num_of_nans = df[feature].isna().sum()
            features_with_nan[feature] = num_of_nans
            print(f"    {feature} has {num_of_nans} nans")

    
    

    return features_with_nan
