#!/usr/bin/env python3

import pandas as pd
import os

BIDS_dir="/path/to/input/"

#open participants.tsv

df = pd.read_table(os.path.join(BIDS_dir, 'participants.tsv'))

#grab lines associated with one subject

columns=df.head()


for subject in df['participant_id']:
	subject_df = df.loc[df['participant_id'] == subject]
	subject_df_wo_subid = subject_df.loc[:, ~subject_df.columns.isin(['participant_id'])]
	subject_df_new_index = subject_df_wo_subid.reset_index(drop=True)
	subject_df_new_index.to_csv(os.path.join(BIDS_dir, subject, subject + "_sessions.tsv"), sep="\t", index=False, header=['session_id','age'])
	
	 
