import click
import os
import json
import warnings
from apps.utils.log import Log
@click.group()
def cli():
    """
    Aplicação para transformar casos de Newave
    """
    pass

@click.command("prospectivo")
@click.argument(
    "arquivo_txt",
)
def prospectivo(arquivo_txt):
    
    warnings.filterwarnings('ignore')
    from apps.prospectivo.transformaProspectivo import TransformaProspectivo
    print("--------- Realizando Transformação do caso em prospectivo---------------")
    flag_prossegue = 0
    with open(arquivo_txt, "r") as file:
        for line in file:
            if("caminho" in line):
                caminho = line.split('"')[1]
                if os.path.isdir(caminho):
                    print("Pasta: ", caminho, " Existe, Prosseguindo")
                    flag_prossegue = 1
                else:
                    print("ERRO: Pasta: ", caminho, " Não Existe")
                    exit(1)
                    
            if(line.startswith("&")):
                continue  
            if(flag_prossegue == 1):
                print("INICIALIZANDO Transformação do deck")
                TransformaProspectivo(caminho, arquivo_txt)
                flag_prossegue = 0

cli.add_command(prospectivo)
