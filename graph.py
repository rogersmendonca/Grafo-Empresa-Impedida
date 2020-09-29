# -*- encoding: utf-8 -*-
"""Módulo graph

Módulo de Análise de Grafos. 
Utiliza multiprocessamento para a realizar a pesquisa dos caminhos do grafo que denotam os impedimentos.

Autor: Rogers Reiche de Mendonça <rogers.rj@gmail.com>
Data: Setembro/2020
"""
import csv
from multiprocessing import Pool
import os

import igraph as ig
import pandas as pd

from common.logging import log
from common import util
from classes.counter import Counter

# Funcao utilizada no inicializador do Pool de processos
def init_globals(graph: ig.Graph,
                 total_licit_contrato: int,
                 iter_counter: Counter,
                 path_counter: Counter,
                 txt_output_paths: str):
    global pool_graph
    global pool_total_licit_contrato
    global pool_iter_counter
    global pool_path_counter
    global pool_txt_output_paths
    
    pool_graph = graph
    pool_total_licit_contrato = total_licit_contrato
    pool_iter_counter = iter_counter
    pool_path_counter = path_counter
    pool_txt_output_paths = txt_output_paths

def is_vertex_licit_contrato(vs: ig.Vertex) -> bool:
    return vs[util.V_PROP_TIPO] in [util.V_CONTRATO, util.V_LICITACAO]

def is_vertex_sancao(vs: ig.Vertex) -> bool:
    return vs[util.V_PROP_TIPO] == util.V_SANCAO

def is_contratacao_impedida(v_licit_contrato: ig.Vertex, v_sancao: ig.Vertex) -> bool:    
    licit_contrato_ini = v_licit_contrato[util.V_PROP_DATA_INI]
    licit_contrato_fim = v_licit_contrato[util.V_PROP_DATA_FIM]
    sancao_ini = v_sancao[util.V_PROP_DATA_INI]
    sancao_fim = v_sancao[util.V_PROP_DATA_FIM]    
    is_imped = ((licit_contrato_ini <= sancao_fim) and
                (licit_contrato_fim >= sancao_ini)) \
                if ((not util.is_null(licit_contrato_ini)) and 
                    (not util.is_null(licit_contrato_fim)) and 
                    (not util.is_null(sancao_ini)) and 
                    (not util.is_null(sancao_fim))) \
                else False
                   
    return is_imped

# Verifica se o caminho "v[i]"-"v[j]" e' um dos seguintes tipos:
# 1. [C]-[F]-[Sa] (tamanho = 2)
# 2. [C]-[F]-[E] (tamanho = 2)    
# 3. [C]-[F]-[S]-[E] (tamanho = 3)
# 4. [C]-[F]-[S]-[F]-[Sa] (tamanho = 4)
def is_path_contratacao_impedida(shortest_paths: list, i: int, j: int) -> bool:

    if (2 <= shortest_paths[0][j] <= 4):
        vpath_imped_n = pool_graph.get_shortest_paths(i, j, output = 'vpath')[0]
        vpath_imped_tipo = [pool_graph.vs[n][util.V_PROP_TIPO] for n in vpath_imped_n]
        
        count_contrato = vpath_imped_tipo.count(util.V_CONTRATO)
        count_licitacao = vpath_imped_tipo.count(util.V_LICITACAO)
        count_fornec = vpath_imped_tipo.count(util.V_FORNECEDOR)
        count_socio = vpath_imped_tipo.count(util.V_SOCIO)
        count_empregado = vpath_imped_tipo.count(util.V_EMPREGADO)        
        count_sancao = vpath_imped_tipo.count(util.V_SANCAO)
        
        if (((count_contrato + count_licitacao) == 1) and
            (count_fornec in [1, 2]) and
            (count_socio in [0, 1]) and
            ((count_empregado + count_sancao) == 1)):
            
            if (count_empregado == 1):
                return True
            else:
                vpath_imped = [pool_graph.vs[n] for n in vpath_imped_n]                
                for vs in vpath_imped:
                    if is_vertex_licit_contrato(vs):
                        v_licit_contrato = vs
                    elif is_vertex_sancao(vs):
                        v_sancao = vs
                return is_contratacao_impedida(v_licit_contrato, v_sancao)
        else:
            return False
    
def epath_log_msg(epath: list) -> str:
    epath_labels = []
    for i in epath:
        v_source_name = pool_graph.es[i][util.E_SOURCE]
        v_target_name = pool_graph.es[i][util.E_TARGET]
            
        epath_labels.append(f"{v_source_name}={v_target_name}")
        
    return ';'.join(epath_labels)    
    
def verify_path(i: int):
    iter_counter = pool_iter_counter.increment()
    v1 = pool_graph.vs[i]
    
    # graph.shortest_paths = Calcula o tamanho do caminho minimo 
    # entre um vertice e os demais vertices do grafo
    shortest_paths = pool_graph.shortest_paths(source = v1.index)
    
    # Verifica se os caminhos que denotam impedimentos
    for j in range(i, len(shortest_paths[0])):
        if is_path_contratacao_impedida(shortest_paths, i, j):
            path_counter = pool_path_counter.increment()
            epath_imped = pool_graph.get_shortest_paths(i, j, output = 'epath')[0]
            log(f"{os.getpid()}: {iter_counter}/{pool_total_licit_contrato} " \
                f"({round(iter_counter/pool_total_licit_contrato*100, 2)}%) | "\
                f" {path_counter}. {epath_imped}")
            log(epath_log_msg(epath_imped), log_file = pool_txt_output_paths)

class GraphAnalysis:
    def __init__(self,
                 csv_edges: str,
                 output_paths_txt: str):
        """Construtor da classe GraphAnalysis.

        :param csv_edges str: Caminho do arquivo CSV das arestas do grafo.
        :param output_paths_txt str: Caminho do arquivo TXT para output dos caminhos do grafo que denotam impedimentos.
        """
        self.csv_edges = csv_edges
        self.output_paths_txt = output_paths_txt
                
        self._graph = None
        
    def get_graph(self) -> ig.Graph:
        """Cria e retorna o grafo.
        """
        log("Criando o grafo...")
        if (not util.file_exists(self.csv_edges)):
            log(f"Arquivo {self.csv_edges} inexistente")
        else:
            if (util.is_null(self._graph)):            
                with open(self.csv_edges, mode = 'r', encoding = 'utf-8-sig') as csv_edges:
                    dict_edges = csv.DictReader(csv_edges, delimiter = ';')
                    self._graph = ig.Graph.DictList(vertices = None, 
                                                    edges = dict_edges, 
                                                    directed = False)
                    
                # Novas propriedades dos vertices
                for vs in self._graph.vs:
                    props = vs['name'].split('-')
                    vs[util.V_PROP_TIPO] = props[0]
                    vs[util.V_PROP_SUBTIPO] = props[1]
                    vs[util.V_PROP_ID] = props[2]
                    vs[util.V_PROP_DATA_INI] = util.yyyymmdd_to_Timestamp(props[3], pd.Timestamp.min) \
                                                   if (len(props) > 3) else None
                    vs[util.V_PROP_DATA_FIM] = util.yyyymmdd_to_Timestamp(props[4], pd.Timestamp.max) \
                                                   if (len(props) > 4) else None
                                
            log(f"Grafo criado ({len(self._graph.vs)} vertices, {len(self._graph.es)} arestas)")
            
        return self._graph

    def search_paths(self):
        """Pesquisa os caminhos do grafo que denotam impedimentos.
        """        
        graph = self.get_graph()
                
        gindex_licit_contrato = [vs.index for vs in graph.vs if is_vertex_licit_contrato(vs)]
        
        total_licit_contrato = len(gindex_licit_contrato)
        iter_counter = Counter(0) 
        path_counter = Counter(0)
                        
        util.remove_file(self.output_paths_txt)
        with Pool(initializer = init_globals, initargs = (graph,
                                                          total_licit_contrato,
                                                          iter_counter,
                                                          path_counter,
                                                          self.output_paths_txt)) as pool:
            pool.map(verify_path, gindex_licit_contrato)
                
        log(f"TOTAL = {path_counter.value()} caminhos", log_file = self.output_paths_txt)