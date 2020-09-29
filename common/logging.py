# -*- encoding: utf-8 -*-
"""Módulo common.logging

Contém a classe de log.

Autor: Rogers Reiche de Mendonça <rogers.rj@gmail.com>
Data: Setembro/2020
"""
from . import util

def log(message: str, end: str = '\n', log_file: str = None):
    log_message = f"[{util.now()}] {message}"
    print(log_message, end)  
    
    if (log_file):
        with open(log_file, 'a') as f:
            f.write(log_message + end)