def bias_calculator(mag_df):
    bias_df = mag_df[['x_uncalib', 'y_uncalib', 'z_uncalib']].quantile([0.01, 0.99]).sum()/2
    return bias_df

def bias_calibrator(mag_df, bias_df):
    mag_df[['x_uncalib', 'y_uncalib', 'z_uncalib']] = mag_df[['x_uncalib', 'y_uncalib', 'z_uncalib']][['x_uncalib', 'y_uncalib', 'z_uncalib']] - bias_df
    return mag_df

def scale_calculator(mag_df):
    scale_df = mag_df[['x_uncalib', 'y_uncalib', 'z_uncalib']].quantile([0.01, 0.99]).diff()/2
    max_num = scale_df.max(axis = 1).max()
    scale_df = scale_df/max_num
    return scale_df.max()

def scale_calibrator(mag_df, scale_df):
    mag_df[['x_uncalib', 'y_uncalib', 'z_uncalib']] = mag_df[['x_uncalib', 'y_uncalib', 'z_uncalib']] / scale_df
    return mag_df
