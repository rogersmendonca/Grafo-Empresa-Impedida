# -*- encoding: utf-8 -*-
"""Módulo classes.counter

Contador para ser utilizado em multiprocessamento.

Autor: Rogers Reiche de Mendonça <rogers.rj@gmail.com>
Data: Setembro/2020
"""
import multiprocessing

class Counter(object):
    def __init__(self, initval = 0):
        self.val = multiprocessing.RawValue('i', initval)
        self.lock = multiprocessing.Lock()
    
    def increment(self):
        with self.lock:
            self.val.value += 1
            return self.value()
            
    def set_max(self, val):
        with self.lock:
            if (self.val.value < val):
                self.val.value = val
    
    def value(self):
        return self.val.value