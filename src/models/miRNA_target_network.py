import pandas as pd
import numpy as np
import networkx as nx
from networkx.algorithms import bipartite


class miRNATargetNetwork:
    def __init__(self, threshold=0.6):
        self.threshold = threshold
        self.B = nx.Graph()

    def add_miRNA_nodes(self, miRNAs):
        self.B.add_nodes_from(miRNAs, bipartite=0)

    def add_target_nodes(self, targets):
        self.B.add_nodes_from(targets, bipartite=1)

    def train(self, miRNAs_A, targets_A, miRNAs_B, targets_B):
        """
        Constructing the MTDN from xu2011prioritizing

        :param miRNAs_A: Pandas dataframe for tumor samples
        :param targets_A: Pandas dataframe for tumor samples
        :param miRNAs_B: Pandas dataframe for normal  samples
        :param targets_B: Pandas dataframe for normal samples
        """
        miRNAs = miRNAs_A.columns
        targets = targets_B.columns
        self.add_miRNA_nodes(miRNAs)
        self.add_target_nodes(targets)

        n_A = miRNAs_A.shape[0]
        n_B = miRNAs_B.shape[0]
        print 'n_A', n_A
        print 'n_B', n_B

        for m in miRNAs:
            edge_count = 1
            miRNA_A_m = miRNAs_A[m] - np.mean(miRNAs_A[m])
            miRNA_B_m = miRNAs_B[m] - np.mean(miRNAs_B[m])
            miRNA_A_m_std = np.std(miRNAs_A[m])
            miRNA_B_m_std = np.std(miRNAs_B[m])
            for t in targets:
                miRNA_target_A_corr = np.dot(miRNA_A_m, targets_A[t] - np.mean(targets_A[t])) / \
                                      ((n_A - 1) * miRNA_A_m_std * np.std(targets_A[t]))

                miRNA_target_B_corr = np.dot(miRNA_B_m, targets_B[t] - np.mean(targets_B[t])) / \
                                      ((n_B - 1) * miRNA_B_m_std * np.std(targets_B[t]))

                dys = miRNA_target_A_corr - miRNA_target_B_corr
                # print m, '<->', t, ':', dys
                try:
                    if np.abs(dys) >= self.threshold:
                        self.add_edge(m, t, dys=dys)
                        edge_count += 1
                except ValueError:
                    pass

            print m, ':', edge_count

    def add_edge(self, miRNA, target, dys):
        self.B.add_edge(miRNA, target, dys=dys)
