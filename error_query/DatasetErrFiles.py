#!/usr/bin/env python3

"""
Greg Conan: gregmconan@gmail.com
Created 2024-02-19
Updated 2024-03-20
"""
# Standard imports
import os
import pdb
import re

# Type hints to help define inputs and outputs in function headers
from typing import Any, List, Mapping, Optional

# External imports
import pandas as pd

# Local custom imports
from utilities import (ensure_ID_cols_prefixed, get_run_numbers_from,
                       get_sub_or_ses_ID_in, get_sub_ses_info_from_run_file,
                       is_nothing, LazyDict, remove_err_and_out_files,
                       stringify_num_ser, stringify_whole_num_or_empty)

# TODO:
#   - add ValueError message back in for sub ses without run file?
#   - make sure either run files dir or subject list is a required input?


class DatasetErrFiles:
    def __init__(self, err_strings: Mapping[str, str], logs_dir: str,
                 output_dir: str, run_dir: Optional[str] = None,
                 sub_IDs_CSV: Optional[str] = None, delete: bool = False,
                 add_err_log_path: bool = False,
                 dataset_id: Optional[str] = None, **_) -> None:
        """
        Collection of error files for a given dataset 
        :param err_strings: Dict mapping error name strings to the errors'
                            text content strings; --error-strings
        :param logs_dir: Valid path to existing output_logs directory to find
                         error log files in (any subdirectory of)
        :param output_dir: Valid path to existing directory to save this
                           script's output files into
        :param run_dir: Valid path to existing directory containing run files
        :param sub_IDs_CSV: Valid path to existing .csv file which
                            lists subject IDs to include.
        :param delete: True to delete .err/.out files, else False
        :param dataset_id: String naming the dataset
        """
        self.dataset_id = dataset_id
        self.dir = LazyDict(logs=logs_dir, run=run_dir, out=output_dir)
        self.subj_IDs_fpath = sub_IDs_CSV
        self.will_delete = delete

        # LazyDict[str, str] mapping short nicknames to self.df column names
        self.COLS = LazyDict(ID=["Subject_IDs", "Session_IDs"],
                             fpath="Error_Log_Paths", run="Run_Number",
                             recency="Recency", err="Errors", ix="ix",
                             dataset="Dataset_ID")
        self.COLS.from_err_file = [*self.COLS.ID, self.COLS.err]
        
        # Strings naming all of the different errors to search for
        self.errs = pd.Series(err_strings)
        self.errs.index.name = self.COLS.err
        self.errs.drop("undetermined_or_no", inplace=True)

        # List of columns to include in the output .csv files
        self.COLS.save = [*self.COLS.ID, self.COLS.run]
        if dataset_id:
            self.COLS.save.append(self.COLS.dataset)
        if add_err_log_path:
            self.COLS.save.append(self.COLS.fpath)

        # Regex pattern matchers to find subject and session IDs in text
        self.find = LazyDict(subj=re.compile(r"sub-([a-zA-Z0-9_]+)"),
                             ses=re.compile(r"ses-([a-zA-Z0-9_]+)"))
        
        self.df = self.make_df()

        # Identify the most recent error file for each subject session
        self.most_recent = self.remove_err_files_and_get_most_recent()

        # Get all error file paths without a subject ID to identify them
        self.no_sub_id = self.get_df_without_subj_ID()

        # If subject ID and session ID not found within the .err file, then 
        # extract info from the associated run file in the run_files directory
        if self.dir.get("run"):
            self.no_sub_id = self.no_sub_id.apply(
                self.add_missing_IDs_from_run_file_to, axis=1
            )
            self.df.update(self.no_sub_id)


    def add_dataset_ID_to(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add dataset ID to each row of df if -ID/--dataset-id in CLI args 
        :param df: pd.DataFrame to add a dataset ID column to
        :return: df, now with the dataset ID in every row of a new column
        """
        if self.dataset_id:
            df[self.COLS.dataset] = self.dataset_id
        return df


    def add_detail_cols_to(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        :param df: pd.DataFrame with a file path column (self.COLS.fpath)
        :return: df, now with columns of additional details (self.COLS.ID,
                 self.COLS.run, and self.COLS.recency) gleaned from the
                 files at the file path column
        """
        # Get each error file's subject, session ID, and errors
        df = df.reindex(columns=[self.COLS.fpath, *self.COLS.from_err_file,
                                 self.COLS.run, self.COLS.recency])
        df[self.COLS.from_err_file] = df[self.COLS.fpath].apply(
            self.get_info_from_err_file
        ).values.tolist()

        df[self.COLS.run] = get_run_numbers_from(df[self.COLS.fpath]
                                                 ).astype(float)

        # Check how recently each error file was updated [created?]
        df[self.COLS.recency] = df[self.COLS.fpath].apply(os.path.getctime)
        return df
    

    def add_missing_IDs_from_run_file_to(self, row: pd.Series) -> pd.Series:
        """
        If row does not have a subject or session ID, then get them from the
        associated run file
        :param row: pd.Series, self.df row which may not have a subj/ses ID
        :return: row, but now with a subject and session ID if we can find
                 them in the run file
        """
        sub_ses = row[self.COLS.ID]
        sub_ses_IDs = sub_ses.values.tolist()
        if sub_ses.isna().any():
            run = row.get(self.COLS.run)
            if not is_nothing(run):  # TODO This ignores filenames without run numbers. Should it look for "run1" instead?
                run_fpath = os.path.join(self.dir.run, "run" +
                                         stringify_whole_num_or_empty(run))
                if os.path.exists(run_fpath):
                    new_IDs = get_sub_ses_info_from_run_file(run_fpath)
                    for ix in range(len(sub_ses_IDs)):
                        if not sub_ses_IDs[ix]:
                            sub_ses_IDs[ix] = new_IDs[ix]
                        row[self.COLS.ID[ix]] = sub_ses_IDs[ix]
        return row


    def get_1st_err_in(self, file_content: str) -> str:
        """
        :param file_content: String, all content of a text file which might
                             contain any of the error strings in self.errs
        :return: String naming the first error in the file, or None if the 
                 file has no errors
        """  # Only keep the first error in the file
        # Get index of every error in file_content
        err_ixs = self.errs.apply(file_content.find)
        ixs_df = err_ixs[err_ixs > -1].reset_index(name=self.COLS.ix)

        # Return the error with the lowest index (or None if no errors found)
        return (None if ixs_df.empty else
                ixs_df.loc[ixs_df[self.COLS.ix].idxmin(), self.COLS.err])


    def get_info_from_err_file(self, err_file_path: str) -> list:
        """
        Read the file at err_file_path. Get subject ID, session ID, and any
        errors from its content. Return any missing IDs as Nones instead.
        :param err_file_path: String, valid path to readable error file
        :return: List of 3 items, each of which may be None:
                 0. subject ID string, or None if not specified in err file
                 1. session ID string, or None if not specified in err file
                 2. set of strings where each names an error in err file, or
                    None if the err file does not contain any errors
        """
        with open(err_file_path, 'r') as infile:
            file_content = infile.read()
        return [get_sub_or_ses_ID_in(self.find.subj, file_content),
                get_sub_or_ses_ID_in(self.find.ses, file_content),
                self.get_1st_err_in(file_content)]


    def get_most_recent_err_file_and_remove_others(self, sub_ses_df:
                                                   pd.DataFrame) -> pd.Series:
        """
        Get the most recent error file and delete the rest
        :param sub_ses_df: pd.DataFrame where the subject and session ID
                           columns each only have one value 
        :return: pd.Series, 1 self.df row with the most recent error file path
        """
        most_recent_row = None
        if not sub_ses_df.empty: 
            is_most_recent = (sub_ses_df[self.COLS.recency] ==
                              sub_ses_df[self.COLS.recency].max())
            most_recent_row = sub_ses_df[is_most_recent].iloc[0].to_dict()
            if self.will_delete:
                sub_ses_df[~is_most_recent
                           ][self.COLS.fpath].apply(remove_err_and_out_files)
        return most_recent_row
    

    def get_df_without_subj_ID(self) -> pd.DataFrame:
        """
        :return: pd.DataFrame, self.df excluding any rows with a subject ID
        """
        return self.df.loc[self.df[self.COLS.ID].isna().all(axis=1)]
    

    def list_err_files_in(self, logs_dir_path: str) -> List[str]:
        """
        :param logs_dir_path: String, valid path to readable directory that
                              contains .err files
        :return: List[str] of all valid readable .err file paths in logs dir
        """
        return [os.path.join(dirpath, fname)
                for dirpath, _, fnames in os.walk(logs_dir_path)
                for fname in fnames if fname.endswith(".err")]


    def make_df(self) -> pd.DataFrame:
        """
        :return: pd.DataFrame to save as self.df, with one row per log file
                 and the columns named in self.COLS
        """
        df = self.read_df_from_fpaths_in(self.dir.logs)
        df = self.add_detail_cols_to(df)
        df = ensure_ID_cols_prefixed(df, self.COLS.ID)
        
        # Filter to only get subjects in subject_IDs_CSV_fpath if it was given
        if self.subj_IDs_fpath:
            csv_df = self.read_IDs_df_from(self.subj_IDs_fpath)
            df = df.merge(csv_df, how="inner", on=self.COLS.ID)

        return self.add_dataset_ID_to(df)


    def read_df_from_fpaths_in(self, logs_dir: str) -> pd.DataFrame:
        """
        Get path to every error file in the output_logs_dir
        :param logs_dir: String, valid path to existing directory containing
                         output log files
        :return: pd.DataFrame with one column containing output error/log 
                 file paths
        """
        return pd.DataFrame({self.COLS.fpath:
                             self.list_err_files_in(logs_dir)})


    def read_IDs_df_from(self, subject_IDs_CSV_fpath: str) -> pd.DataFrame:
        """
        :param subject_IDs_CSV_fpath: String, valid path to existing .csv file
                                      with all subject IDs to include
        :return: pd.DataFrame of subject IDs
        """
        csv_df = pd.read_csv(subject_IDs_CSV_fpath)
        if self.COLS.get("ID"):
            csv_df.rename(columns={csv_df.columns[i]: self.COLS.ID[i] for i
                                   in range(len(self.COLS.ID))}, inplace=True)
        else:
            self.COLS["ID"] = csv_df.columns[:2].values.tolist()
        return ensure_ID_cols_prefixed(csv_df, self.COLS.ID)


    def remove_err_files_and_get_most_recent(self) -> pd.DataFrame:
        """
        Find the most recent .err file associated with each unique run number,
        and delete the rest of them if --delete 
        :return: pd.DataFrame, self.df subset with only the most recent files
        """
        return pd.DataFrame(self.df.groupby(self.COLS.run).apply(
            self.get_most_recent_err_file_and_remove_others
        ).dropna().values.tolist())


    def save_and_print_all_errs(self) -> None:
        """
        For each different kind of error, save a .csv file of the subject and
        session IDs (plus most recent error file path, if --add-err-log-path)
        """
        # Save .csv for each kind of error
        self.errs.reset_index()[self.COLS.err].apply(self.save_subj_ses_w_err)

        # Save .csv for err files that don't have a subject or session ID
        self.save_if_any(self.get_df_without_subj_ID(), "no_sub_id_errors"
                         ".csv", self.COLS.run, self.COLS.fpath)
        
        # Save .tsv that maps error types to run numbers affected
        runs_df = self.df.groupby([self.COLS.err]
                                  )[self.COLS.run].agg(stringify_num_ser)
        self.save_if_any(self.add_dataset_ID_to(runs_df), "run_numbers.tsv",
                         self.COLS.run, index=True, sep="\t")
                
        # Save .csv with all err types, putting the err file path column last
        all_fname = (f"{self.dataset_id}-all.csv" if self.dataset_id
                     else "all_err_types.csv")
        self.save_if_any(self.df, all_fname, *self.COLS.save[:-1],
                         self.COLS.err, self.COLS.save[-1])
    

    def save_subj_ses_w_err(self, err_name: str) -> pd.DataFrame:
        """
        :param err_name: String naming the error 
        :return: self.df, but only including runs that raised err_name
        """
        self.save_if_any(self.df[self.df[self.COLS.err] == err_name],
                         err_name + ".csv", *self.COLS.save)
            

    def save_if_any(self, df: pd.DataFrame, csv_fname: str,
                    *save_COLS: str, **save_kwargs: Any) -> None: 
        """
        Save all self.df subj-ses rows with (a) certain error(s) to a
        .csv or .tsv spreadsheet file
        :param df: pd.DataFrame to export into a new .csv file
        :param csv_fname: String naming the .csv file to save
        :param save_COLS: List[str] of names of columns to save in output file
        :param save_args: Dict of parameters to pass into pd.DataFrame.to_csv
        """
        if not df.empty:
            # Format run numbers without decimals when saving them as string
            save_kwargs["float_format"] = "%.0f"

            # Exclude index from output file unless specified otherwise
            save_kwargs.setdefault("index", False)

            # Save the output file and print a message saying so
            out_file_path = os.path.join(self.dir.out, csv_fname)
            df.to_csv(out_file_path, columns=save_COLS, **save_kwargs)
            print(f"Saved {df.shape[0]} entries to {out_file_path}")
            