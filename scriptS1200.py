import os
import xml.etree.ElementTree as ET


# Função para adicionar o namespace ao caminho do elemento
def ns(tag, namespace):
    return f"{{{namespace}}}{tag}"


# Função para buscar o CPF no XML e retornar as informações necessárias
def buscar_informacoes_por_cpf(caminho_arquivo, cpf, namespace_evt, namespace_retorno):
    try:
        tree = ET.parse(caminho_arquivo)
        root = tree.getroot()

        # Procurar o CPF no XML
        cpf_xml = root.find(
            f".//{ns('ideTrabalhador', namespace_evt)}/{ns('cpfTrab', namespace_evt)}"
        )

        if cpf_xml is not None and cpf_xml.text == cpf:
            # Encontrar o ID do evento
            id_evento_novo = root.find(
                f".//{ns('evtRemun', namespace_evt)}"
            ).attrib.get("Id")

            # Procurar o nrRecibo dentro da tag <retornoEvento> > <recibo> > <nrRecibo>
            nr_recibo = root.find(
                f".//{ns('retornoEvento', namespace_retorno)}/{ns('recibo', namespace_retorno)}/{ns('nrRecibo', namespace_retorno)}"
            )

            # Verificar se o número do recibo foi encontrado
            nr_recibo_text = (
                nr_recibo.text if nr_recibo is not None else "NR_RECIBO_NAO_ENCONTRADO"
            )

            return id_evento_novo, nr_recibo_text, cpf_xml.text
        return None
    except ET.ParseError:
        return None
    except Exception as e:
        return None


# Função principal para processar a lista de IDs e CPFs
def processar_lista_cpfs(
    lista_ids_cpfs, caminho_pasta_xml, namespace_evt, namespace_retorno
):
    resultados = []

    # Percorrer cada ID antigo e CPF da lista
    for id_antigo, cpf in lista_ids_cpfs:
        for arquivo in os.listdir(caminho_pasta_xml):
            if arquivo.endswith(".xml"):
                caminho_completo = os.path.join(caminho_pasta_xml, arquivo)

                informacoes = buscar_informacoes_por_cpf(
                    caminho_completo, cpf, namespace_evt, namespace_retorno
                )

                # Se encontrar as informações, armazenar no resultado
                if informacoes is not None:
                    id_evento_novo, nr_recibo, cpf_encontrado = informacoes
                    resultados.append(
                        (id_evento_novo, nr_recibo, cpf_encontrado, id_antigo)
                    )
                    break  # Sai do loop se as informações foram encontradas

    return resultados


# Funções para salvar os resultados em um arquivo TXT
def salvar_resultados_em_txt(resultados, caminho_arquivo_txt):
    with open(caminho_arquivo_txt, "w") as f:
        for resultado in resultados:
            # f.write(f"ID Evento Novo: {resultado[0]}\n")
            # f.write(f"NR Recibo: {resultado[1]}\n")
            # f.write(f"CPF Encontrado: {resultado[2]}\n")
            # f.write(f"ID Antigo: {resultado[3]}\n\n")

            f.write(
                f"update esocial.s1200 set idevento='{resultado[0]}', situacao='1' where cpftrab='{resultado[2]}' and idevento='{resultado[3]}' and perapur='2024-08';\n\n"
            )
            f.write(
                f"update esocial.historico set idevento='{resultado[0]}', nr_recibo='{resultado[1]}', message='201 - Lote processado com sucesso', status='P' where idevento='{resultado[3]}';\n\n"
            )


# Namespaces do XML
namespace_evt = "http://www.esocial.gov.br/schema/evt/evtRemun/v_S_01_02_00"
namespace_retorno = "http://www.esocial.gov.br/schema/evt/retornoEvento/v1_2_1"

# Lista de IDs antigos e CPFs fornecida
lista_ids_cpfs = [
    ("IDEVENTO", "CPFTRAB"),
]

# Caminho para a pasta contendo os arquivos XML
caminho_pasta_xml = "C:/Users/itarg/Downloads/TomeAcuS1200-/S-1200"

# Processar a lista e obter os resultados
resultados = processar_lista_cpfs(
    lista_ids_cpfs, caminho_pasta_xml, namespace_evt, namespace_retorno
)

# Caminho para salvar o arquivo TXT com os resultados
caminho_arquivo_txt = "C:/Users/itarg/Downloads/resultados.txt"

# Salvar os resultados em um arquivo TXT
salvar_resultados_em_txt(resultados, caminho_arquivo_txt)
