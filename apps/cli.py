import click
import os
import json
import warnings
from apps.utils.log import Log
@click.group()
def cli():
    """
    Aplicação para reproduzir testes
    de planejamento energético feitos no âmbito
    da FT-NEWAVE pelo ONS.
    """
    pass

@click.command("avalia-fpha")
@click.argument(
    "arquivo_json",
)
def avalia_fpha(arquivo_json):
    """
    Avaliacao da FPHA
    """
    
    warnings.filterwarnings('ignore')
    from apps.avalia_fpha.caso import CasoAvalicao
    from apps.avalia_fpha.usina import UsinaAvalicao
    from apps.avalia_fpha.indicadores import IndicadoresAvaliacaoFPHA
    from apps.avalia_fpha.graficos import GraficosAvaliacaoFPHA
    from apps.avalia_balanco.configuracao import Configuracao

    if os.path.isfile(arquivo_json):
        with open(arquivo_json, "r") as f:
            dados = json.load(f)
        # Cria objetos do estudo
        casos = [CasoAvalicao.from_dict(d) for d in dados["casos"]]
        usinas = [UsinaAvalicao.from_dict(d) for d in dados["usinas"]]
        configuracao = [Configuracao.from_dict(d) for d in dados["configuracao"]]

        configuracao[0].cenarios = list(range(1, 1951))
        configuracao[0].periodos = list(range(1, 51))

        indicadores = IndicadoresAvaliacaoFPHA(casos, usinas, configuracao)
        graficos = GraficosAvaliacaoFPHA(casos, usinas, configuracao)
        
        diretorio_saida = f"resultados/fpha"
        os.makedirs(diretorio_saida, exist_ok=True)

        arquivo_eco = "fpha_cortes.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_fpha_cortes.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=False)

        arquivo_eco = "eco_hidr.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_hidr.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=False)

        arquivo_eco = "eco_varmf.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_varmf.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=False)

        arquivo_eco = "eco_varmi.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_varmi.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=False)

        arquivo_eco = "eco_qtur_est.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_qtur_est.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=False)

        arquivo_eco = "eco_qver_est.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_qver_est.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=False)

        arquivo_eco = "eco_patamares.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_patamares.to_csv(os.path.join(diretorio_saida, arquivo_eco), index=False)

        #from apps.avalia_hliq.indicadores import IndicadoresAvaliacaoHJUS
        #indic_hjus = IndicadoresAvaliacaoHJUS(casos, usinas)
        Log.log().info("Gerando Graficos FPHA Temporal")
        mapa_titulo_fig_temporal = graficos.compara_newave_sddp_2(            
            indicadores.df_eco_fpha_cortes,
            indicadores.df_hidr,
            indicadores.df_eco_qtur_est,
            indicadores.df_eco_qver_est,
            indicadores.df_eco_varmi,
            indicadores.df_eco_varmf,
            indicadores.df_patamares
        )
        

        #mapa_titulo_fig_temporal = graficos.compara_newave_sddp(            
        #    indicadores.df_avl_fpha,
        #    indicadores.df_hidr,
        #    indicadores.df_eco_qtur_est,
        #    indicadores.df_eco_qver_est,
        #    indicadores.df_eco_varmi,
        #    indicadores.df_eco_varmf,
        #    indicadores.df_patamares
        #)



        mapa_titulo_fig = {
                           **mapa_titulo_fig_temporal,
                          }
        
        
        for titulo in mapa_titulo_fig:
            Log.log().info("Exportanto Grafico "+ titulo)
            mapa_titulo_fig[titulo].write_image(
                os.path.join(diretorio_saida, titulo+".png"),
                width=1200,
                height=800
            )

        exit(1)

        
        #arquivo_eco = "eco_avl_fpha.csv"
        #Log.log().info("Gerando Eco "+arquivo_eco)
        #indicadores.df_avl_fpha.to_csv(os.path.join(diretorio_saida, arquivo_eco), index=False)




        arquivo_eco = "eco_ghmax_newave.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_ghmax_newave.to_csv(os.path.join(diretorio_saida, arquivo_eco), index=False)
        
        arquivo_eco = "calculo_ghmax_fpha.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_ghmax_calculado.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=False)
        
        arquivo_eco = "memoria_calculo_ghmax_fpha.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_ghmax_memoria_calculo.to_csv(os.path.join(diretorio_saida, arquivo_eco), index=False)

        arquivo_eco = "eco_qtur_pat.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_qtur_pat.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=False)

        arquivo_eco = "eco_qver_pat.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_qver_pat.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=False)

        arquivo_compara = "compara_ghmax_newave_ghmax_calculado.csv"
        Log.log().info("Gerando Eco "+arquivo_compara)
        indicadores.df_compara_ghmax_newave_ghmax_calculado.to_csv(os.path.join(diretorio_saida, arquivo_compara), index=False)



        if( (indicadores.df_compara_ghmax_newave_ghmax_calculado["Erro"] < 0.01).all()):
            zeros = (indicadores.df_compara_ghmax_newave_ghmax_calculado["Erro"] == 0).sum()
            nonZeros = (indicadores.df_compara_ghmax_newave_ghmax_calculado["Erro"] != 0).sum()
            Log.log().info("TESTE CALCULO GHMAX - ERRO = 0: "+str(zeros) +" ERRO > 0: "+ str(nonZeros)+" -  STATUS: OK ")
        else:
            zeros = (indicadores.df_compara_ghmax_newave_ghmax_calculado["Erro"] == 0).sum()
            nonZeros = (indicadores.df_compara_ghmax_newave_ghmax_calculado["Erro"] != 0).sum()
            maximo =  (indicadores.df_compara_ghmax_newave_ghmax_calculado["Erro"]).max()
            Log.log().info("TESTE CALCULO GHMAX - ERRO = 0: "+str(zeros) +" ERRO > 0: "+ str(nonZeros)+" -  STATUS: FALHA - VERIFICAR ARQUIVO: "+arquivo_compara)
            Log.log().info("MAIOR ERRO: "+str(maximo))
            #print(indicadores.df_compara_ghmax_newave_ghmax_calculado)




        Log.log().info("Gerando Graficos Qturb cte")
        mapa_titulo_fig_turb_cte = graficos.turbinamento_constante(            
            indicadores.df_avl_fpha,
            indicadores.df_hidr
        )
        Log.log().info("Gerando Graficos Volu cte")
        mapa_titulo_fig_vol_cte = graficos.volume_constante(            
            indicadores.df_avl_fpha,
            indicadores.df_hidr
        )
        Log.log().info("Gerando Graficos GHMAX cte")
        mapa_titulo_fig_fpha_cte = graficos.fpha_constante(            
            indicadores.df_avl_fpha,
            indicadores.df_hidr
        )



        mapa_titulo_fig = {
                           **mapa_titulo_fig_turb_cte,
                           **mapa_titulo_fig_vol_cte,
                           **mapa_titulo_fig_fpha_cte
                          }
        
        
        for titulo in mapa_titulo_fig:
            Log.log().info("Exportanto Grafico "+ titulo)
            mapa_titulo_fig[titulo].write_image(
                os.path.join(diretorio_saida, titulo+".png"),
                width=1200,
                height=800
            )

        exit(1)

        Log.log().info("Gerando Grafico Scatter Periodo Qturb Varmf")
        mapa_titulo_fig_qturb_est_varmf_periodo = graficos.scatter_qturb_varmf_periodo(            
            indicadores.df_eco_qtur_est,
            indicadores.df_eco_varmf
        )

        Log.log().info("Gerando Grafico Scatter Patamar Qturb Varmf")
        mapa_titulo_fig_qturb_varmf_patamar = graficos.scatter_qturb_varmf_patamar(            
            indicadores.df_eco_qtur_pat,
            indicadores.df_eco_varmf
        )
        mapa_titulo_scatter = {**mapa_titulo_fig_qturb_est_varmf_periodo,
                               **mapa_titulo_fig_qturb_varmf_patamar
                              }
        for titulo in mapa_titulo_scatter:
            Log.log().info("Exportanto Grafico "+ titulo)
            mapa_titulo_scatter[titulo].write_image(
                os.path.join(diretorio_saida, titulo+".png"),
                width=1200,
                height=800
            )
        
        Log.log().info("Gerando Superficies FPHA")
        mapa_titulo_fig_superficie = graficos.superficie_fpha(
            indicadores.df_avl_fpha,
            indicadores.df_hidr
        )
        for titulo in mapa_titulo_fig_superficie:
            Log.log().info("Exportanto Grafico "+ titulo)
            mapa_titulo_fig_superficie[titulo].write_html(
                os.path.join(diretorio_saida, titulo+".html") 
            )
            mapa_titulo_fig_superficie[titulo].write_image(
                os.path.join(diretorio_saida, titulo+".png"),
                width=1200,
                height=800
            )

    else:
        raise FileNotFoundError(f"Arquivo {arquivo_json} não encontrado.")



@click.command("avalia-hliq")
@click.argument(
    "arquivo_json",
)
def avalia_hliq(arquivo_json):
    """
    Avaliacao do HJUS, HMON e HLIQ
    """
    
    warnings.filterwarnings('ignore')
    from apps.avalia_fpha.caso import CasoAvalicao
    from apps.avalia_fpha.usina import UsinaAvalicao
    from apps.avalia_hliq.indicadores import IndicadoresAvaliacaoHJUS
    from apps.avalia_hliq.graficos import GraficosAvaliacaoHJUS

    if os.path.isfile(arquivo_json):
        with open(arquivo_json, "r") as f:
            dados = json.load(f)
        # Cria objetos do estudo
        casos = [CasoAvalicao.from_dict(d) for d in dados["casos"]]
        usinas = [UsinaAvalicao.from_dict(d) for d in dados["usinas"]]

        indicadores = IndicadoresAvaliacaoHJUS(casos, usinas)
        graficos = GraficosAvaliacaoHJUS(casos, usinas)
        
        diretorio_saida = f"resultados/hliq"
        os.makedirs(diretorio_saida, exist_ok=True)

        arquivo_eco = "eco_hidr.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_hidr.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)
        
        arquivo_eco = "eco_qtur_pat.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_qtur_pat.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_qver_pat.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_qver_pat.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)
        
        arquivo_eco = "calc_vazao_jusante.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_vazao_jusante.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_patamares.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_patamares.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)
        
        
        
        arquivo_eco = "eco_poljus_hidr.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_pol_jus_HIDR.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_polmon_csv.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_pol_mon.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_altura_montante_Newave.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_hmon_NW.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        
        arquivo_eco = "calc_altura_montante.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_altura_montante.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "memoria_calculo_altura_montante.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_altura_montante_memoria.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "compara_altura_montante_NW_e_Calc.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_compara_hmon_newave_hmon_calculado.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)


        arquivo_eco = "eco_curva_jusante.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_curvajusante.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_curva_jusante_polinomio.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_curvajusante_polinomio.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_curva_jusante_polinomio_segmento.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_curvajusante_polinomio_segmento.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "calc_altura_jusante.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_altura_jusante_calculado.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_altura_jusante_Newave.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_hjus_NW.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)
        
        arquivo_eco = "memoria_df_altura_jusante.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_altura_jusante_memoria.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)
        
        arquivo_eco = "compara_altura_jusante_NW_e_Calc.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_compara_hjus_newave_hjus_calculado.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)


        arquivo_eco = "eco_altura_liquida_Newave.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_hliq_NW.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "calc_altura_liquida.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_hliq_calculado.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)
        
        arquivo_eco = "memoria_df_altura_liquida.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_hliq_memoria.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "compara_altura_liquida_NW_e_Calc.csv" 
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_compara_hliq_newave_hliq_calculado.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)


        Log.log().info("Gerando Gráficos Altura Montante")
        mapa_titulo_fig_hmon = graficos.polinomio_hmon(
            indicadores.df_hidr
        )
        for titulo in mapa_titulo_fig_hmon:
            Log.log().info("Exportanto Grafico "+ titulo)
            mapa_titulo_fig_hmon[titulo].write_image(
                os.path.join(diretorio_saida, titulo+".png"),
                width=1200,
                height=800
            )
            
        

        
    else:
        raise FileNotFoundError(f"Arquivo {arquivo_json} não encontrado.")





@click.command("avalia-evap")
@click.argument(
    "arquivo_json",
)
def avalia_evap(arquivo_json):
    """
    Avaliacao do EVAPORACAO
    """
    
    warnings.filterwarnings('ignore')
    from apps.avalia_fpha.caso import CasoAvalicao
    from apps.avalia_fpha.usina import UsinaAvalicao
    from apps.avalia_evap.indicadores import IndicadoresAvaliacaoEVAP
    from apps.avalia_hliq.graficos import GraficosAvaliacaoHJUS

    if os.path.isfile(arquivo_json):
        with open(arquivo_json, "r") as f:
            dados = json.load(f)
        # Cria objetos do estudo
        casos = [CasoAvalicao.from_dict(d) for d in dados["casos"]]
        usinas = [UsinaAvalicao.from_dict(d) for d in dados["usinas"]]

        indicadores = IndicadoresAvaliacaoEVAP(casos, usinas)
        graficos = GraficosAvaliacaoHJUS(casos, usinas)
        
        diretorio_saida = f"resultados/evap"
        os.makedirs(diretorio_saida, exist_ok=True)

        arquivo_eco = "eco_hidr.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_hidr.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_pol_cota_area_hidr.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_pol_cota_area_HIDR.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)


        arquivo_eco = "eco_coef_evapa_hidr.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_coef_evap_HIDR.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_volref_saz.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_volref_saz.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "calc_volref_saz.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_calc_volref_saz.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "memo_volref_saz.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_memoria_calc_volref_saz.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_evap_Newave.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_evap_Newave.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)


        arquivo_eco = "eco_evap_cortes_Newave.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_eco_nwv_cortes_evap_Newave.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        
        arquivo_eco = "eco_pol_cota_volume_hidr.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_pol_cota_volume_HIDR.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        
        arquivo_eco = "calc_evap_ref.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_calc_evap_ref.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "memo_evap_ref.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_memoria_calc_evap_ref.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "compara_evap_ref.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_compara_evap_ref_newave_evap_ref_calc.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "calc_derivadas.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_calc_derivadas.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "memo_derivadas.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_memo_derivadas.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "compara_derivadas.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_compara_derivadas.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)
    
        
    else:
        raise FileNotFoundError(f"Arquivo {arquivo_json} não encontrado.")



@click.command("avalia-balanco")
@click.argument(
    "arquivo_json",
)
def avalia_balanco(arquivo_json):
    """
    Avaliacao do Balanço Hidrico
    """
    
    warnings.filterwarnings('ignore')
    from apps.avalia_fpha.caso import CasoAvalicao
    from apps.avalia_balanco.configuracao import Configuracao
    from apps.avalia_fpha.usina import UsinaAvalicao
    from apps.avalia_balanco.indicadores import IndicadoresAvaliacaoBalanco
    from apps.avalia_hliq.graficos import GraficosAvaliacaoHJUS

    if os.path.isfile(arquivo_json):
        with open(arquivo_json, "r") as f:
            dados = json.load(f)
        # Cria objetos do estudo
        casos = [CasoAvalicao.from_dict(d) for d in dados["casos"]]
        configuracao = [Configuracao.from_dict(d) for d in dados["configuracao"]]
        usinas = [UsinaAvalicao.from_dict(d) for d in dados["usinas"]]

        indicadores = IndicadoresAvaliacaoBalanco(casos, usinas, configuracao) 
        graficos = GraficosAvaliacaoHJUS(casos, usinas)
        
        diretorio_saida = f"resultados/balanco"
        os.makedirs(diretorio_saida, exist_ok=True)

        arquivo_eco = "eco_varmf_uhe_est.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_varmf_uhe_est.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_varmi_uhe_est.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_varmi_uhe_est.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)


        arquivo_eco = "eco_vdes_uhe_est.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_vdes_uhe_est.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_vret_uhe_est.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_vret_uhe_est.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_vtur_uhe_est.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_vtur_uhe_est.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_vver_uhe_est.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_vver_uhe_est.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_vafl_uhe_est.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_vafl_uhe_est.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_vevap_uhe_est.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_vevap_uhe_est.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

       
        arquivo_eco = "calc_balanco_hidrico.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_balanco_hidrico_usina.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)
    
        
    else:
        raise FileNotFoundError(f"Arquivo {arquivo_json} não encontrado.")

@click.command("avalia-balanco-demanda")
@click.argument(
    "arquivo_json",
)
def avalia_balanco_demanda(arquivo_json):
    """
    Avaliacao do Balanço Demanda
    """
    
    warnings.filterwarnings('ignore')
    from apps.avalia_fpha.caso import CasoAvalicao
    from apps.avalia_balanco.configuracao import Configuracao
    from apps.avalia_fpha.usina import UsinaAvalicao
    from apps.avalia_balanco_demanda.indicadores_demanda import IndicadoresAvaliacaoBalancoDemanda
    from apps.avalia_hliq.graficos import GraficosAvaliacaoHJUS

    if os.path.isfile(arquivo_json):
        with open(arquivo_json, "r") as f:
            dados = json.load(f)
        # Cria objetos do estudo
        casos = [CasoAvalicao.from_dict(d) for d in dados["casos"]]
        configuracao = [Configuracao.from_dict(d) for d in dados["configuracao"]]
        usinas = [UsinaAvalicao.from_dict(d) for d in dados["usinas"]]

        indicadores = IndicadoresAvaliacaoBalancoDemanda(casos, usinas, configuracao) 
        graficos = GraficosAvaliacaoHJUS(casos, usinas)
        
        diretorio_saida = f"resultados/balanco"
        os.makedirs(diretorio_saida, exist_ok=True)


        arquivo_eco = "eco_mercL_SBM.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_mercL_SBM.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)
       
        arquivo_eco = "eco_gt_SBM.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_gt_SBM.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_gh_SBM.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_gh_SBM.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_interc_SBM.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_interc_SBM.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_exc_SBM.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_exc_SBM.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_def_SM.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_def_SM.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "calc_balanco_demanda_SBM.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_balanco_demanda_SBM.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)


        arquivo_eco = "eco_mercL_SIN.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_mercL_SIN.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)
       
        arquivo_eco = "eco_gt_SIN.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_gt_SIN.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_gh_SIN.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_gh_SIN.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_def_SIN.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_def_SIN.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_exc_SIN.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_exc_SIN.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)


        arquivo_eco = "calc_balanco_demanda_SIN.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_balanco_demanda_SIN.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)
    
        
    else:
        raise FileNotFoundError(f"Arquivo {arquivo_json} não encontrado.")

@click.command("avalia-custos")
@click.argument(
    "arquivo_json",
)
def avalia_custos(arquivo_json):
    """
    Avaliacao do Custos
    """
    
    warnings.filterwarnings('ignore')
    from apps.avalia_fpha.caso import CasoAvalicao
    from apps.avalia_fpha.usina import UsinaAvalicao
    from apps.avalia_custos.indicadores import IndicadoresAvaliacaoCustos
    from apps.avalia_hliq.graficos import GraficosAvaliacaoHJUS

    if os.path.isfile(arquivo_json):
        with open(arquivo_json, "r") as f:
            dados = json.load(f)
        # Cria objetos do estudo
        casos = [CasoAvalicao.from_dict(d) for d in dados["casos"]]
        usinas = [UsinaAvalicao.from_dict(d) for d in dados["usinas"]]

        indicadores = IndicadoresAvaliacaoCustos(casos, usinas)
        graficos = GraficosAvaliacaoHJUS(casos, usinas)
        
        diretorio_saida = f"resultados/custos"
        os.makedirs(diretorio_saida, exist_ok=True)

        arquivo_eco = "eco_custo_gt.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_custo_gt.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        arquivo_eco = "eco_taxa_desconto_anual.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_taxa_desconto_anual.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)
        
        
        arquivo_eco = "calc_custo_gt_valor_presente.csv"
        Log.log().info("Gerando Eco "+arquivo_eco)
        indicadores.df_custo_gt_valor_presente.to_csv(os.path.join(diretorio_saida, arquivo_eco),index=True)

        
        
    else:
        raise FileNotFoundError(f"Arquivo {arquivo_json} não encontrado.")





@click.command("ftnewave")
@click.argument(
    "arquivo_txt",
)
def avalia_ftnewave(arquivo_txt):
    """
    Realiza Rodadas da FTNEWAVE
    - Pega um deck teste com o caminho apontado no txt
    - Realiza o conjunto de testes descritos no txt
    """
    
    warnings.filterwarnings('ignore')
    from apps.automatizacao_ftnewave.restricoes_eletricas_especiais import RestricoesEletricasEspeciais
    from apps.automatizacao_ftnewave.balanco_demanda import Balanco_Demanda
    from apps.automatizacao_ftnewave.balanco_hidrico import Balanco_Hidrico
    from apps.automatizacao_ftnewave.evaporacao import Evaporacao
    from apps.automatizacao_ftnewave.hmon import Hmon
    from apps.automatizacao_ftnewave.organizaTestes import OrganizaTestes
    print("--------- Realizando Testes da FT-NEWAVE---------------")
    flag_prossegue = 0
    with open(arquivo_txt, "r") as file:
        for line in file:
            if("caminho" in line):
                caminho = line.split('"')[1]
                if os.path.isdir(caminho):
                    print("Pasta: ", caminho, " Existe, Prosseguindo")
                else:
                    print("ERRO: Pasta: ", caminho, " Não Existe")
                    exit(1)
                OrganizaTestes(caminho)
                flag_prossegue = 1
            if(line.startswith("&")):
                continue  
            if("Restricao_Eletrica_Especial" in line and flag_prossegue == 1):
                print("INICIALIZANDO TESTES DE RESTRICOES ELETRICAS ESPECIAIS")
                print(line.strip())
                RestricoesEletricasEspeciais(caminho)
            if("Balanco_Demanda" in line and flag_prossegue == 1):
                print("INICIALIZANDO TESTES DE BALANÇO DE DEMANDA")
                print(line.strip())
                Balanco_Demanda(caminho)
                
            if("Balanco_Hidrico_Usina" in line and flag_prossegue == 1):
                print("INICIALIZANDO TESTES DE BALANÇO HIDRICO DAS USINAS")
                print(line.strip())
                Balanco_Hidrico(caminho)

            if("Altura" in line and flag_prossegue == 1):
                print("INICIALIZANDO TESTES DE BALANÇO HIDRICO DAS USINAS")
                print(line.strip())
                Hmon(caminho)

            if("Evaporacao" in line and flag_prossegue == 1):
                print("INICIALIZANDO TESTES DE EVAPORACAO")
                print(line.strip())
                Evaporacao(caminho)
            else:
                print(line.strip())
            
            

cli.add_command(avalia_hliq)
cli.add_command(avalia_fpha)
cli.add_command(avalia_evap)
cli.add_command(avalia_balanco)
cli.add_command(avalia_balanco_demanda)
cli.add_command(avalia_custos)
cli.add_command(avalia_ftnewave)
