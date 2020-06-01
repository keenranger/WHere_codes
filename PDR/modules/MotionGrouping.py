# fig = plt.figure()
# fig.suptitle(file_name)
# ax1 = fig.add_subplot(2,1,1)
# ax2 = fig.add_subplot(2,1,2)
# ax1.scatter(pvdetect.acc_sq_df['time'], pvdetect.acc_sq_df['value_z'], c='orange')
# ax1.set_title("Mrz")

# motion_df = pd.DataFrame(columns=("time", "value"))
# for idx,row in pvdetect.acc_sq_df.iterrows():
#     if row['value_z'] > 0.6:
#         motion_df.loc[idx] = [row['time'], 1]
#     else:
#         motion_df.loc[idx] = [row['time'], 0]
#
# ax2.plot(motion_df['time'], motion_df['value'], c = 'black')
# ax2.set_title("Motion")
# ax2.set_xlabel('time')
