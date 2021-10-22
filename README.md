# Grafo-Empresa-Impedida
Programa em Python que utiliza Grafos para identificar empresas impedidas de ser contratadas por empresa pública ou sociedade de economia mista, de acordo com o artigo 38 da [Lei 13.303/2016  (Lei das Estatais)](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/lei/l13303.htm).

Trabalho apresentado no 6º Seminário Internacional sobre Análise de Dados na Administração Pública, em 29/09/2020 ([Link do YouTube](https://youtu.be/aCRY8ZQDGS4)).

## Linha de Comando
`python -m empresa_impedida --csv_edges=<valor> --txt_impedimentos=<valor>`

### Parâmetros

#### csv_edges
[INPUT] Caminho do arquivo CSV das arestas do grafo (mais informações sobre o conteúdo do arquivo abaixo).

#### txt_impedimentos
[OUTPUT] Caminho do arquivo TXT dos caminhos do grafo que identificam impedimentos.

### Exemplo
python -m empresa_impedida --csv_edges=C:\input\graph_edges.csv --txt_impedimentos=C:\output\impedimentos.txt

## Bibliotecas Python requeridas:
* IGraph
* Pandas

## Arquivo CSV das arestas do grafo (informado no parâmetro **csv_edges**)

### Arquivo CSV com 3 colunas
* **source** = Nome do vértice de origem
* **target** = Nome do vértice de destino
* **tipo** = Rótulo do tipo do relacionamento

### Padrão para o nome do vértice
O nome do vértice segue o padrão `<1>-<2>-<3>-<4>-<5>`, onde:

* **<1>** = Rótulo do tipo do objeto representado no vértice. Domínio: **E** (Empregado); **L** (Licitação); **C** (Contrato); **F** (Fornecedor); **S** (Sócio); **Sa** (Sanção)

* **<2>** = Subtipo do objeto representado no vértice.
<br />`Subtipo do Tipo E` **Domínio: Livre.** Por exemplo, pode ser o nível hierárquico ou a área do empregado.
<br />`Subtipo do Tipo L` **Domínio: Livre.** Por exemplo, pode ser a classificação da oportunidade como Bens ou Serviços.
<br />`Subtipo do Tipo C` **Domínio: Livre.** Por exemplo, a classificação do contrato como Bens ou Serviços.
<br />`Subtipo do Tipo F` **Domínio:** **J** (Pessoa Jurídica), **F** (Pessoa Física) ou **E** (Estrangeiro)
<br />`Subtipo do Tipo S` **Domínio:** **1** (Pessoa Jurídica), **2** (Pessoa Física) ou **3** (Estrangeiro)
<br />`Subtipo do Tipo Sa` **Domínio:** **CEIS**, **CNEP**, **CEPIM**, ...

* **<3>** = Identificador do objeto.

* **<4>** = Data de início. Utilizado para L (Licitação), C (Contrato) e Sa (Sanção), opcional para os outros tipos.

* **<5>** = Data de término. Utilizado para L (Licitação), C (Contrato) e Sa (Sanção), opcional para os outros tipos.

### Tipos de relacionamentos:
<table>
  <tr>
  <th>Origem (Vértice)</th>
  <th>Destino (Vértice)</th>
  <th>Relacionamento (Aresta)</th>
  </tr>
  <tr>
  <td>Licitação</td>
  <td>Fornecedor</td>
  <td>Participação</td>
  </tr>

  <tr>
  <td>Contrato</td>
  <td>Fornecedor</td>
  <td>Fornecimento</td>
  </tr>  

  <tr>
  <td>Fornecedor</td>
  <td>Empregado</td>
  <td>Igualdade</td>
  </tr>  
  
  <tr>
  <td>Fornecedor</td>
  <td>Sócio</td>
  <td>Responsabilidade</td>
  </tr>
  
  <tr>
  <td>Fornecedor</td>
  <td>Sanção</td>
  <td>Penalidade</td>
  </tr>
  
<tr>
  <td>Sócio</td>
  <td>Empregado</td>
  <td>Igualdade</td>
  </tr>  
  </table>

**Observação:** O arquivo [graph_edges.csv](input/graph_edges.csv) é uma **amostra do CSV** das arestas do grafo, a partir de dados simulados.
