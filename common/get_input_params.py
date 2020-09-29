# -*- encoding: utf-8 -*-
"""Modulo common.get_input_params

Contém a classe responsável por ler os valores dos parâmetros de entrada da linha de comando.

Autor: Rogers Reiche de Mendonça <rogers.rj@gmail.com>
Data: Setembro/2020
"""
import getopt

from typing import Dict, NoReturn

from . import util
from .input_param import InputParamDef

InputParamDefDictType = Dict[str, InputParamDef]

class GetInputParams:
    def __init__(self, spec_name: str, input_param_def_dict: InputParamDefDictType, argv: list):
        """Construtor da classe GetInputParams.
        
        :param spec_name str: Spec module name (__spec__.name)
        :param input_param_def_dict InputParamDefDictType: Dicionário de definição dos parâmetros a ser lidos da linha de comando.
        :param argv list: Arguments list (sys.argv)            
        """
        if (not isinstance(argv, list)):
            raise ValueError(f"argv (type = {type(argv)}) must be a list object.")
        elif (not isinstance(input_param_def_dict, dict)):
            raise ValueError(f"input_param_def_dict (type = {type(input_param_def_dict)}) must be a dict object.")
        else:
            self.spec_name = util.strip_val(spec_name).replace(".__main__", "")
            self.input_param_def_dict = input_param_def_dict
            self.script_file = util.strip_val(argv[0])
            self.args = [util.strip_val(v) for v in argv[1:]]
            
    def _get_longopts(self) -> list:
        longopts = [k + '=' for k in self.input_param_def_dict]
        longopts.append('help')
        return longopts
    
    def _read_input(self) -> dict:
        opts, args = getopt.getopt(self.args, '', self._get_longopts())
        return {p[2:]:v for p, v in opts}
    
    def _get_mandatory_params(self) -> list:
        return [k for k, v in self.input_param_def_dict.items() if not v.default]
    
    def _check_mandatory_params(self, input_params: dict) -> NoReturn:
        mandatory_params = self._get_mandatory_params()
        for param in self._get_mandatory_params():
            if param not in input_params:
                raise getopt.GetoptError('Parametros obrigatorios: ' + ', '.join(mandatory_params))
                
    def _complement_default_values(self, input_params: dict) -> dict:
        for k in self.input_param_def_dict:
            if not input_params.get(k):
                input_params[k] = self.input_param_def_dict[k].default
        return input_params
                
    def get(self) -> dict:
        """Obtém os valores dos parametros de entrada da linha de comando.
        """        
        try:
            input_params = self._read_input()
            
            self._check_mandatory_params(input_params)
            
            return self._complement_default_values(input_params)
        
        except getopt.GetoptError as e:
            self.help()
            raise e
            
    def help(self) -> NoReturn:
        """Imprime a ajuda da linha de comando de execução.
        """
        module_exec = f"python -m {self.spec_name}"
        
        param_usage = ''
        param_defs = ''
        param_example = ''
        for k, param in self.input_param_def_dict.items():
            param_usage += f"--{param.name}=<valor> "
            
            if (param.default):
                param_defs += f". {param.name} = {param.definition} (Default: {param.default})\r\n"
            else:
                param_defs += f". {param.name} = {param.definition}\r\n"
                                
            param_example += f"--{param.name}={param.example} "
            
        print(f"* Uso:\r\n{module_exec} {param_usage}\r\n")
        print(f"* Parametros:\r\n{param_defs}")
        print(f"* Exemplo:\r\n{module_exec} {param_example}\r\n")