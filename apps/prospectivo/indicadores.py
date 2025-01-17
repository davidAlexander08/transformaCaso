from typing import List
from os.path import join
from datetime import datetime
from calendar import monthrange
import numpy as np
import pandas as pd
from inewave.newave import Dger
from apps.utils.log import Log
import os.path
from apps.avalia_fpha.caso import CasoAvalicao
from apps.avalia_fpha.usina import UsinaAvalicao
from inewave.newave import AvlCortesFpha
from inewave.newave import Hidr
from inewave.newave import Confhd
from inewave.newave import Patamar
from inewave.nwlistop import GhmaxFpha
from inewave.libs import UsinasHidreletricas
from apps.avalia_fpha.indicadores import IndicadoresAvaliacaoFPHA

class IndicadoresAvaliacaoHJUS:
    """
    Calcula os indicadores que são utilizados nas visualizações e comparações
    """
    DIR_SINTESE = "sintese"

    def __init__(
        self, 
        casos: List[CasoAvalicao],
        usinas: List[UsinaAvalicao]
    ):
        self.indicadores_FPHA = IndicadoresAvaliacaoFPHA(casos,usinas)
        
        self.casos = casos
        self.usinas = usinas
        self.__eco_avl_fpha = None
        self.__eco_patamares = None

        self.__eco_qtur_est = None
        self.__eco_qtur_pat = None
        self.__eco_qver_est = None
        self.__eco_qver_pat = None
        self.__eco_ghmax_newave = None
        self.__ghmax_calculado = None
        self.__ghmax_memoria_calculo = None
        self.__compara_ghmax_newave_ghmax_calculado = None
        #pd.set_option('display.max_columns', None)
        self.__calc_vazao_jusante = None
        self.__eco_poljus_HIDR = None
        self.__eco_polmon = None
        self.__df_hidr_com_jusante = None
        self.__eco_varmf_jusante = None
        self.__eco_varmi_jusante = None
        self.__hmon_calculado = None
        self.__hmon_memoria_calculo = None
        self.__hmon_NW = None
        self.__compara_hmon_newave_hmon_calculado = None
        self.__eco_curvajusante = None
        self.__eco_curvajusante_polinomio = None
        self.__eco_curvajusante_polinomio_segmento = None
        self.__hjus_calculado = None
        self.__hjus_memoria_calculo = None
        self.__hjus_NW = None
        self.__compara_hjus_newave_hjus_calculado = None
        self.__hliq_calculado = None
        self.__hliq_memoria_calculo = None
        self.__hliq_NW = None
        self.__compara_hliq_newave_hliq_calculado = None



    @property
    def df_compara_hliq_newave_hliq_calculado(self) -> pd.DataFrame:
        if self.__compara_hliq_newave_hliq_calculado is None:
            self.__compara_hliq_newave_hliq_calculado = self.__gera_tabela_comparacao_hliq()
        return self.__compara_hliq_newave_hliq_calculado


    def __gera_tabela_comparacao_hliq(self) -> pd.DataFrame:
        lista_df = []
        df_comparacao = pd.DataFrame(columns=["caso", "usina", "periodo", "dataInicio","cenario", "patamar","Hliq_NW", "Hliq_calc", "Erro"   ])

        
        for index, row in self.df_hliq_calculado.iterrows():
            dataInicioPeriodo = row["dataInicio"]
            calculado = row["Hliq_calc"]
            row_hliq_nw = self.df_eco_hliq_NW.loc[(self.df_eco_hliq_NW["caso"] == row["caso"]) & (self.df_eco_hliq_NW["usina"] == row["usina"]) & (self.df_eco_hliq_NW["patamar"] == row["patamar"]) & (self.df_eco_hliq_NW["estagio"] == row["periodo"]) & (self.df_eco_hliq_NW["cenario"] == row["cenario"])]
            hliq_nw = row_hliq_nw["valor"].iloc[0]
            ERRO = (calculado-hliq_nw)/calculado
            new_row = pd.DataFrame({"caso": row["caso"],
                                     "usina": row["usina"],
                                     "periodo": row["periodo"],
                                     "dataInicio": dataInicioPeriodo,
                                     "cenario": row["cenario"],
                                    "patamar": row["patamar"],
                                     "Hliq_NW":hliq_nw,
                                     "Hliq_calc":calculado,
                                     "Erro":round(ERRO,2)},
                                   index = [0])
            df_comparacao = pd.concat([df_comparacao.loc[:],new_row]).reset_index(drop=True)
            
        return df_comparacao

    @property
    def df_hliq_calculado(self) -> pd.DataFrame:
        if self.__hliq_calculado is None:
            self.__gera_hliq_calculado()
        return self.__hliq_calculado

    @property
    def df_hliq_memoria(self) -> pd.DataFrame:
        if self.__hliq_memoria_calculo is None:
            self.__gera_hliq_calculado()
        return self.__hliq_memoria_calculo

    def __gera_hliq_calculado(self) -> pd.DataFrame:
        listaDF = []
        df_hliq_calculado = pd.DataFrame(columns=["caso", "usina", "usina_jusante", "periodo", "dataInicio","patamar","cenario", "Hliq_calc"])
        df_hliq_memoria = pd.DataFrame(columns=["caso", "usina", "usina_jusante", "periodo", "dataInicio","patamar","cenario", "Hmon_calc", "Hjus_calc", "perdas", "Hliq_calc"])
        for caso in self.casos:
             for u in self.usinas:
                 perdas = self.df_hidr.loc[(self.df_hidr["nome_usina"] == u.nome)]["perdas"].iloc[0]
                 for p in u.periodo:
                    df_altura_jusante_usi = self.df_altura_jusante_calculado.loc[(self.df_altura_jusante_calculado["caso"] == caso.nome) & (self.df_altura_jusante_calculado["usina"] == u.nome) & (self.df_altura_jusante_calculado["periodo"] == p)]
                    df_altura_montante_usi = self.df_altura_montante.loc[(self.df_altura_montante["caso"] == caso.nome) & (self.df_altura_montante["usina"] == u.nome) & (self.df_altura_montante["periodo"] == p)]
                    patamares = df_altura_jusante_usi["patamar"].unique()
                    cenarios = df_altura_jusante_usi["cenario"].unique()
                    dataInicial = df_altura_montante_usi.loc[(df_altura_montante_usi["periodo"] == p)]["dataInicio"].iloc[0]
                    for cen in cenarios:
                        hmon = df_altura_montante_usi.loc[(df_altura_montante_usi["cenario"] == cen)]["Hmon_calc"].iloc[0]
                        for pat in patamares:
                            hjus = df_altura_jusante_usi.loc[(df_altura_jusante_usi["cenario"] == cen) & (df_altura_jusante_usi["patamar"] == pat) ]["Hjus_calc"].iloc[0]
                            hliq = hmon - hjus - perdas
                            hliq = round(hliq,2)
                            new_row = pd.DataFrame({"caso": caso.nome,
                                         "usina": u.nome,
                                         "usina_jusante":u.nome_usina_jusante,
                                         "periodo": p,
                                         "dataInicio": dataInicial,
                                        "patamar": pat,
                                         "cenario": cen,
                                         "Hliq_calc":hliq},
                                   index = [0])
                            new_row_memoria = pd.DataFrame({"caso": caso.nome,
                                         "usina": u.nome,
                                         "usina_jusante":u.nome_usina_jusante,
                                         "periodo": p,
                                         "dataInicio": dataInicial,
                                        "patamar": pat,
                                         "cenario": cen,
                                        "Hmon_calc":hmon,
                                        "Hjus_calc":hjus,
                                        "perdas":perdas,
                                         "Hliq_calc":hliq},
                                   index = [0])
                            df_hliq_calculado = pd.concat([df_hliq_calculado.loc[:],new_row]).reset_index(drop=True)
                            df_hliq_memoria = pd.concat([df_hliq_memoria.loc[:],new_row_memoria]).reset_index(drop=True)
        self.__hliq_calculado = df_hliq_calculado
        self.__hliq_memoria_calculo = df_hliq_memoria
        return 0


    @property
    def df_eco_hliq_NW(self) -> pd.DataFrame:
        if self.__hliq_NW is None:
            self.__hliq_NW = self.__gera_hliq_NW()
        return self.__hliq_NW
        
    def __gera_hliq_NW(self) -> pd.DataFrame:
        listaDF = []
        for caso in self.casos:
            arq_sintese = join(
                caso.caminho, self.DIR_SINTESE, "HLIQ_UHE_PAT.parquet.gzip"
            )
            df = pd.read_parquet(arq_sintese)
            for u in self.usinas:
                for p in u.periodo:
                    df_usi = df.loc[(df["usina"] == u.nome) & (df["estagio"] == p)]
                    df_usi["caso"] = caso.nome
                    listaDF.append(df_usi)
                
        df_completo = pd.concat(listaDF)
        df_completo = df_completo.reset_index(drop = True)
        return df_completo

    
    @property
    def df_compara_hjus_newave_hjus_calculado(self) -> pd.DataFrame:
        if self.__compara_hjus_newave_hjus_calculado is None:
            self.__compara_hjus_newave_hjus_calculado = self.__gera_tabela_comparacao_hjus()
        return self.__compara_hjus_newave_hjus_calculado


    def __gera_tabela_comparacao_hjus(self) -> pd.DataFrame:
        lista_df = []
        df_comparacao = pd.DataFrame(columns=["caso", "usina", "usina_jusante", "periodo", "dataInicio","cenario", "patamar","Hjus_NW", "Hjus_calc", "Erro"   ])

        
        for index, row in self.df_altura_jusante_calculado.iterrows():
            dataInicioPeriodo = row["dataInicio"]
            calculado = row["Hjus_calc"]
            row_hjus_nw = self.df_eco_hjus_NW.loc[(self.df_eco_hjus_NW["caso"] == row["caso"]) & (self.df_eco_hjus_NW["usina"] == row["usina"]) & (self.df_eco_hjus_NW["patamar"] == row["patamar"]) & (self.df_eco_hjus_NW["estagio"] == row["periodo"]) & (self.df_eco_hjus_NW["cenario"] == row["cenario"])]
            hjus_nw = row_hjus_nw["valor"].iloc[0]
            ERRO = (calculado-hjus_nw)/calculado
            new_row = pd.DataFrame({"caso": row["caso"],
                                     "usina": row["usina"],
                                     "periodo": row["periodo"],
                                    "usina_jusante" : row["usina_jusante"],
                                     "dataInicio": dataInicioPeriodo,
                                     "cenario": row["cenario"],
                                    "patamar": row["patamar"],
                                     "Hjus_NW":hjus_nw,
                                     "Hjus_calc":calculado,
                                     "Erro":round(ERRO,2)},
                                   index = [0])
            df_comparacao = pd.concat([df_comparacao.loc[:],new_row]).reset_index(drop=True)
            
        return df_comparacao

    @property
    def df_eco_hjus_NW(self) -> pd.DataFrame:
        if self.__hjus_NW is None:
            self.__hjus_NW = self.__gera_hjus_NW()
        return self.__hjus_NW
        
    def __gera_hjus_NW(self) -> pd.DataFrame:
        listaDF = []
        for caso in self.casos:
            arq_sintese = join(
                caso.caminho, self.DIR_SINTESE, "HJUS_UHE_PAT.parquet.gzip"
            )
            df = pd.read_parquet(arq_sintese)
            for u in self.usinas:
                for p in u.periodo:
                    df_usi = df.loc[(df["usina"] == u.nome) & (df["estagio"] == p)]
                    df_usi["caso"] = caso.nome
                    listaDF.append(df_usi)
                
        df_completo = pd.concat(listaDF)
        df_completo = df_completo.reset_index(drop = True)
        return df_completo

    

    @property
    def df_altura_jusante_calculado(self) -> pd.DataFrame:
        if self.__hjus_calculado is None:
            self.__calcula_df_altura_jusante()
        return self.__hjus_calculado
        
    @property
    def df_altura_jusante_memoria(self) -> pd.DataFrame:
        if self.__hjus_memoria_calculo is None:
            self.__calcula_df_altura_jusante()
        return self.__hjus_memoria_calculo
        
    def __calcula_df_altura_jusante(self) -> pd.DataFrame:
        df_hjus_calculado = pd.DataFrame(columns=["caso", "usina", "usina_jusante", "periodo", "dataInicio","patamar","DurPat","cenario", "Hjus_calc"])
        df_hjus_memoria = pd.DataFrame(columns=["caso", "usina", "usina_jusante", "periodo","dataInicio" ,"patamar" , "DurPat", "cenario", "hmon_jus",
                                                "indice_familia1", "indice_familia2",
                                                "qtur", "indice_polinomio_1","indice_polinomio_2",
                                                "limite_inferior1", "limite_superior1", "limite_inferior2", "limite_superior2",
                                                "A0_1", "A1_1", "A2_1", "A3_1", "A4_1",  "A0_2", "A1_2", "A2_2", "A3_2", "A4_2",
                                                "hjus_1", "hjus_2", "fator_1", "fator_2", "Hjus_calc" ])

        df_temp = pd.DataFrame()
        for caso in self.casos:            
            for u in self.usinas:
                df_eco_hmon_NW_usi = self.df_eco_hmon_NW.loc[(self.df_eco_hmon_NW["usina"] == u.nome_usina_jusante)]
                df_eco_hmon_NW_usi = df_eco_hmon_NW_usi[df_eco_hmon_NW_usi[['cenario']].apply(lambda x: x[0].isdigit(), axis=1)]

                df_eco_curva_jusante_usi = self.df_eco_curvajusante.loc[(self.df_eco_curvajusante["codigo_usina"] == u.codigo)]
                df_eco_curvajusante_polinomio_usi = self.df_eco_curvajusante_polinomio.loc[(self.df_eco_curvajusante_polinomio["codigo_usina"] == u.codigo)]
                df_eco_curvajusante_polinomio_segmento_usi = self.df_eco_curvajusante_polinomio_segmento.loc[(self.df_eco_curvajusante_polinomio_segmento["codigo_usina"] == u.codigo)]
                df_vazao_jusante_usi = self.df_vazao_jusante.loc[(self.df_vazao_jusante["usina"] == u.nome)]
                
                cenarios = df_eco_hmon_NW_usi["cenario"].unique()
                patamares = df_vazao_jusante_usi["patamar"].unique()                
                for est in u.periodo:
                    dataInicial = df_eco_hmon_NW_usi.loc[(df_eco_hmon_NW_usi["estagio"] == est)]["dataInicio"].iloc[0]
                    for cen in cenarios:
                        hmon = df_eco_hmon_NW_usi.loc[(df_eco_hmon_NW_usi["estagio"] == est ) & (df_eco_hmon_NW_usi["cenario"] == cen)]["valor"].iloc[0]
                        hmon = round(hmon,4)
                        ## CODIGO PARA ENCONTRAR QUAIS FAMILIAS VAO SER USADAS
                        #hmon = 382.2
                        df_teste = pd.DataFrame()
                        df_teste = df_eco_curva_jusante_usi.copy()
                        df_teste["nivel_montante_referencia"] = (df_eco_curva_jusante_usi["nivel_montante_referencia"] - hmon).round(4)
                        lista_teste = df_teste["nivel_montante_referencia"].tolist()
                        indice_familias = []
                        elemento_anterior = 0
                        if(lista_teste[-1] < 0.00):
                            indice_familias.append(max(df_eco_curva_jusante_usi["indice_familia"].tolist()))

                        elif(lista_teste[0] > 0.00):
                            indice_familias.append(min(df_eco_curva_jusante_usi["indice_familia"].tolist()))
                        else:
                            elemento_anterior = 0
                            flag_fim = 0
                            for elemento in lista_teste:
                                if((elemento > 0.00) & (elemento_anterior < 0.00) & (flag_fim == 0)):
                                    indice_familias.append(df_teste.loc[(df_teste["nivel_montante_referencia"] == elemento_anterior)]["indice_familia"].iloc[0])
                                    indice_familias.append(df_teste.loc[(df_teste["nivel_montante_referencia"] == elemento)]["indice_familia"].iloc[0])
                                    flag_fim = 1
                                if((elemento == 0.00) & (flag_fim == 0)):
                                    indice_familias.append(df_teste.loc[(df_teste["nivel_montante_referencia"] == elemento)]["indice_familia"].iloc[0])                                 
                                    flag_fim = 1
                                elemento_anterior = elemento
                        for pat in patamares:
                            durPat = self.df_eco_patamares.loc[(self.df_eco_patamares["data"] == dataInicial) & (self.df_eco_patamares["patamar"] == int(pat)) ]["valor"].iloc[0]

                            df_vazao_jusante_usi_est_pat_cen = df_vazao_jusante_usi.loc[(df_vazao_jusante_usi["estagio"] == est) & (df_vazao_jusante_usi["patamar"] == pat) & (df_vazao_jusante_usi["cenario"] == cen)]["valor"].iloc[0]
                            df_vazao_jusante_usi_est_pat_cen = round(df_vazao_jusante_usi_est_pat_cen/durPat,4)
                            lista_hjus = []
                            save_old_hjus = []
                            salva_indice_polinomio = []
                            salva_limite_inferior = []
                            salva_limite_superior = []
                            salva_A0 = []
                            salva_A1 = []
                            salva_A2 = []
                            salva_A3 = []
                            salva_A4 = []
                            for familia in indice_familias:
                                n_polinomios = df_eco_curvajusante_polinomio_usi.loc[(df_eco_curvajusante_polinomio_usi["indice_familia"] == familia)]["numero_polinomios"].iloc[0]
                                df_familia = df_eco_curvajusante_polinomio_segmento_usi.loc[(df_eco_curvajusante_polinomio_segmento_usi["indice_familia"] == familia)]
                                lista_limite_inferior_vazao_jusante = df_familia["limite_inferior_vazao_jusante"].tolist()
                                lista_limite_superior_vazao_jusante = df_familia["limite_superior_vazao_jusante"].tolist()
                                indice_polinomio = 0
                                for contador in range(0,len(lista_limite_inferior_vazao_jusante)):
                                    if((df_vazao_jusante_usi_est_pat_cen >= lista_limite_inferior_vazao_jusante[contador]) & (df_vazao_jusante_usi_est_pat_cen <= lista_limite_superior_vazao_jusante[contador])):
                                        salva_limite_inferior.append(lista_limite_inferior_vazao_jusante[contador])
                                        salva_limite_superior.append( lista_limite_superior_vazao_jusante[contador])
                                        indice_polinomio = df_familia["indice_polinomio"].tolist()[contador]
                                        salva_indice_polinomio.append(indice_polinomio)
                                polinomios = df_familia.loc[(df_familia["indice_polinomio"] == indice_polinomio)]
                                A0 = polinomios["coeficiente_a0"].iloc[0]
                                A1 = polinomios["coeficiente_a1"].iloc[0]
                                A2 = polinomios["coeficiente_a2"].iloc[0]
                                A3 = polinomios["coeficiente_a3"].iloc[0]
                                A4 = polinomios["coeficiente_a4"].iloc[0]
                                salva_A0.append(A0)
                                salva_A1.append(A1)
                                salva_A2.append(A2)
                                salva_A3.append(A3)
                                salva_A4.append(A4)
                                hjus = A0*(df_vazao_jusante_usi_est_pat_cen**0) + A1*(df_vazao_jusante_usi_est_pat_cen**1) + A2*(df_vazao_jusante_usi_est_pat_cen**2) + A3*(df_vazao_jusante_usi_est_pat_cen**3) + A4*(df_vazao_jusante_usi_est_pat_cen**4)
                                lista_hjus.append(round(hjus,2))
                                save_old_hjus.append(round(hjus,2))
                            memoria_fatores = []
                            if(len(lista_hjus) == 2):
                                fator1 = 1-(abs(hmon - lista_hjus[0])/(lista_hjus[1] - lista_hjus[0]))
                                fator2 = 1-(abs(hmon - lista_hjus[1])/(lista_hjus[1] - lista_hjus[0]))
                                memoria_fatores.append(fator1)
                                memoria_fatores.append(fator2)
                                hjus = 0
                                hjus = fator1 * lista_hjus[0] + fator2*lista_hjus[1]
                                lista_hjus = []
                                lista_hjus.append(round(hjus,2))
                               
                            hjus = lista_hjus[0]
                            new_row = pd.DataFrame({"caso": caso.nome,
                                         "usina": u.nome,
                                         "usina_jusante":u.nome_usina_jusante,
                                         "periodo": est,
                                         "dataInicio": dataInicial,
                                        "patamar": pat,
                                        "DurPat":durPat,
                                         "cenario": cen,
                                         "Hjus_calc":hjus},
                                   index = [0])
                            indice_familia2 = 0 if len(indice_familias) == 1 else indice_familia[1]
                            hjus_2 = 0 if len(save_old_hjus) == 1 else save_old_hjus[1] 
                            memoria_fator_1 = 0 if len(memoria_fatores) == 0 else memoria_fatores[0] 
                            memoria_fator_2 = 0 if len(memoria_fatores) == 0 else memoria_fatores[1] 
                            indice_polinomio_2 = 0 if len(salva_indice_polinomio) == 1 else salva_indice_polinomio[1]
                            limite_inferior_2 =0 if len(salva_limite_inferior) == 1 else salva_limite_inferior[1]
                            limite_superior_2 =0 if len(salva_limite_superior) == 1 else salva_limite_superior[1]
                            A0_2 = 0 if len(salva_A0) == 1 else salva_A0[1]
                            A1_2 = 0 if len(salva_A1) == 1 else salva_A1[1]
                            A2_2 = 0 if len(salva_A2) == 1 else salva_A2[1]
                            A3_2 = 0 if len(salva_A3) == 1 else salva_A3[1]
                            A4_2 = 0 if len(salva_A4) == 1 else salva_A4[1]

                            new_row_memoria = pd.DataFrame({"caso": caso.nome,
                                                    "usina": u.nome,
                                                    "usina_jusante":u.nome_usina_jusante,
                                                    "periodo": est,
                                                    "dataInicio": dataInicial,
                                                    "patamar": pat,
                                                    "DurPat":durPat,
                                                    "cenario": cen,
                                                    "hmon_jus":hmon,
                                                    "indice_familia1": indice_familias[0],
                                                    "indice_familia2": indice_familia2,
                                                    "qtur":df_vazao_jusante_usi_est_pat_cen,
                                                    "indice_polinomio_1":salva_indice_polinomio[0],
                                                    "indice_polinomio_2":indice_polinomio_2,
                                                    "limite_inferior1":salva_limite_inferior[0], 
                                                    "limite_superior1":salva_limite_superior[0], 
                                                    "limite_inferior2":limite_inferior_2, 
                                                    "limite_superior2":limite_superior_2,
                                                    "A0_1":salva_A0[0], 
                                                    "A1_1":salva_A1[0],
                                                    "A2_1":salva_A2[0],
                                                    "A3_1":salva_A3[0],
                                                    "A4_1":salva_A4[0],
                                                    "A0_2":A0_2, 
                                                    "A1_2":A1_2, 
                                                    "A2_2":A2_2, 
                                                    "A3_2":A3_2, 
                                                    "A4_2":A4_2,                                                            
                                                    "hjus_1":save_old_hjus[0], 
                                                    "hjus_2":hjus_2, 
                                                    "fator_1":memoria_fator_1, 
                                                    "fator_2":memoria_fator_2, 
                                                    "Hjus_calc": hjus
                                                   },
                                   index = [0])

                            df_hjus_calculado = pd.concat([df_hjus_calculado.loc[:],new_row]).reset_index(drop=True)
                            df_hjus_memoria = pd.concat([df_hjus_memoria.loc[:],new_row_memoria]).reset_index(drop=True)
        
        self.__hjus_calculado = df_hjus_calculado
        self.__hjus_memoria_calculo = df_hjus_memoria
        return 0


    @property
    def df_qtur_pat(self) -> pd.DataFrame:
        return self.indicadores_FPHA.df_eco_qtur_pat

    @property
    def df_qver_pat(self) -> pd.DataFrame:
        return self.indicadores_FPHA.df_eco_qver_pat

    @property
    def df_eco_patamares(self) -> pd.DataFrame:
        return self.indicadores_FPHA.df_patamares
    

    @property
    def df_vazao_jusante(self) -> pd.DataFrame:
        if self.__calc_vazao_jusante is None:
            self.__calc_vazao_jusante = self.__gera_df_vazao_jusante()
        return self.__calc_vazao_jusante
        
    def __gera_df_vazao_jusante(self) -> pd.DataFrame:

        listDF = []
        for caso in self.casos:            
            for u in self.usinas:
                vertfuga = int(
                                self.df_hidr.loc[self.df_hidr["nome_usina"] == u.nome]["influencia_vertimento_canal_fuga"].iloc[0]
                            )
                df_filtered_qtur = self.df_qtur_pat.loc[(self.df_qtur_pat["caso"] == caso.nome) & (self.df_qtur_pat["usina"] == u.nome)]
                df_filtered_qtur =  df_filtered_qtur[df_filtered_qtur[['cenario']].apply(lambda x: x[0].isdigit(), axis=1)]
                df_filtered_qver = self.df_qver_pat.loc[(self.df_qver_pat["caso"] == caso.nome) & (self.df_qver_pat["usina"] == u.nome)]
                df_filtered_qver =  df_filtered_qver[df_filtered_qver[['cenario']].apply(lambda x: x[0].isdigit(), axis=1)]
                df_filtered_qvaz = df_filtered_qtur
                if vertfuga == 1: # if vertfuga == 1, #qjus = qtur_uhe + qver_uhe else : #qjus = qtur_uhe
                    df_filtered_qvaz["valor"] = df_filtered_qvaz["valor"] +  df_filtered_qver["valor"]
                listDF.append(df_filtered_qvaz)
        df_completo = pd.concat(listDF)
        return df_completo
        
    
    @property
    def df_eco_curvajusante(self) -> pd.DataFrame:
        if self.__eco_curvajusante is None:
            self.__gera_df_poljus_CSV()
        return self.__eco_curvajusante

    @property
    def df_eco_curvajusante_polinomio(self) -> pd.DataFrame:
        if self.__eco_curvajusante_polinomio is None:
            self.__gera_df_poljus_CSV()
        return self.__eco_curvajusante_polinomio

    @property
    def df_eco_curvajusante_polinomio_segmento(self) -> pd.DataFrame:
        if self.__eco_curvajusante_polinomio_segmento is None:
            self.__gera_df_poljus_CSV()
        return self.__eco_curvajusante_polinomio_segmento
    

    def __gera_df_poljus_CSV(self) -> pd.DataFrame:
        lista_df_curva_jusante = []
        lista_df_curvajusante_polinomio = []
        lista_df_curvajusante_polinomio_segmento = []
        for caso in self.casos:
            caminho  = "/".join( (caso.caminho,"polinjus.csv") )
            
            df_polinjus = UsinasHidreletricas.read(caminho)
            
            df_curvajusante_polinomio = ( df_polinjus.hidreletrica_curvajusante_polinomio(df=True) )
            
            df_curvajusante = df_polinjus.hidreletrica_curvajusante(df=True)

            df_curvajusante_polinomio_segmento  = df_polinjus.hidreletrica_curvajusante_polinomio_segmento(df=True)

            df_curvajusante_afogamentoexplicito_usina = ( df_polinjus.hidreletrica_curvajusante_afogamentoexplicito_usina( df=True) )

            for u in self.usinas:
                df_curvajusante_polinomio_usina = df_curvajusante_polinomio.loc[(df_curvajusante_polinomio["codigo_usina"] == u.codigo)].reset_index(drop = True)
                df_curvajusante_usina = df_curvajusante.loc[(df_curvajusante["codigo_usina"] == u.codigo)].reset_index(drop = True)
                df_curvajusante_polinomio_segmento_usina = df_curvajusante_polinomio_segmento.loc[(df_curvajusante_polinomio_segmento["codigo_usina"] == u.codigo)].reset_index(drop = True)

                lista_df_curva_jusante.append(df_curvajusante_usina)
                lista_df_curvajusante_polinomio.append(df_curvajusante_polinomio_usina)
                lista_df_curvajusante_polinomio_segmento.append(df_curvajusante_polinomio_segmento_usina)

            self.__eco_curvajusante = pd.concat(lista_df_curva_jusante)
            self.__eco_curvajusante_polinomio = pd.concat(lista_df_curvajusante_polinomio)
            self.__eco_curvajusante_polinomio_segmento = pd.concat(lista_df_curvajusante_polinomio_segmento)
        return 0

    
    
    @property
    def df_eco_hmon_NW(self) -> pd.DataFrame:
        if self.__hmon_NW is None:
            self.__hmon_NW = self.__gera_hmon_NW()
        return self.__hmon_NW
        
    def __gera_hmon_NW(self) -> pd.DataFrame:
        listaDF = []
        for caso in self.casos:
            arq_sintese = join(
                caso.caminho, self.DIR_SINTESE, "HMON_UHE_EST.parquet.gzip"
            )
            df = pd.read_parquet(arq_sintese)
            for u in self.usinas:
                df_usi = df.loc[(df["usina"] == u.nome)]
                df_usi_jus = df.loc[(df["usina"] == u.nome_usina_jusante)]
                df_usi["caso"] = caso.nome
                df_usi_jus["caso"] = caso.nome
                listaDF.append(df_usi)
                listaDF.append(df_usi_jus)
                
        df_completo = pd.concat(listaDF)
        df_completo = df_completo.reset_index(drop = True)
        return df_completo
        
    @property
    def df_eco_varmf_jusante(self) -> pd.DataFrame:
        if self.__eco_varmf_jusante is None:
            list_df = []
            df_just = self.__adiciona_eco_parquets_jusante("VARMF_UHE_EST")
            list_df.append(df_just)
            list_df.append(self.indicadores_FPHA.df_eco_varmf)
            self.__eco_varmf_jusante = pd.concat(list_df)
        return self.__eco_varmf_jusante

    @property
    def df_eco_varmi_jusante(self) -> pd.DataFrame:
        if self.__eco_varmi_jusante is None:
            list_df = []
            df_just = self.__adiciona_eco_parquets_jusante("VARMI_UHE_EST")
            list_df.append(df_just)
            list_df.append(self.indicadores_FPHA.df_eco_varmi)
            self.__eco_varmi_jusante = pd.concat(list_df)
        return self.__eco_varmi_jusante

    def __le_arquivo_sintese_caso(
        self, caso: CasoAvalicao, nome_sintese: str
    ) -> np.ndarray:
        caminho_caso = caso.caminho
        arq_sintese = join(
            caminho_caso, self.DIR_SINTESE, f"{nome_sintese}.parquet.gzip"
        )
        df = pd.read_parquet(arq_sintese)
        return df
    
    def __adiciona_eco_parquets_jusante(self, sintese) -> pd.DataFrame:
        lista_df = []
        for caso in self.casos:
            df_leitura = self.__le_arquivo_sintese_caso(caso, sintese)            
            for u in self.usinas:
                df_filtrado = df_leitura.loc[(df_leitura["usina"]== u.nome_usina_jusante )]
                df_filtrado["caso"] = caso.nome
                lista_df.append(df_filtrado)
        
        df_completo = pd.concat(lista_df)
        df_completo = df_completo.reset_index(drop = True)
        return df_completo
    
    @property
    def df_hidr(self) -> pd.DataFrame:
        if self.__df_hidr_com_jusante is None:
            self.__df_hidr_com_jusante = self.__gera_eco_hidr_com_jusante()
        return self.__df_hidr_com_jusante
        #return self.indicadores_FPHA.df_hidr


    def __gera_eco_hidr_com_jusante(self) -> pd.DataFrame:
        lista_df = []
        lista_df.append(self.indicadores_FPHA.df_hidr)
        for caso in self.casos:
            caminho_hidr  = "/".join( (caso.caminho,"hidr.dat") )
            df_leitura = Hidr.read(caminho_hidr).cadastro
            df_leitura = df_leitura.reset_index(drop = False)
            for u in self.usinas:
                codigo_usi_jusante = df_leitura.loc[(df_leitura["nome_usina"]== u.nome)]["codigo_usina_jusante"].iloc[0]
                nome_usina_jusante = df_leitura.loc[df_leitura["codigo_usina"] == codigo_usi_jusante]["nome_usina"].iloc[0]
                u.codigo_usina_jusante =  codigo_usi_jusante # DEFININDO NOVAS PROPRIEDADES
                u.nome_usina_jusante = nome_usina_jusante # DEFININDO NOVAS PROPRIEDADES
                u.codigo = df_leitura.loc[(df_leitura["nome_usina"]== u.nome)]["codigo_usina"].iloc[0]
                df_filtrado = df_leitura.loc[(df_leitura["nome_usina"]== nome_usina_jusante)]
                df_filtrado["caso"] = caso.nome
                lista_df.append(df_filtrado)
        df_completo = pd.concat(lista_df)
        df_completo = df_completo.reset_index(drop = True)
        return df_completo


     
    @property
    def df_eco_qver_pat(self) -> pd.DataFrame:
        return self.indicadores_FPHA.df_eco_qver_pat

    @property
    def df_eco_qtur_pat(self) -> pd.DataFrame:
        return self.indicadores_FPHA.df_eco_qtur_pat

    @property
    def df_compara_hmon_newave_hmon_calculado(self) -> pd.DataFrame:
        if self.__compara_hmon_newave_hmon_calculado is None:
            self.__compara_hmon_newave_hmon_calculado = self.__gera_tabela_comparacao_hmon()
        return self.__compara_hmon_newave_hmon_calculado


    def __gera_tabela_comparacao_hmon(self) -> pd.DataFrame:
        lista_df = []
        df_comparacao = pd.DataFrame(columns=["caso", "usina", "usina_jusante", "periodo", "dataInicio","cenario", "patamar","Hmon_NW", "Hmon_calc", "Erro"   ])

        
        for index, row in self.__hmon_calculado.iterrows():
            dataInicioPeriodo = row["dataInicio"]
            calculado = row["Hmon_calc"]
            row_hmon_nw = self.df_eco_hmon_NW.loc[(self.df_eco_hmon_NW["caso"] == row["caso"]) & (self.df_eco_hmon_NW["usina"] == row["usina"]) & (self.df_eco_hmon_NW["estagio"] == row["periodo"]) & (self.df_eco_hmon_NW["cenario"] == row["cenario"])]
            hmon_nw = row_hmon_nw["valor"].iloc[0]
            ERRO = (calculado-hmon_nw)/calculado
            new_row = pd.DataFrame({"caso": row["caso"],
                                     "usina": row["usina"],
                                     "periodo": row["periodo"],
                                     "dataInicio": dataInicioPeriodo,
                                     "cenario": row["cenario"],
                                     "Hmon_NW":hmon_nw,
                                     "Hmon_calc":calculado,
                                     "Erro":round(ERRO,2)},
                                   index = [0])
            df_comparacao = pd.concat([df_comparacao.loc[:],new_row]).reset_index(drop=True)
            
        return df_comparacao

    

    @property
    def df_altura_montante(self) -> pd.DataFrame:
        if self.__hmon_calculado is None:
            self.__calcula_df_altura_montante()
        return self.__hmon_calculado
        
    @property
    def df_altura_montante_memoria(self) -> pd.DataFrame:
        if self.__hmon_memoria_calculo is None:
            self.__calcula_df_altura_montante()
        return self.__hmon_memoria_calculo
        
    def __calcula_df_altura_montante(self) -> pd.DataFrame:
        df_hmon_resultado = pd.DataFrame(columns=["caso", "usina", "periodo", "dataInicio","cenario", "Hmon_calc"])
        df_hmon_memoria = pd.DataFrame(columns=["caso", "usina", "periodo","dataInicio" , "cenario", "vf_usi_per_jus", "vi_usi_per_jus", "v_med", "vmin_usi_jus", "A0", "A1", "A2", "A3", "A4", "Hmon_calc" ])

        df_temp = pd.DataFrame()
        for caso in self.casos: 
            for u in self.usinas:
                usinas_analise  = []
                usinas_analise.append(u.nome)
                usinas_analise.append(u.nome_usina_jusante)
                for nome_usi_analise in usinas_analise:
                    polinomio = self.df_pol_mon.loc[(self.df_pol_mon["usina"] == nome_usi_analise)]
                    v_min_usi_jus = self.__df_hidr_com_jusante.loc[self.__df_hidr_com_jusante["nome_usina"] == nome_usi_analise]["volume_minimo"].iloc[0]
                    for p in u.periodo:
                        cenarios =  self.df_eco_varmi_jusante[self.df_eco_varmi_jusante[['cenario']].apply(lambda x: x[0].isdigit(), axis=1)]["cenario"].unique()
                        dataInicial =self.df_eco_varmf_jusante.loc[(self.df_eco_varmf_jusante["estagio"] == p)]["dataInicio"].iloc[0]
                        for cen in cenarios:
                            vf_usi_per = self.df_eco_varmf_jusante.loc[(self.df_eco_varmf_jusante["usina"] == nome_usi_analise) & (self.df_eco_varmf_jusante["estagio"] == p) & (self.df_eco_varmf_jusante["cenario"] == cen)]["valor"].iloc[0]
                            vi_usi_per = self.df_eco_varmi_jusante.loc[(self.df_eco_varmi_jusante["usina"] == nome_usi_analise) & (self.df_eco_varmi_jusante["estagio"] == p) & (self.df_eco_varmi_jusante["cenario"] == cen)]["valor"].iloc[0]
                            v_med = ((vf_usi_per+vi_usi_per)/2) + v_min_usi_jus
                            h_mon = (v_med**0)*polinomio["A0"].iloc[0] + (v_med**1)*polinomio["A1"].iloc[0] + (v_med**2)*polinomio["A2"].iloc[0] + (v_med**3)*polinomio["A3"].iloc[0] + (v_med**4)*polinomio["A4"].iloc[0]
                            
                            h_mon = round(h_mon,2)
                            new_row = pd.DataFrame({"caso": caso.nome,
                                         "usina": nome_usi_analise,
                                         "periodo": p,
                                        "dataInicio": dataInicial,
                                         "cenario": cen,
                                         "Hmon_calc":h_mon},
                                   index = [0])
                            new_row_memoria = pd.DataFrame({"caso": caso.nome,
                                         "usina": nome_usi_analise,
                                         "periodo": p,
                                        "dataInicio": dataInicial,
                                         "cenario": cen,
                                         "vf": vf_usi_per,
                                         "vi": vi_usi_per,
                                         "v_med": v_med,
                                         "vmin_usi_jus": v_min_usi_jus,
                                         "A0" : polinomio["A0"].iloc[0], 
                                         "A1" : polinomio["A1"].iloc[0], 
                                         "A2" :  polinomio["A2"].iloc[0], 
                                         "A3" : polinomio["A3"].iloc[0], 
                                         "A4" : polinomio["A4"].iloc[0], 
                                         "Hmon_calc":h_mon},
                                   index = [0])
                            df_hmon_resultado = pd.concat([df_hmon_resultado.loc[:],new_row]).reset_index(drop=True)
                            df_hmon_memoria = pd.concat([df_hmon_memoria.loc[:],new_row_memoria]).reset_index(drop=True)
        
        self.__hmon_calculado = df_hmon_resultado
        self.__hmon_memoria_calculo = df_hmon_memoria
        return 0


    

    
    @property
    def df_pol_mon(self) -> pd.DataFrame:
        if self.__eco_polmon is None:
            self.__eco_polmon = self.__gera_df_polmon()
        return self.__eco_polmon
    

    def __gera_df_polmon(self) -> pd.DataFrame:
        df_temp = pd.DataFrame()
        for caso in self.casos:  
            usinas_calc_hmon = self.usinas
            for u in self.usinas:
                df_temp.at[u.nome_usina_jusante, "caso"] = caso.nome
                df_temp.at[u.nome_usina_jusante,"A0"] = self.df_hidr.loc[(self.df_hidr["codigo_usina"] == u.codigo_usina_jusante)]["a0_volume_cota"].iloc[0]
                df_temp.at[u.nome_usina_jusante,"A1"] = self.df_hidr[(self.df_hidr["codigo_usina"] == u.codigo_usina_jusante)]["a1_volume_cota"].iloc[0]
                df_temp.at[u.nome_usina_jusante,"A2"] = self.df_hidr[(self.df_hidr["codigo_usina"] == u.codigo_usina_jusante)]["a2_volume_cota"].iloc[0]
                df_temp.at[u.nome_usina_jusante,"A3"] = self.df_hidr[(self.df_hidr["codigo_usina"] == u.codigo_usina_jusante)]["a3_volume_cota"].iloc[0]
                df_temp.at[u.nome_usina_jusante,"A4"] = self.df_hidr[(self.df_hidr["codigo_usina"] == u.codigo_usina_jusante)]["a4_volume_cota"].iloc[0]
                df_temp.index.name = "usina"

                df_temp.at[u.nome, "caso"] = caso.nome
                df_temp.at[u.nome,"A0"] = self.df_hidr.loc[(self.df_hidr["codigo_usina"] == u.codigo)]["a0_volume_cota"].iloc[0]
                df_temp.at[u.nome,"A1"] = self.df_hidr[(self.df_hidr["codigo_usina"] == u.codigo)]["a1_volume_cota"].iloc[0]
                df_temp.at[u.nome,"A2"] = self.df_hidr[(self.df_hidr["codigo_usina"] == u.codigo)]["a2_volume_cota"].iloc[0]
                df_temp.at[u.nome,"A3"] = self.df_hidr[(self.df_hidr["codigo_usina"] == u.codigo)]["a3_volume_cota"].iloc[0]
                df_temp.at[u.nome,"A4"] = self.df_hidr[(self.df_hidr["codigo_usina"] == u.codigo)]["a4_volume_cota"].iloc[0]
                df_temp.index.name = "usina"
        df_temp = df_temp.reset_index(drop = False)
        
        return df_temp

    


    

        


    
    @property
    def df_pol_jus_HIDR(self) -> pd.DataFrame:
        if self.__eco_poljus_HIDR is None:
            self.__eco_poljus_HIDR = self.__gera_df_poljus_HIDR()
        return self.__eco_poljus_HIDR
    

    def __gera_df_poljus_HIDR(self) -> pd.DataFrame:
        numero_pol_jusante = int(self.df_hidr["numero_polinomios_jusante"].iloc[0])
        df_temp = pd.DataFrame()
        for caso in self.casos:            
            for u in self.usinas:
                for i in range(1,numero_pol_jusante+1):
                    df_temp.at[i,"caso"] = caso.nome
                    df_temp.at[i,"usina"] = u.nome
                    df_temp.at[i,"A0"] = self.df_hidr["a0_jusante_"+str(i)].iloc[0]
                    df_temp.at[i,"A1"] = self.df_hidr["a1_jusante_"+str(i)].iloc[0]
                    df_temp.at[i,"A2"] = self.df_hidr["a2_jusante_"+str(i)].iloc[0]
                    df_temp.at[i,"A3"] = self.df_hidr["a3_jusante_"+str(i)].iloc[0]
                    df_temp.at[i,"A4"] = self.df_hidr["a4_jusante_"+str(i)].iloc[0]
        df_temp.index.name = "indice_pol"
        return df_temp



  
        

    

        

























    
    
    def __le_arquivo_sintese_caso(
        self, caso: CasoAvalicao, nome_sintese: str
    ) -> np.ndarray:
        caminho_caso = caso.caminho
        arq_sintese = join(
            caminho_caso, self.DIR_SINTESE, f"{nome_sintese}.parquet.gzip"
        )
        df = pd.read_parquet(arq_sintese)
        return df

    

    def __gera_eco_parquets(self, sintese) -> pd.DataFrame:
        lista_df = []
        for caso in self.casos:
            df_leitura = self.__le_arquivo_sintese_caso(caso, sintese)            
            for u in self.usinas:
                df_filtrado = df_leitura.loc[(df_leitura["usina"]== u.nome)]
                df_filtrado["caso"] = caso.nome
                lista_df.append(df_filtrado)
        
        df_completo = pd.concat(lista_df)
        df_completo.reset_index(drop = True)
        df_completo.set_index("caso", inplace = True)
        return df_completo
        
