import numpy as np

def filter_percentile(df, col, up=95, down=5):
    """
    Return only subset with values inside the percentile range.
    """
    pup = np.percentile(df[col].values, up)
    pdw = np.percentile(df[col].values, down)

    s = (df[col]<pup) & (df[col]>pdw)
    df2 = df[s]

    return df2