#!/usr/bin/env python3

"""
Greg Conan: gregmconan@gmail.com
Created 2024-02-21
Updated 2024-03-20
"""
# Standard imports
import argparse
import json
import os
import pdb
import re

# Type hints to help define inputs and outputs in function headers
from typing import Any, Callable, Hashable, Iterable, List, Optional

# External imports
import numpy as np
import pandas as pd


def ensure_ID_cols_prefixed(a_df: pd.DataFrame, cols_ID: Iterable[str]
                            ) -> pd.DataFrame:
    return a_df.apply(lambda col: ensure_ID_col_prefixed(col) 
                      if col.name in cols_ID else col)


def ensure_ID_col_prefixed(col: pd.Series):
    prefix = f"{col.name.lower()[:3]}-"
    return col.apply(lambda el: ensure_prefixed(el, prefix))


def ensure_prefixed(each_ID: str, prefix: str) -> str:
    return (each_ID if (not each_ID) or each_ID.startswith(prefix)
            else prefix + each_ID)


def extract_from_json(json_path):
    """
    :param json_path: String, a valid path to a real readable .json file
    :return: Dictionary, the contents of the file at json_path
    """
    with open(json_path, 'r') as infile:
        return json.load(infile)


def get_sub_or_ses_ID_in(pattern: re.Pattern, str_to_find_ID_in: str) -> str:
    """
    Get the subject- or session-ID from a string by using the Regex pattern
    :param pattern: re.Pattern, _description_
    :param str_to_find_ID_in: str, _description_
    :return: str, _description_
    """
    matched_ID = re.search(pattern, str_to_find_ID_in)
    if matched_ID:
        matched_ID = matched_ID.groups()
        if len(matched_ID) == 1:
            matched_ID = matched_ID[0]
    return matched_ID


def get_run_numbers_from(fnames: pd.Series) -> pd.Series:
    return fnames.str.extract(r"_(\d+)\.err")[0]


def get_sub_ses_info_from_run_file(run_fpath: str) -> List[str]:
    """
    :param run_fpath: String, valid path to readable text file with run info
    :return: List of 2 strings, subject ID and session ID; either can be None
    """
    with open(run_fpath, 'r') as run_infile:
        contents = run_infile.read()
    both_IDs = {"subject": None, "ses": None}
    for which_ID in both_IDs.keys():
        each_ID = get_sub_or_ses_ID_in(
            r"(?:{}_id=)(\w+)".format(which_ID), contents
        )
        both_IDs[which_ID] = ensure_prefixed(each_ID, which_ID[:3] + "-")
    return [both_IDs["subject"], both_IDs["ses"]]


class LazyDict(dict):
    """
    Dictionary subclass that can get/set items...
    ...as object-attributes: self.item is self['item']. Benefit: You can get/
       set items by using '.' accessor OR using variable names in brackets.
    ...and ignore the 'default=' code until it's needed, ONLY evaluating it
       after failing to get/set an existing key. Benefit: The 'default='
       code does not need to be valid if self already has the key.
    Extended version of LazyButHonestDict from stackoverflow.com/q/17532929
    Does not change core functionality of the Python dict type.
    TODO: Should this subclass dict or collections.UserDict?
    TODO: Right now, trying to overwrite a LazyDict method or a core dict
          attribute will silently fail: the new value can be accessed through
          dict methods but not as an attribute. Maybe worth fixing eventually?
    """
    def __getattr__(self, __name: str):
        """
        For convenience, access items as object attributes.
        :param __name: String naming this instance's item/attribute to return
        :return: Object (any) mapped to __name in this instance
        """
        return self.__getitem__(__name)
    
    def __setattr__(self, __name: str, __value: Any) -> None:
        """
        For convenience, set items as object attributes.
        :param __name: String, the key to map __value to in this instance
        :param __value: Object (any) to store in this instance
        """
        self.__setitem__(__name, __value)

    def lazyget(self, key: Hashable, get_if_absent:
                Optional[Callable] = lambda: None) -> Any:
        """
        LazyButHonestDict.lazyget from stackoverflow.com/q/17532929
        :param key: Object (hashable) to use as a dict key
        :param get_if_absent: function that returns the default value
        :return: _type_, _description_
        """
        return self[key] if self.get(key) is not None else get_if_absent()
    
    def lazysetdefault(self, key: Hashable, set_if_absent:
                       Optional[Callable] = lambda: None) -> Any:
        """
        LazyButHonestDict.lazysetdefault from stackoverflow.com/q/17532929 
        :param key: Object (hashable) to use as a dict key
        :param set_if_absent: function that returns the default value
        :return: _type_, _description_
        """
        return (self[key] if self.get(key) is not None else
                self.setdefault(key, set_if_absent()))
    

def is_nothing(thing: Any) -> bool:
    if thing is None:
        result = True
    elif isinstance(thing, float):
        result = np.isnan(thing) or not thing
    elif hasattr(thing, "empty"):  # get_module_name_of(thing) == "pandas":
        result = thing.empty
    else:
        result = not thing
    return result


def remove_err_and_out_files(err_file_path: str) -> None:
    """
    Delete file at err_file_path and its corresponding .out file 
    :param err_file_path: String, valid .err file path
    """
    for each_log_file in (err_file_path,
                          err_file_path.replace(".err", ".out")):
        if os.path.exists(each_log_file):
            print(f"Deleting {each_log_file}")
            os.remove(each_log_file)


def stringify_num_ser(nums: pd.Series) -> str:
    """ 
    :param nums: pd.Series of whole number floats
    :return: String of all items in a_list, single-quoted and comma-separated
    """
    # return nums.sort_values().to_string(float_format="%.0f", index=False, header=False).strip().replace('\n',',')
    return ",".join(nums.sort_values().astype(int).astype(str))


def stringify_whole_num_or_empty(a_number: float) -> str:
    return f"{a_number:.0f}" if a_number else ""


def stringify_list(a_list: list) -> str:
    """ 
    :param a_list: List (any)
    :return: String of all items in a_list, single-quoted and comma-separated
    """
    result = ""       
    if a_list and isinstance(a_list, list):
        list_with_str_els = [str(el) for el in a_list]
        result = "'{}'".format("','".join(list_with_str_els) if len(a_list)
                               > 1 else list_with_str_els[0])
    return result


def valid_readable_json_content(path: Any) -> dict:
    """
    Throw exception unless parameter is a valid path to a readable .JSON file.
    :param path: Parameter to check if it represents a valid filepath
    :return: String representing a valid filepath
    """
    return validate(path, valid_readable_file,
                    extract_from_json, "Cannot read a .JSON file at '{}'")


def valid_readable_file(path: Any) -> str:
    """
    Throw exception unless parameter is a valid readable filepath string. Use
    this, not argparse.FileType('r') which leaves an open file handle.
    :param path: Parameter to check if it represents a valid filepath
    :return: String representing a valid filepath
    """
    return validate(path, lambda x: os.access(x, os.R_OK),
                    os.path.abspath, "Cannot read file at '{}'")


def valid_output_dir(path: Any) -> str:
    """
    Try to make a folder for new files at path; throw exception if that fails
    :param path: String which is a valid (not necessarily real) folder path
    :return: String which is a validated absolute path to real writeable folder
    """
    return validate(path, lambda x: os.access(x, os.W_OK),
                    valid_readable_dir, "Cannot create directory at '{}'", 
                    lambda y: os.makedirs(y, exist_ok=True))


def valid_readable_dir(path: Any) -> str:
    """
    :param path: Parameter to check if it represents a valid directory path
    :return: String representing a valid directory path
    """
    return validate(path, os.path.isdir, valid_readable_file,
                    "Cannot read directory at '{}'")


def validate(to_validate: Any, is_real: Callable, make_valid: Callable,
             err_msg: str, prepare:Callable = None):
    """
    Parent/base function used by different type validation functions. Raises an
    argparse.ArgumentTypeError if the input object is somehow invalid.
    :param to_validate: String to check if it represents a valid object 
    :param is_real: Function which returns true iff to_validate is real
    :param make_valid: Function which returns a fully validated object
    :param err_msg: String to show to user to tell them what is invalid
    :param prepare: Function to run before validation
    :return: to_validate, but fully validated
    """
    try:
        if prepare:
            prepare(to_validate)
        assert is_real(to_validate)
        return make_valid(to_validate)
    except (OSError, TypeError, AssertionError, ValueError, 
            argparse.ArgumentTypeError):
        raise argparse.ArgumentTypeError(err_msg.format(to_validate))