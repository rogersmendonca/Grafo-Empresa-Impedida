# -*- encoding: utf-8 -*-
"""Módulo common.util

Módulo de contantes e funções utilitárias.

Autor: Rogers Reiche de Mendonça <rogers.rj@gmail.com>
Data: Setembro/2020
"""
import csv
from datetime import datetime
from distutils.util import strtobool
import glob
import os
import string
import time

import numpy as np
import pandas as pd 
from nltk import word_tokenize
from nltk.corpus import stopwords
from unicodedata import normalize
from xlrd import XLRDError

from .logging import log

E_SOURCE = 'source'
E_TARGET = 'target'
E_TIPO = 'tipo'
E_COLUMNS = [E_SOURCE, E_TARGET, E_TIPO]
V_DELIM = '-'
V_CONTRATO = 'C'
V_LICITACAO = 'L'
V_FORNECEDOR = 'F'
V_SOCIO = 'S'
V_SANCAO = 'Sa'
V_EMPREGADO = 'E'

V_PROP_TIPO = 'tipo'
V_PROP_SUBTIPO = 'subtipo'
V_PROP_ID = 'id'
V_PROP_DATA_INI = 'data_ini'
V_PROP_DATA_FIM = 'data_fim'

# TIPOS DE PESSOA
TIPO_PJ = 'J'
TIPO_PF = 'F'
TIPO_ESTRANGEIRO = 'E'

# Param Default
FILTER_MASK_EXPORT_TABLE_RESULT = "*[0-9]?[0-9].txt"
FILTER_MASK_CSV = "*.csv"

# lambdas usadas em df.apply          
LAMBDA_YYYYMMDD_TO_TIMESTAMP_DEFAULT_MIN = lambda x: yyyymmdd_to_Timestamp(x, pd.Timestamp.min)
LAMBDA_YYYYMMDD_TO_TIMESTAMP_DEFAULT_MAX = lambda x: yyyymmdd_to_Timestamp(x, pd.Timestamp.max)
def yyyymmdd_to_Timestamp(str_date: str, default_Timestamp: pd.Timestamp) -> pd.Timestamp: 
    return pd.to_datetime(str_date, format = '%Y%m%d') \
           if ((not is_blank(str_date)) and 
               (len(str_date) == 8) and 
               (str_date.isdigit()) and 
               (str_date[:2] in ['19', '20'])) \
           else default_Timestamp

def cnpj_raiz(cnpj: str, exc: str = None, must_fill: bool = True) -> str:
    cnpj = handling_cnpj(cnpj, exc, must_fill)
    return cnpj[:8]

def df_trim_all_columns(df: pd.DataFrame) -> pd.DataFrame:
    trim_strings = lambda x: x.strip() if isinstance(x, str) else x
    return df.applymap(trim_strings) if not is_null(df) else None

def drop_duplicates_reindex(df: pd.DataFrame, drop: bool = True) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop = drop) if not is_null(df) else None

def file_exists(file_path: str) -> bool:
    return (not is_blank(file_path)) and os.path.isfile(file_path) and os.access(file_path, os.R_OK)

def get_df_from_file(input_file: str, sep: str = ';', usecols: list = None, 
                     quotechar = '"', encoding = 'utf-8-sig', dtype = 'str', 
                     na_filter = False) -> pd.DataFrame:
    return get_df_from_files([input_file], sep, usecols, quotechar, encoding, 
                             dtype, na_filter)

def get_df_from_files(input_files: list, sep: str = ';', usecols: list = None, 
                      quotechar = '"', encoding = 'utf-8-sig', dtype = 'str', 
                      na_filter = False) -> pd.DataFrame:
    df = None
    
    for input_file in input_files:
        if file_exists(input_file):
            log(f"Lendo arquivo {input_file} ...")
            try:
                df_from_csv = read_csv(input_file,
                                       sep = sep,
                                       usecols = usecols,
                                       quotechar = quotechar,
                                       encoding = encoding,
                                       dtype = dtype,
                                       na_filter = na_filter)
            except UnicodeDecodeError:
                df_from_csv = read_csv(input_file,
                                       sep = sep,
                                       usecols = usecols,
                                       quotechar = quotechar,
                                       encoding = 'iso-8859-1',
                                       dtype = dtype,
                                       na_filter = na_filter)
                
            df = df_from_csv if df is None else df.append(df_from_csv)
            df = drop_duplicates_reindex(df)
        
    return df

def get_df_from_excel(input_file: str, sheet_name = 0, usecols = None, dtype = None, 
                       skiprows = None, na_values = None, parse_dates = False, 
                       date_parser = None, thousands = None, skipfooter = 0):
    return get_df_from_excels([input_file], sheet_name, usecols, dtype, skiprows, 
                              na_values, parse_dates, date_parser, thousands, skipfooter)

def get_df_from_excels(input_files: list, sheet_name = 0, usecols = None, dtype = None, 
                       skiprows = None, na_values = None, parse_dates = False, 
                       date_parser = None, thousands = None, skipfooter = 0):
    df = None
    
    for input_file in input_files:
        if file_exists(input_file):
            log(f"Lendo arquivo {input_file} ...")
            try:
                df_from_excel = read_excel(input_file,
                                           sheet_name = sheet_name,
                                           usecols = usecols,
                                           dtype = dtype,
                                           skiprows = skiprows,
                                           na_values = na_values,
                                           parse_dates = parse_dates,
                                           date_parser = date_parser,
                                           thousands = thousands,
                                           skipfooter = skipfooter)                
            except XLRDError:
                df_from_excel = None
                
            df = df_from_excel if df is None else df.append(df_from_excel)
            df = drop_duplicates_reindex(df)
        
    return df

def get_file_list(input_path: str, path_filter: str) -> list:
    return glob.glob(os.path.join(input_path, path_filter))

def handling_cnpj(cnpj: str, exc: str = None, must_fill: bool = True) -> str:
    cnpj = remove_punctuation(strip_val(cnpj), exc)
    return cnpj.zfill(14) if must_fill and not is_blank(cnpj) else cnpj

def handling_cpf(cpf: str, exc: str = None, must_fill: bool = True) -> str:
    cpf = remove_punctuation(strip_val(cpf), exc)
    return cpf.zfill(11) if must_fill and not is_blank(cpf) else cpf

def handling_timestamp(original_ts, default_ts: pd.Timestamp) -> pd.Timestamp:
    ts = to_timestamp(original_ts)
    return ts if not is_null(ts) else default_ts

def is_blank(x) -> bool:
    return strip_val(x) == ''

def is_null(x) -> bool:
    return pd.isnull(x) if (type(pd.isnull(x)) is bool) else False

def mask_cpf(cpf: str, exc: str = None, must_fill: bool = True) -> str:
    cpf = handling_cpf(cpf, exc, must_fill)
    return '***' + cpf[3:9] + '**'

def normalize_name(name: str) -> str:
    name_tk = [remove_punctuation(w) 
               for w in word_tokenize(remove_accents(name).lower()) 
               if w not in STOPWORDS_PT]
    return ' '.join(name_tk)

def now():
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

def now_time():
    return time.time()

def properties_to_dict(input_path: str) -> dict:
    try:
        return {strip_val(line.split('=', 1)[0]) : strip_val(line.split('=', 1)[1])
                for line in open(input_path, 'r')
                if (("=" in line) and  (not line.startswith("#")))}
    except FileNotFoundError:
        return {}

def read_csv(file_input, sep = ';', quotechar = '"', encoding = 'utf-8-sig',
             dtype = 'str', usecols = None, na_filter = False):
    df = None
    if file_exists(file_input):
        df = pd.read_csv(file_input,
                         sep = sep,
                         quotechar = quotechar,
                         encoding = encoding,
                         dtype = dtype,
                         usecols = usecols,
                         na_filter = na_filter)
    return df_trim_all_columns(df)
        
def read_excel(file_input, sheet_name = 0, usecols = None, dtype = None, 
               skiprows = None, na_values = None, parse_dates = False, 
               date_parser = None, thousands = None, skipfooter = 0):
    df = None
    if file_exists(file_input):
        df = pd.read_excel(file_input,
                           sheet_name = sheet_name,
                           usecols = usecols,
                           dtype = dtype,
                           skiprows = skiprows, 
                           na_values = na_values, 
                           parse_dates = parse_dates,
                           date_parser = date_parser,
                           thousands = thousands,
                           skipfooter = skipfooter)
    return df_trim_all_columns(df)
        
def remove_accents(txt: str, codif: str = 'utf-8') -> str:
    return normalize('NFKD', txt).encode('ASCII','ignore').decode(codif)

def remove_file(file_path: str):
    if ((not is_blank(file_path)) and file_exists(file_path)):
        os.remove(file_path)

STOPWORDS_PT = {remove_accents(stopword).lower()
                for stopword in stopwords.words('portuguese')}
    
def remove_punctuation(s, exc = None):
    remove_str = ''
    for c in ' ' + string.punctuation:
        if ((exc is None) or (c not in exc)):
            remove_str += c
    s = str(s)
    return s.translate({ord(i): '' for i in remove_str})

def str_to_bool(val) -> bool:
    try:
        return bool(strtobool(strip_val(val)))
    except ValueError:
        return False
    
def strip_val(val):
    return str(val).strip() if np.isscalar(val) and (not is_null(val)) else ''

def to_timestamp(dt, errors = 'coerce'):
    ts = pd.to_datetime(dt, errors = errors)
    return ts if (ts == dt) else pd.NaT

def to_csv(df, file_output, sep = ';', header = True, mode = 'a', 
           encoding = 'utf-8-sig', index = False,  quoting = csv.QUOTE_ALL):
    df = drop_duplicates_reindex(df)
    df.to_csv(file_output,
              sep = sep,
              header = header,
              mode = mode,
              encoding = encoding,
              index = index,
              quoting = quoting)
    log(f"{file_output} : {df.shape[0]} registros distintos")
    
