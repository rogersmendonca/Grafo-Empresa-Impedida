# -*- encoding: utf-8 -*-
"""Módulo empresa_impedida

Módulo principal (execução por linha de comando).

Autor: Rogers Reiche de Mendonça <rogers.rj@gmail.com>
Data: Setembro/2020
"""
import sys

from common.input_param import InputParamDef
from common.get_input_params import GetInputParams
from common.logging import log
from common import util
from graph import GraphAnalysis

INPUT_CSV_EDGES = 'csv_edges'
OUTPUT_TXT_IMPEDIMENTOS = 'txt_impedimentos'

INPUT_PARAMS_DEF = {                                              
    INPUT_CSV_EDGES: InputParamDef(INPUT_CSV_EDGES,
                                   '[INPUT] Arquivo CSV das arestas do grafo',
                                   r'C:\input\graph_edges.csv',
                                   None),
                                    
    OUTPUT_TXT_IMPEDIMENTOS: InputParamDef(OUTPUT_TXT_IMPEDIMENTOS,
                                           '[OUTPUT] Arquivo TXT dos caminhos do grafo que denotam impedimentos',
                                           r'C:\output\impedimentos.txt',
                                           None)
}

def main(): 
    try:
        get_input_params = GetInputParams(f"{__spec__.name}",
                                          INPUT_PARAMS_DEF,
                                          sys.argv)
        input_params = get_input_params.get()
    except Exception as e:
        print(e)
        sys.exit(1)
        
    start = util.now_time()
    
    graph_analysis = GraphAnalysis(csv_edges = input_params[INPUT_CSV_EDGES],
                                   output_paths_txt = input_params[OUTPUT_TXT_IMPEDIMENTOS])
    
    graph_analysis.search_paths()
    
    end = util.now_time()
                
    delta = end - start
    mins, secs = divmod(delta, 60)
    hours, mins = divmod(mins, 60)
            
    log("Processamento concluido!")
    log(f"Tempo de execucao: {delta} " \
        f"({int(hours):02}:{int(mins):02}:{int(secs):02}" \
        f".{str(secs-int(secs)).split('.')[1]})")            
        
if __name__ == '__main__':
    main()