def ler_config(S):
    """
    Lê o ficheiro de configuração "config_S.txt" e devolve um dicionário com os parâmetros.

    Args:
        S (str): Código da simulação (por exemplo, "T11").

    Returns:
        dict: Dicionário contendo as constantes e os valores lidos do ficheiro.
    """
    ficheiro = f"config_{S}.txt"
    parametros = {}

    try:
        with open(ficheiro, "r") as f:
            linhas = f.readlines()

        # Processar linha a linha
        for linha in linhas:
            # Separar chave e valor
            chave, valor = linha.split("=", 1)
            chave = chave.strip()
            valor = valor.strip()

            # Verifica dacă expresia conține chei (și păstreaz-o neevaluată)
            if any(key in valor for key in parametros):
                parametros[chave] = valor  # Păstrează expresia ca text
            else:
                try:
                    parametros[chave] = eval(valor, {}, parametros)
                except Exception:
                    parametros[chave] = valor  # Salvează ca string dacă nu poate fi evaluat

    except Exception as e:
        print(f"Erro ao processar o ficheiro {ficheiro}: {e}")

    return parametros


# T12
def nova_pessoa(idade=0):
    """
    Cria uma nova pessoa com todos os campos necessários.

    Args:
        idade (int): Idade da pessoa (por omissão = 0).

    Returns:
        dict: Um dicionário representando a pessoa.
    """
    global proximo_cc

    # Determinar o género com base no número de CC
    genero = "M" if proximo_cc % 2 == 0 else "F"

    # Criar o dicionário representando a pessoa
    pessoa = {
        "cc": proximo_cc,
        "nome": f"Pessoa_{proximo_cc}",
        "genero": genero,
        "idade": idade,
        "salario": SALARIO_BASE,
        "pensao": PENSAO_BASE
    }

    # Incrementar o CC para garantir que o próximo é único
    proximo_cc += 1

    return pessoa


# T13
def ler_populacao_inicial(S):
    new_population = []

    file = f"população_inicial_{S}.txt"
    with open(file, 'r') as population:
        for line in population:
            dados = line.strip().split(',')

            idade = int(dados[3])
            genero = dados[2].strip()

            new_p = nova_pessoa(idade)
            new_population.append(new_p)

    return new_population


# exclude
def exclude_entities(entities, p, year):
    """
    Exclude a percentage p of entities deterministically based on the year.

    Parameters:
        entities (list of dict): List of entities.
        p (float): The percentage of entities to exclude (0 <= p <= 1).
        year (int): The year used for deterministic variation.

    Returns:
        list of dict: List of entities that are not excluded.
    """
    num_to_exclude = int(len(entities) * p)

    # Calculate a score for each entity based on its index and the year
    entities_sorted = sorted(
        enumerate(entities),
        key=lambda e: (e[0] + year) % 100  # e[0] is the index
    )

    # Exclude the first num_to_exclude entities based on the sorted order
    included_entities = [entity for i, entity in entities_sorted[num_to_exclude:]]
    return included_entities


# T21
def simula_ano(populacao, ano_corrente):
    """
    Simula a passagem de um ano em termos demográficos.

    Args:
        populacao (list): Lista de pessoas (dicionários com atributo 'idade').
        ano_corrente (int): Ano atual da simulação.

    Returns:
        list: Nova população após a simulação do ano.
    """
    # 1. Salvar o tamanho da população original (antes da mortalidade)
    tamanho_original = len(populacao)

    # 2. Incrementar a idade de todos os indivíduos
    for pessoa in populacao:
        pessoa['idade'] += 1

    # 3. Remover pessoas com idade maior que 100
    populacao = [p for p in populacao if p['idade'] <= 100]

    # 4. Aplicar mortalidade
    nova_populacao = []
    for faixa_etaria, (range_idade, taxa_mortalidade) in MORTALIDADE.items():
        grupo_atual = [p for p in populacao if p['idade'] in range_idade]
        sobreviventes = exclude_entities(grupo_atual, taxa_mortalidade, ano_corrente)
        nova_populacao.extend(sobreviventes)

    populacao = nova_populacao

    # 5. Calcular o número de novos bebês (1% da população original)
    num_bebes = max(1, tamanho_original // NATALIDADE)
    novos_bebes = [nova_pessoa(idade=0) for _ in range(num_bebes)]
    populacao.extend(novos_bebes)

    return populacao


# T22
def cobra_seg_social(ano, total, population):
    # IDADE_REFORMA =67
    contribution = sum(
        person['salario'] * 0.23 for person in population if person['idade'] in range(23, IDADE_REFORMA + 1))
    total += contribution
    pensao = sum(person['pensao'] for person in population if person['idade'] in range(IDADE_REFORMA + 1, 102))
    total -= pensao

    return float(total)


# T3

### Programação 1 Grupo 236
### Vlad Digori - 64120
### Nome2 Apelido2 Número2

config = ler_config('11')


proximo_cc = config['CC']
IDADE_REFORMA = config['IDADE_REFORMA']
SALARIO_BASE = config['SALARIO_BASE']
PENSAO_BASE = config['PENSAO_BASE']
ano_start = config['ANO_INICIAL']
fundo_p = config['FUNDO_PENSOES_INICIAL']
epocas = config['EPOCAS']
populacao = ler_populacao_inicial(11)
MORTALIDADE = config['MORTALIDADE']
NATALIDADE = config['NATALIDADE']
print(f'A simulação começou no ano {ano_start}, com população total de {len(populacao)}, e o fundo de pensões a valer {fundo_p}.')

for i in range(epocas + 1):
    ano_actual = ano_start + i
    populacao = simula_ano(populacao, ano_actual)
    fundo_p = cobra_seg_social(ano_actual, fundo_p, populacao)
    if fundo_p < 0:
        print(
            f"No ano {ano_actual}, a população foi {len(populacao)} e o fundo de pensões foi negativo, com valor {fundo_p}.")
        # 1000000 no final
        # 10000000 no config

print( f'A simulação terminou no ano {ano_start + epocas}, com população total de {len(populacao)} pessoas e o fundo de pensões vale {fundo_p}.')