#T11

def ler_config(S):
    """
    Read simulation configuration from 'config_S.txt'

    Args:
        S (str): Simulation code

    Returns:
        dict: Configuration parameters
    """
    filename = f"config_{S}.txt"
    config = {}

    with open(filename, 'r') as file:
        # First pass: read all simple values
        for line in file:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=')
                key = key.strip()
                value = value.split('#')[0].strip()

                # Handle numeric expressions
                try:
                    # Attempt to evaluate numeric expressions
                    config[key] = eval(value)
                except:
                    # If evaluation fails, handle as before
                    if value.lower() in ['true', 'false']:
                        config[key] = value.lower() == 'true'
                    else:
                        config[key] = value

    # Second pass: handle ranges and complex structures
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=')
                key = key.strip()
                value = value.split('#')[0].strip()

                # Handle ranges and complex structures
                if 'range' in value:
                    # Replace known variables
                    if 'IDADE_REFORMA' in value:
                        value = value.replace('IDADE_REFORMA', str(config.get('IDADE_REFORMA', 67)))
                    config[key] = eval(value)
                elif value.startswith('{'):
                    # For complex dictionary-like structures like MORTALIDADE
                    config[key] = eval(value)

    return config








#T12
cc=1000000

def nova_pessoa(idade=0,config=None):
    global cc
    """
    Creates a new person 


    Args :
        idade (int) inicial value = 0  
        config = None (dict) dictionary from configuration to read the salary and other things   


    Return:
        Pessoa (dict) the persons info
    """
    genero = 'M' if cc % 2 == 0 else 'F'

    cc += 1


    pessoa = {
        'cc': cc,
        'nome': f'Pessoa_{cc}',
        'genero': genero,
        'idade': idade,
        'salario': config['SALARIO_BASE'] if 23 <= idade and idade <= config['IDADE_REFORMA'] else 0,
        'pensao': config['PENSAO_BASE'] if idade >= config['IDADE_REFORMA'] else 0
    }

    return pessoa



#T13
def ler_populacao_inicial(S, config):
    """
    Read the initial population from a file.

    Args:
        S (str): Simulation code.
        config (dict): Configuration dictionary.

    Returns:
        list: Initial population.
    """
    new_population = []
    file_pop = f'população_inicial_{S}.txt'

    with open(file_pop, 'r') as populacion:
        for line in populacion:
            idade_data = line.strip().split(',')

            try:
                # Attempt to get the age from the expected position
                idade = int(idade_data[3])
            except (ValueError, IndexError):
                # If not possible, search for any valid age in the line
                idade = None
                for data in idade_data:
                    try:
                        idade = int(data)
                        break
                    except ValueError:
                        continue
                if idade is None:
                    # Skip this line if no valid age is found
                    continue

            new_pers = nova_pessoa(idade, config)
            new_population.append(new_pers)

    return new_population




#exclude
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







#T21
def simula_ano(populacao, ano_corrente,config):
    """


    Args:
        populacao: list
        ano_corrente: int
        config: dict

    Returns:

    """
    for person in populacao:
        person['idade']+=1
    populacao = [person for person in populacao if person['idade'] <= config['MAX_IDADE']]
    for groups,(idade_range,rate) in config['MORTALIDADE'].items():
        group_population= [p for p in populacao if p['idade']in idade_range]
        survive=exclude_entities(group_population,rate,ano_corrente)
        populacao=[p for p in populacao if p not in group_population or p in survive]

    #new people
    birth_rate = max(1, len(populacao) // config['NATALIDADE'])
    novos_nascidos = [nova_pessoa(0, config) for _ in range(birth_rate)]

    populacao.extend(novos_nascidos)

    for person in populacao:
        if person['idade'] >= config['IDADE_REFORMA']:
            person['salario'] = 0
            person['pensao'] = config['PENSAO_BASE']
        elif person['idade'] in config['ACTIVO']:
            person['salario'] = config['SALARIO_BASE']
            person['pensao'] = 0
        else:
            person['salario'] = 0
            person['pensao'] = 0

    return populacao








#T22
def cobra_seg_social(ano, total, population,config):

        contribution =sum(person['salario']*config['DESCONTOS'] for person in population if person['idade'] in config['ACTIVO'])
        total+=contribution
        pensao=sum(person['pensao'] for person in population if person['idade'] in config['PENSIONISTA'])
        total-=pensao

        return int(total)


#T3

### Programação 1 Grupo 236
### Vlad Digori - 64120
### Nome2 Apelido2 Número2
def main(S):

    config=ler_config(S)

    populacion = ler_populacao_inicial(S,config)
    ano_start=config['ANO_INICIAL']
    fundo_p=config['FUNDO_PENSOES_INICIAL']
    epocas=config['EPOCAS']

    print(f'A simulação começou no ano de {ano_start}, com população total de {len(populacion)}, e o fundo de pensões a valer {fundo_p}.')

    for i in range(epocas):
        ano_actual=ano_start+i
        populacion=simula_ano(populacion,ano_actual,config)

        fundo_p=cobra_seg_social(ano_actual,fundo_p,populacion,config)


        if fundo_p<0:
            print(f"No ano {ano_actual}, a população foi {len(populacion)} e o fundo de pensões foi negativo, com valor {fundo_p}.")
        #break#sa nu mearga iar pana la  2041
    print(f'A simulação terminou no ano {ano_start+epocas}, com população total de {len(populacion)} pessoas e o fundo de pensões vale {fundo_p}.')

    with open(f'população_final_{S}.txt','w') as final:
        for person in populacion:
            final.write(str(person['cc'])+', '+person['nome']+', '+ str(person['genero'])+', '+str(person['idade'])+', '+str(person['salario'])+', '+str(person['pensao'])+'\n')
if __name__ == "__main__":
   main(11)


"""
ceva merge rau la salariu ca la unele persoane acesta nu alocheaza salariu la oameni 
de scos oamenii peste 100 ani 
"""