# -*- encoding: utf-8 -*-
"""Módulo common.input_params

Contém a classe de definição de um parâmetro de entrada da linha de comando.

Autor: Rogers Reiche de Mendonça <rogers.rj@gmail.com>
Data: Setembro/2020
"""
from . import util

class InputParamDef:    
    def __init__(self, name: str, definition: str, example: str, default: str = None):
        """Construtor da classe GetInputParams.
        
        :param name str: Nome do parâmetro.
        :param definition str: Definição do parâmetro.
        :param example str: Exemplo de valor do parâmetro.
        :param default str: Valor default do parâmetro.
        """        
        self.name = util.strip_val(name)
        self.definition = util.strip_val(definition)
        self.example = util.strip_val(example)
        self.default = util.strip_val(default)