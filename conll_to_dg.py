import sys
import logging
from re import *

from networkx import DiGraph, is_directed_acyclic_graph

logger = logging.Logger('catch_all')

remultword = compile('\d+.\d+')

def read_graph_from_lines(graph_lines: list) -> DiGraph:
    di_graph = DiGraph()
    di_graph.add_node(0)
    for line in graph_lines:
        di_graph.add_node(
            int(line.split('\t')[0]),
            token=line.split('\t')[1],
            lemma=line.split('\t')[2].strip(),
            upos=line.split('\t')[3],
            xpos=line.split('\t')[4],
            ufeats=line.split('\t')[5],
            misc=line.split('\t')[9])
        di_graph.add_edge(
            int(line.split('\t')[6]),
            int(line.split('\t')[0]),
            ud_label=line.split('\t')[7])
    return di_graph


def read_graph(conllu, howManyGraphs):
    digraphs = {}
    try:
        graph_lines = []
        i = 0
        for line in conllu.readlines():
            if line.strip():
                if line.startswith('#'):
                    pass
                # multiwords will be ignored
                elif remultword.search(line.split()[0]):
                    pass
                else:
                    graph_lines.append(line.strip())
            else:
                di_graph = read_graph_from_lines(graph_lines)
                # di_graph mozna segmentowac
                digraphs[i] = di_graph
                i = i + 1
            if i == howManyGraphs:
                break
    except Exception as e:
        logger.error(e, exc_info=True)
        return []
    for j in range(len(digraphs)):
        print(digraphs[j].nodes(data=True))
    return digraphs

    

if __name__ == '__main__':
    try:
        conllu = open('C:\\Users\\Adam\\magisterka\\data\\ENG\\eng.erst.gum_dev.conllu', 'r', encoding="utf8")
    except IOError:
        print("The input conllu file not found")
        sys.exit(1)
    except IndexError:
        print("python", sys.argv[0], "inputfile outputfile")
        sys.exit(1)
    read_graph(conllu, 2)
