from typing import List
from os.path import join
from datetime import datetime
from calendar import monthrange
import numpy as np
import pandas as pd
from apps.utils.log import Log
import os.path
from inewave.newave import Dger
import shutil
class TransformaProspectivo:
    """
    Calcula os indicadores que são utilizados nas visualizações e comparações
    """
    DIR_SINTESE = "sintese"

    def __init__(self, caminhoDeckBase, arquivo_txt):
        self.caminhoDeckBase = caminhoDeckBase
        self.instrucoes = arquivo_txt

        self.caminhoAntesDoCasoBase = "/".join(self.caminhoDeckBase.split("/")[:-1])
        self.caminhoDeckResultante = self.caminhoAntesDoCasoBase+"/deck_teste_prospectivo"

        if not os.path.exists(self.caminhoDeckResultante):
            shutil.copytree(self.caminhoDeckBase, self.caminhoDeckResultante)
        else:
            #shutil.rmtree(self.caminho_teste_1)
            #shutil.copytree(self.caminho, self.caminho_teste_1)
            print("DIRETORIO DO DECK PROSPECTIVO JÁ EXISTE, UTILIZANDO O DIRETORIO EXISTENTE")
        print(self.caminhoDeckBase)
        with open(arquivo_txt, "r") as file:
                for line in file:
                    if("ANOINICIO" in line):
                        self.ano_inicio = line.split("=")[1]

        self.transformaDger()


    def transformaDger(self):
        dados_Dger = Dger.read(self.caminhoDeckResultante+"/dger.dat")


        print(dados_Dger.ano_inicio_estudo)
        dados_Dger.ano_inicio_estudo = self.ano_inicio
        dados_Dger.ano_inicio_estudo
        print(dados_Dger.ano_inicio_estudo)

