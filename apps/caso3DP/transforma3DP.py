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
from inewave.newave import Manutt
from inewave.newave import Confhd
from inewave.newave import Modif
from inewave.newave import Patamar
from inewave.newave import Ree
from inewave.newave import Sistema
from inewave.newave import Vazpast
from inewave.libs import Restricoes
import shutil
from io import StringIO

class Transforma3DP:
    """
    Calcula os indicadores que são utilizados nas visualizações e comparações
    """
    DIR_SINTESE = "sintese"

    def __init__(self, caminhoDeckBase):
        print(caminhoDeckBase)
        self.caminhoDeckBase = caminhoDeckBase
        self.caminhoAntesDoCasoBase = "/".join(self.caminhoDeckBase.split("/")[:-1])
        self.caminhoDeckResultante = self.caminhoAntesDoCasoBase+"/deck_3DP"
        print(self.caminhoDeckResultante)
        if not os.path.exists(self.caminhoDeckResultante):
            shutil.copytree(self.caminhoDeckBase, self.caminhoDeckResultante)
        else:
            #shutil.rmtree(self.caminho_teste_1)
            #shutil.copytree(self.caminho, self.caminho_teste_1)
            print("DIRETORIO DO DECK PROSPECTIVO JÁ EXISTE, UTILIZANDO O DIRETORIO EXISTENTE")
        #self.dados_Dger_base = Dger.read(self.caminhoDeckBase+"/dger.dat")    
        #print(self.dados_Dger_base.mes_inicio_estudo)    
        #print(self.dados_Dger_base.ano_inicio_estudo)    
        #self.timeTableInicioEstudoBase =  pd.to_datetime(str(self.dados_Dger_base.ano_inicio_estudo)+"-"+str(self.dados_Dger_base.mes_inicio_estudo)+"-01")

        self.usinasRemanescentes = [
            6,
   8,
  11,
  12,
  17,
  18,
  34,
  66,
 156,
 227,
 229,
 251,
 257,
 261,
 285,
 287,
 279,
  24,
  25,
  31,
  32,
  33,
  37,
  40,
  42,
  43,
  45,
  46,
  47,
  49,
  50,
  61,
  62,
  63,
  74,
  86,
  91,
  92,
  93,
 103,
 115,
  76,
  77,
  82,
 169,
 172,
 178,
 295,
 267,
 275,
 291,
 292,
 302,
 303,
 306,
 314,
 288]
        self.retiraUsinas()



    def retiraUsinas(self): 
        dados = Confhd.read(self.caminhoDeckBase+"/confhd.dat").usinas
        dados_dsvagua = Dsvagua.read(self.caminhoDeckBase+"/dsvagua.dat").desvios
        print(dados_dsvagua)

        print(dados)
        dados = dados.loc[(dados["codigo_usina"].isin(self.usinasRemanescentes))].reset_index(drop = True)
        dados_dsvagua = dados_dsvagua.loc[(dados_dsvagua["codigo_usina"].isin(self.usinasRemanescentes))].reset_index(drop = True)

        print(dados_dsvagua)

        print(dados)
        exit(1)
        dados.limites_intercambio["data"] = dados.limites_intercambio["data"] +self.delta + timedelta(days=1)
        df_temp = dados.mercado_energia.loc[(dados.mercado_energia["data"] <  datetime(9990, 1, 1))]
        df_temp["data"] = df_temp["data"] + self.delta  + timedelta(days=1)
        dados.mercado_energia.loc[(dados.mercado_energia["data"] <  datetime(9990, 1, 1))] = df_temp
        dados.geracao_usinas_nao_simuladas["data"] = dados.geracao_usinas_nao_simuladas["data"] +self.delta + timedelta(days=1)
        conteudo = StringIO()
        dados.write(conteudo)
        with open(self.caminhoDeckResultante+"/"+"sistema.dat", "w") as file:
            file.write(conteudo.getvalue())


    #def transformaRestricoes(self):
    #    dados = Restricoes.read(self.caminhoDeckBase+"/restricao-eletrica.csv")
    #    print(dados.re_horiz_per(df = True))
    #    print(dados.re_lim_form_per(df = True))
    #    dados.re_horiz_per(df = True)["data_inicio"] = dados.re_horiz_per(df = True)["data_inicio"] + self.delta
    #    dados.re_lim_form_per(df = True)["data_inicio"] = dados.re_lim_form_per(df = True)["data_inicio"] + self.delta
    #    dados.re_horiz_per(df = True)["data_fim"] = dados.re_horiz_per(df = True)["data_fim"] + self.delta
    #    dados.re_lim_form_per(df = True)["data_fim"] = dados.re_lim_form_per(df = True)["data_fim"] + self.delta
    #    print(dados.re_horiz_per(df = True))
    #    print(dados.re_lim_form_per(df = True))
        
        

        #dados.rees["ano_fim_individualizado"] = dados.rees["ano_fim_individualizado"] + self.delta.days / 365
        #conteudo = StringIO()
        #dados.write(conteudo)
        #with open(self.caminhoDeckResultante+"/"+"ree.dat", "w") as file:
        #    file.write(conteudo.getvalue())

    def transformaRee(self): 
        dados = Ree.read(self.caminhoDeckBase+"/ree.dat")
        dados.rees["ano_fim_individualizado"] = dados.rees["ano_fim_individualizado"] + self.delta.days / 365
        conteudo = StringIO()
        dados.write(conteudo)
        with open(self.caminhoDeckResultante+"/"+"ree.dat", "w") as file:
            file.write(conteudo.getvalue())

    def transformaPatamar(self): 
        dados = Patamar.read(self.caminhoDeckBase+"/patamar.dat")
        dados.duracao_mensal_patamares["data"]   = dados.duracao_mensal_patamares["data"]  +self.delta
        dados.carga_patamares["data"] = dados.carga_patamares["data"] + self.delta
        dados.intercambio_patamares["data"] = dados.intercambio_patamares["data"] + self.delta
        dados.usinas_nao_simuladas["data"] = dados.usinas_nao_simuladas["data"] + self.delta
        conteudo = StringIO()
        dados.write(conteudo)
        with open(self.caminhoDeckResultante+"/"+"patamar.dat", "w") as file:
            file.write(conteudo.getvalue())

    def transformaManutt(self): 
        dados = Manutt.read(self.caminhoDeckBase+"/manutt.dat")
        dados.manutencoes["data_inicio"] = dados.manutencoes["data_inicio"] + self.delta
        conteudo = StringIO()
        dados.write(conteudo)
        with open(self.caminhoDeckResultante+"/"+"manutt.dat", "w") as file:
            file.write(conteudo.getvalue())

    
    def transformaGhmin(self): ## ESTA FALTANDO O POS, NA INEWAVE QUANDO COLOCA O POS ESTÁ VAZIO, VER ISSO COM ROGERINHO
        dados = Ghmin.read(self.caminhoDeckBase+"/ghmin.dat")
        dados.geracoes["data"] = dados.geracoes["data"] + self.delta
        conteudo = StringIO()
        dados.write(conteudo)
        with open(self.caminhoDeckResultante+"/"+"ghmin.dat", "w") as file:
            file.write(conteudo.getvalue())

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
