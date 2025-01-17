from typing import List
from os.path import join
from datetime import datetime, timedelta
from calendar import monthrange
import numpy as np
import pandas as pd
from apps.utils.log import Log
import os.path
from inewave.newave import Dger
from inewave.newave import Agrint
from inewave.newave import Cadic
from inewave.newave import Caso
from inewave.newave import Clast
from inewave.newave import Curva
from inewave.newave import Cvar
from inewave.newave import Dsvagua
from inewave.newave import Exph
from inewave.newave import Expt
from inewave.newave import Ghmin
import shutil
from io import StringIO

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
        print(self.caminhoDeckResultante)
        if not os.path.exists(self.caminhoDeckResultante):
            shutil.copytree(self.caminhoDeckBase, self.caminhoDeckResultante)
        else:
            #shutil.rmtree(self.caminho_teste_1)
            #shutil.copytree(self.caminho, self.caminho_teste_1)
            print("DIRETORIO DO DECK PROSPECTIVO JÁ EXISTE, UTILIZANDO O DIRETORIO EXISTENTE")
        
        with open(arquivo_txt, "r") as file:
                for line in file:
                    if("ANOINICIO" in line):
                        self.ano_inicio = line.split("=")[1]
                    if("VERSAO" in line):
                        self.versao = line.split("=")[1]
        dados_Dger_base = Dger.read(self.caminhoDeckBase+"/dger.dat")        
        self.timeTableInicioEstudoProspectivo =  pd.to_datetime(self.ano_inicio+"-"+str(dados_Dger_base.mes_inicio_estudo)+"-01")
        self.timeTableInicioEstudoBase =  pd.to_datetime(str(dados_Dger_base.ano_inicio_estudo)+"-"+str(dados_Dger_base.mes_inicio_estudo)+"-01")
        self.delta = self.timeTableInicioEstudoProspectivo - self.timeTableInicioEstudoBase
        print(self.delta)
        print(self.timeTableInicioEstudoProspectivo)
        print(self.timeTableInicioEstudoBase)
        self.transformaDger()
        #self.transformaAgrint()
        self.transformaCadic()
        self.transformaCasoDat()
        self.transformaClast()
        self.transformaCurva()
        self.transformaCVAR()
        #self.transformaDsvagua()
        self.transformaExph()
        self.transformaExpt()
        self.transformaGhmin()

    def transformaGhmin(self):
        dados = Expt.read(self.caminhoDeckBase+"/ghmin.dat")
        print(dados.geracoes)
        #dados.expansoes["data_inicio"] = dados.expansoes["data_inicio"] + self.delta
        #dados.expansoes["data_fim"] = dados.expansoes["data_fim"] + self.delta
        #conteudo = StringIO()
        #dados.write(conteudo)
        #with open(self.caminhoDeckResultante+"/"+"expt.dat", "w") as file:
        #    file.write(conteudo.getvalue())

    def transformaExpt(self):
        dados = Expt.read(self.caminhoDeckBase+"/expt.dat")
        dados.expansoes["data_inicio"] = dados.expansoes["data_inicio"] + self.delta
        dados.expansoes["data_fim"] = dados.expansoes["data_fim"] + self.delta
        conteudo = StringIO()
        dados.write(conteudo)
        with open(self.caminhoDeckResultante+"/"+"expt.dat", "w") as file:
            file.write(conteudo.getvalue())

    def transformaExph(self):
        dados = Exph.read(self.caminhoDeckBase+"/exph.dat")
        dados.expansoes["data_inicio_enchimento"] = dados.expansoes["data_inicio_enchimento"] + self.delta
        dados.expansoes["data_entrada_operacao"] = dados.expansoes["data_entrada_operacao"] + self.delta
        conteudo = StringIO()
        dados.write(conteudo)
        with open(self.caminhoDeckResultante+"/"+"exph.dat", "w") as file:
            file.write(conteudo.getvalue())

    #def transformaDsvagua(self):
    #    dados = Dsvagua.read(self.caminhoDeckBase+"/dsvagua.dat")
    #    print(dados.desvios)
    #    #dados.curva_seguranca["data"] = dados.curva_seguranca["data"] + self.delta+ timedelta(days=1)
    #    #conteudo = StringIO()
    #    #dados.write(conteudo)
    #    #with open(self.caminhoDeckResultante+"/"+"curva.dat", "w") as file:
    #    #    file.write(conteudo.getvalue())

    def transformaCVAR(self):
        dados = Cvar.read(self.caminhoDeckBase+"/cvar.dat")

        df_temp = dados.alfa_variavel.loc[(dados.alfa_variavel["data"] <  datetime(9990, 1, 1))]
        df_temp["data"] = df_temp["data"] + self.delta + timedelta(days=1)
        dados.alfa_variavel.loc[(dados.alfa_variavel["data"] <  datetime(9990, 1, 1))] = df_temp

        df_temp = dados.lambda_variavel.loc[(dados.lambda_variavel["data"] <  datetime(9990, 1, 1))]
        df_temp["data"] = df_temp["data"] + self.delta + timedelta(days=1)
        dados.lambda_variavel.loc[(dados.lambda_variavel["data"] <  datetime(9990, 1, 1))] = df_temp

        conteudo = StringIO()
        dados.write(conteudo)
        with open(self.caminhoDeckResultante+"/"+"cvar.dat", "w") as file:
            file.write(conteudo.getvalue())

    def transformaCurva(self):
        dados = Curva.read(self.caminhoDeckBase+"/curva.dat")
        dados.curva_seguranca["data"] = dados.curva_seguranca["data"] + self.delta+ timedelta(days=1)
        conteudo = StringIO()
        dados.write(conteudo)
        with open(self.caminhoDeckResultante+"/"+"curva.dat", "w") as file:
            file.write(conteudo.getvalue())

    def transformaClast(self):
        dados = Clast.read(self.caminhoDeckBase+"/clast.dat")
        dados.modificacoes["data_inicio"] = dados.modificacoes["data_inicio"] + self.delta
        dados.modificacoes["data_fim"] = dados.modificacoes["data_fim"] + self.delta
        conteudo = StringIO()
        dados.write(conteudo)
        with open(self.caminhoDeckResultante+"/"+"clast.dat", "w") as file:
            file.write(conteudo.getvalue())

    def transformaCasoDat(self):
        dados = Caso.read(self.caminhoDeckBase+"/caso.dat")
        dados.gerenciador_processos = "/home/pem/versoes/NEWAVE/v"+self.versao
        conteudo = StringIO()
        dados.write(conteudo)
        with open(self.caminhoDeckResultante+"/"+"caso.dat", "w") as file:
            file.write(conteudo.getvalue())

    def transformaCadic(self):
        dados = Cadic.read(self.caminhoDeckBase+"/c_adic.dat")
        df_temp = dados.cargas.loc[(dados.cargas["data"] <  datetime(9990, 1, 1))]
        df_temp["data"] = df_temp["data"] + self.delta + timedelta(days=1)
        dados.cargas.loc[(dados.cargas["data"] <  datetime(9990, 1, 1))] = df_temp
        conteudo = StringIO()
        dados.write(conteudo)
        with open(self.caminhoDeckResultante+"/"+"c_adic.dat", "w") as file:
            file.write(conteudo.getvalue())


    def transformaAgrint(self):
        dados = Agrint.read(self.caminhoDeckBase+"/agrint.dat")
        print(dados.limites_agrupamentos)


        #conteudo_dger = StringIO()
        #dados_Dger.write(conteudo_dger)
        #with open(self.caminhoDeckResultante+"/"+"dger.dat", "w") as file:
        #    file.write(conteudo_dger.getvalue())
        ##dados_Dger.ano_inicio_estudo


    def transformaDger(self):
        dados_Dger = Dger.read(self.caminhoDeckBase+"/dger.dat")

        #Altera ano de início do estudo
        dados_Dger.ano_inicio_estudo = self.ano_inicio
        dados_Dger.ano_inicio_estudo

        #Altera gerenciador de PLs
        dados_Dger.utiliza_gerenciamento_pls = 1
        dados_Dger.utiliza_gerenciamento_pls
        dados_Dger.comunicacao_dois_niveis = 1
        dados_Dger.comunicacao_dois_niveis
        dados_Dger.armazenamento_local_arquivos_temporarios = 1
        dados_Dger.armazenamento_local_arquivos_temporarios
        dados_Dger.alocacao_memoria_ena = 0
        dados_Dger.alocacao_memoria_ena
        dados_Dger.alocacao_memoria_cortes = 0
        dados_Dger.alocacao_memoria_cortes


        conteudo_dger = StringIO()
        dados_Dger.write(conteudo_dger)
        with open(self.caminhoDeckResultante+"/"+"dger.dat", "w") as file:
            file.write(conteudo_dger.getvalue())
        #dados_Dger.ano_inicio_estudo
