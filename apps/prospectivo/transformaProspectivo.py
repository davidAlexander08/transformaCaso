from typing import List
from os.path import join
from datetime import datetime
from calendar import monthrange
import numpy as np
import pandas as pd
from apps.utils.log import Log
import os.path
from inewave.newave import Dger

class TransformaProspectivo:
    """
    Calcula os indicadores que são utilizados nas visualizações e comparações
    """
    DIR_SINTESE = "sintese"

    def __init__(self, caminhoDeckBase, arquivo_txt):
        self.caminhoDeckBase = caminhoDeckBase
        self.instrucoes = arquivo_txt
        print(self.caminhoDeckBase)
        with open(arquivo_txt, "r") as file:
                for line in file:
                    if("ANOINICIO" in line):
                        self.ano_inicio = line.split("=")[1]

        self.transformaDger()

        
    def transformaDger(self):


        print(self.ano_inicio)

