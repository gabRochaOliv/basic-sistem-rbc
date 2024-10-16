import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2
import json


def load_value_map():
    with open('arq.json', 'r', encoding='utf-8') as f:
        return json.load(f)

value_map = load_value_map()

def get_cases_from_db():
    conn = psycopg2.connect(
        host="localhost",
        database="SistemaRBC_Soja",
        user="postgres",
        password="082130"
    )
    cur = conn.cursor()

    cur.execute("SELECT * FROM casos")
    rows = cur.fetchall()

    cases = []
    for row in rows:
        case = {}
        for idx, col_name in enumerate(cur.description):
            attribute = col_name[0]
            case[attribute] = row[idx]
        cases.append(case)

    cur.close()
    conn.close()

    return cases

#Conversor
def convert_db_value(attribute, value):
    if attribute in value_map and value in value_map[attribute]:
        return value_map[attribute][value]
    else:
        return 0 

weights = {
    "date": 2,
    "plant_stand": 5,
    "precip": 6,
    "temp_": 4,
    "hail": 3,
    "crop_hist": 1,
    "area_damaged": 3,
    "severity": 3,
    "seed_tmt": 1,
    "germination": 1,
    "plant_growth": 8,
    "leaves": 8,
    "leafspots_halo": 6,
    "leafspot_marg": 7, 
    "leafspot_size": 7,
    "leaf_sheath_red": 7, 
    "leaf_malf": 7,
    "leaf_mild": 8,
    "stem": 8,
    "lodging": 6,
    "steam_cankers": 7,  
    "canker_lesion": 7,
    "fruiting_bodies": 7,
    "external_decay": 7,  
    "mycelium": 8,
    "int_discolor": 8,
    "sclerotia": 8,
    "fruit_pods": 8,  
    "fruit_spots": 7,  
    "seed": 7,
    "mold_growth": 8,
    "seed_discolor": 7,
    "seed_size": 8,
    "shriveling": 8,
    "roots": 8
}


def calculate_local_similarity(case_value, new_value):
    case_value = safe_int_conversion(case_value)
    new_value = safe_int_conversion(new_value)

    if case_value == 0 and new_value == 0:
        return 1.0
    return 1 - (abs(case_value - new_value) / max(case_value, new_value)) if max(case_value, new_value) != 0 else 1

def safe_int_conversion(value):
    try:
        return int(value)
    except ValueError:
        return 0


def calculate_global_similarity(db_cases, new_case):
    similarities = []
    for db_case in db_cases:
        local_similarities = []
        weighted_similarities = 0 
        total_weight = 0 

        for attr in new_case.keys():
            
            db_value_converted = convert_db_value(attr, db_case[attr])
            new_value_converted = convert_db_value(attr, new_case[attr])

            local_similarity = calculate_local_similarity(db_value_converted, new_value_converted)
            weight = weights.get(attr, 1)  

            weighted_similarities += local_similarity * weight
            total_weight += weight
        
        global_similarity = weighted_similarities / total_weight if total_weight > 0 else 0
        similarities.append(global_similarity)

    return similarities

def rbc_system(new_case, min_similarity):
    db_cases = get_cases_from_db()
    similarities = calculate_global_similarity(db_cases, new_case)

    similar_cases = []
    for i, similarity in enumerate(similarities):
        if similarity >= min_similarity / 100:  
            similar_cases.append((db_cases[i]['objetivo'], similarity))
    

    similar_cases.sort(key=lambda x: x[1], reverse=True)

    if similar_cases:
        return similar_cases
    else:
        return "Nenhum caso com a similaridade desejada encontrado."
    

def salvar_no_banco(dados_entrada, objetivo):
    try:
        conn = psycopg2.connect(
             host="localhost",
            database="SistemaRBC_Soja",
            user="postgres",
            password="082130",      
            port="5432"              
        )
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO casos (
                date, plant_stand, precip, temp_, hail, crop_hist,
                area_damaged, severity, seed_tmt, germination,
                plant_growth, leaves, leafspots_halo, leafspot_marg,
                leafspot_size, leaf_sheath_red, leaf_malf, leaf_mild,
                stem, lodging, steam_cankers, canker_lesion,
                fruiting_bodies, external_decay, mycelium,
                int_discolor, sclerotia, fruit_pods, fruit_spots,
                seed, mold_growth, seed_discolor, seed_size,
                shriveling, roots, objetivo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            dados_entrada.get('date'),
            dados_entrada.get('plant_stand'),
            dados_entrada.get('precip'),
            dados_entrada.get('temp_'),
            dados_entrada.get('hail'),
            dados_entrada.get('crop_hist'),
            dados_entrada.get('area_damaged'),
            dados_entrada.get('severity'),
            dados_entrada.get('seed_tmt'),
            dados_entrada.get('germination'),
            dados_entrada.get('plant_growth'),
            dados_entrada.get('leaves'),
            dados_entrada.get('leafspots_halo'),
            dados_entrada.get('leafspot_marg'),
            dados_entrada.get('leafspot_size'),
            dados_entrada.get('leaf_sheath_red'),
            dados_entrada.get('leaf_malf'),
            dados_entrada.get('leaf_mild'),
            dados_entrada.get('stem'),
            dados_entrada.get('lodging'),
            dados_entrada.get('steam_cankers'),
            dados_entrada.get('canker_lesion'),
            dados_entrada.get('fruiting_bodies'),
            dados_entrada.get('external_decay'),
            dados_entrada.get('mycelium'),
            dados_entrada.get('int_discolor'),
            dados_entrada.get('sclerotia'),
            dados_entrada.get('fruit_pods'),
            dados_entrada.get('fruit_spots'),
            dados_entrada.get('seed'),
            dados_entrada.get('mold_growth'),
            dados_entrada.get('seed_discolor'),
            dados_entrada.get('seed_size'),
            dados_entrada.get('shriveling'),
            dados_entrada.get('roots'),
            objetivo 
        ))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"Dados salvos no banco de dados: {dados_entrada} => {objetivo}")
        return True

    except Exception as e:
        print(f"Erro ao salvar no banco de dados: {e}")
        return False
    
    
def abrir_comparacao(caso_escolhido, dados_entrada):
    comparacao_window = tk.Toplevel()
    comparacao_window.title("Comparar Casos")
    
    comparacao_frame = tk.Frame(comparacao_window)
    comparacao_frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(comparacao_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    comparacao_canvas = tk.Canvas(comparacao_frame, yscrollcommand=scrollbar.set)
    comparacao_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=comparacao_canvas.yview)

    comparacao_interior = tk.Frame(comparacao_canvas)

    tk.Label(comparacao_interior, text="Atributo", font=('bold', 12)).grid(row=0, column=0, padx=10, pady=5)
    tk.Label(comparacao_interior, text="Entradas do Usuário", font=('bold', 12)).grid(row=0, column=1, padx=10, pady=5)
    tk.Label(comparacao_interior, text="Caso Selecionado", font=('bold', 12)).grid(row=0, column=2, padx=10, pady=5)
    
    for index, (atributo, valor_usuario) in enumerate(dados_entrada.items(), start=1):
        valor_caso = caso_escolhido.get(atributo, "Desconhecido")
        
        tk.Label(comparacao_interior, text=atributo.capitalize()).grid(row=index, column=0, padx=10, pady=5)
        tk.Label(comparacao_interior, text=valor_usuario).grid(row=index, column=1, padx=10, pady=5)
        tk.Label(comparacao_interior, text=valor_caso).grid(row=index, column=2, padx=10, pady=5)

    comparacao_canvas.create_window((0, 0), window=comparacao_interior, anchor="nw")
    comparacao_interior.update_idletasks()
    comparacao_canvas.config(scrollregion=comparacao_canvas.bbox("all"))

    inferir_button = tk.Button(comparacao_interior, text="Inferir", bg="lightgreen",command=lambda: inferir(caso_escolhido['objetivo'], dados_entrada))
    inferir_button.grid(row=row + 6, column=5, columnspan=2, pady=20)
  

def inferir(objetivo, dados_entrada):
    salvar_no_banco(dados_entrada, objetivo)
    messagebox.showinfo("Sucesso", f"Dados inferidos e salvos para: {objetivo}")

def exibir_resultados(resultados, dados_entrada):
    resultados_window = tk.Toplevel()
    resultados_window.title("Resultados")

    resultados_frame = tk.Frame(resultados_window)
    resultados_frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(resultados_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    resultados_canvas = tk.Canvas(resultados_frame, yscrollcommand=scrollbar.set)
    resultados_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
 
    scrollbar.config(command=resultados_canvas.yview)

    resultados_interior = tk.Frame(resultados_canvas)

    if isinstance(resultados, list):
        for index, resultado in enumerate(resultados, start=1):
            objetivo, similaridade = resultado
            
            tk.Label(resultados_interior, text=objetivo).grid(row=index, column=0, padx=5, pady=5)
            tk.Label(resultados_interior, text=f"{similaridade:.2f}").grid(row=index, column=1, padx=5, pady=5)
            
            comparar_button = tk.Button(resultados_interior, text="Comparar", bg="lightblue", 
                                        command=lambda idx=index-1: abrir_comparacao(get_cases_from_db()[idx], dados_entrada))
            comparar_button.grid(row=index, column=2, padx=5, pady=5)
    else:
        tk.Label(resultados_interior, text=resultados).grid(row=0, column=0, padx=5, pady=5)
        
    resultados_canvas.create_window((0, 0), window=resultados_interior, anchor="nw")

    resultados_interior.update_idletasks()
    resultados_canvas.config(scrollregion=resultados_canvas.bbox("all"))


def submit_form():
    nova_entrada = {key: var.get() for key, var in vars_dict.items()}
    
    try:
        min_similarity = float(similarity_entry.get())
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira um número válido para o grau de similaridade.")
        return
    
    resultado = rbc_system(nova_entrada, min_similarity)
    exibir_resultados(resultado, nova_entrada)


root = tk.Tk()
root.title("Sistema RBC")
root.geometry("800x600")


main_frame = ttk.Frame(root, padding="10 10 20 20")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

vars_dict = {
    "date": tk.StringVar(),
    "plant_stand": tk.StringVar(),
    "precip": tk.StringVar(),
    "temp_": tk.StringVar(),
    "hail": tk.StringVar(),
    "crop_hist": tk.StringVar(),
    "area_damaged": tk.StringVar(),
    "severity": tk.StringVar(),
    "seed_tmt": tk.StringVar(),
    "germination": tk.StringVar(),
    "plant_growth": tk.StringVar(),
    "leaves": tk.StringVar(),
    "leafspots_halo": tk.StringVar(),
    "leafspot_marg": tk.StringVar(),  
    "leafspot_size": tk.StringVar(),
    "leaf_sheath_red": tk.StringVar(), 
    "leaf_malf": tk.StringVar(),
    "leaf_mild": tk.StringVar(),
    "stem": tk.StringVar(),
    "lodging": tk.StringVar(),
    "steam_cankers": tk.StringVar(),  
    "canker_lesion": tk.StringVar(),
    "fruiting_bodies": tk.StringVar(),
    "external_decay": tk.StringVar(), 
    "mycelium": tk.StringVar(),
    "int_discolor": tk.StringVar(),
    "sclerotia": tk.StringVar(),
    "fruit_pods": tk.StringVar(), 
    "fruit_spots": tk.StringVar(),  
    "seed": tk.StringVar(),
    "mold_growth": tk.StringVar(),
    "seed_discolor": tk.StringVar(),
    "seed_size": tk.StringVar(),
    "shriveling": tk.StringVar(),
    "roots": tk.StringVar()
}

attribute_options = {
    "date": ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
    "plant_stand": ["Normal", "lt-normal", "Desconhecido"],
    "precip": ["gt-normal", "lt-normal", "normal", "Desconhecido"],
    "temp_": ["normal", "lt-normal", "normal gt", "Desconhecido"],
    "hail": ["Sim", "Não", "Desconhecido"],
    "crop_hist": ["dif-1º ano", "mesmo primeiro ano", "mesmo-último-dois anos", "mesmo-lst-sev-anos", "Desconhecido"],
    "area_damaged": ["áreas baixas", "espalhado", "campo inteiro", "áreas superiores", "Desconhecido"],
    "severity": ["Menor", "forte", "pode-severo", "Desconhecido"],
    "seed_tmt": ["nenhuma", "fungicida", "Outros", "Desconhecido"],
    "germination": ["90-100%", "80-89%", "lt-80%", "Desconhecido"],
    "plant_growth": ["normal", "Anormal", "Desconhecido"],
    "leaves": ["normal", "Anormal", "Desconhecido"],
    "leafspots_halo": ["ausente", "sem halos amarelos", "halos amarelos", "Desconhecido"],
    "leafspot_marg": ["no-w-s-marg", "w-s-marg", "dna", "Desconhecido"],
    "leafspot_size": ["lt-1/8", "gt-1/8", "dna", "Desconhecido"],
    "leaf_sheath_red": ["ausente", "Presente", "Desconhecido"], 
    "leaf_malf": ["Ausente", "Presente", "Desconhecido"],
    "leaf_mild": ["Ausente", "Surf mais baixo", "Surf superior", "Desconhecido"],
    "stem": ["normal", "Anormal", "Desconhecido"],
    "lodging": ["Sim", "Não", "Desconhecido"],
    "steam_cankers": ["Ausente", "abaixo do solo", "Acima do solo", "Acima-sec-nde", "Desconhecido"],
    "canker_lesion": ["bronzeado", "Marrom", "dna", "dk-marrom-preto", "Desconhecido"],
    "fruiting_bodies": ["Ausente", "Presente", "Desconhecido"],
    "external_decay": ["firme e seco", "Ausente", "Desconhecido"],
    "mycelium": ["Ausente", "Presente", "Desconhecido"],
    "int_discolor": ["Nenhuma", "Marrom", "Preto", "Desconhecido"],
    "sclerotia": ["Ausente", "Presente", "Desconhecido"],
    "fruit_pods": ["normal", "poucos presentes", "Doente", "dna", "Desconhecido"],
    "fruit_spots": ["Ausente", "Colorido", "Marrom com manchas pretas", "dna", "Desconhecido"],
    "seed": ["normal", "Anormal", "Desconhecido"],
    "mold_growth": ["Ausente", "Presente", "Desconhecido"],
    "seed_discolor": ["Ausente", "Presente", "Desconhecido"],
    "seed_size": ["normal", "lt-normal", "Desconhecido"],
    "shriveling": ["Ausente", "Presente", "Desconhecido"],
    "roots": ["normal", "Apodrecido", "cistos de vesícula", "Desconhecido"]
}

#Interface

column = 0
row = 0
for label_text, options in attribute_options.items():

    label = tk.Label(main_frame, text=label_text.capitalize())
    label.grid(row=row, column=column*2, padx=10, pady=5, sticky="w")
    
    dropdown = ttk.OptionMenu(main_frame, vars_dict[label_text], options[0], *options)
    dropdown.grid(row=row, column=column*2 + 1, padx=10, pady=5, sticky="w")
    
    row += 1
    if row >= 10: 
        row = 0
        column += 1
row += 4


similarity_label = tk.Label(main_frame, text="Grau de Similaridade (%)")
similarity_label.grid(row=row + 1, column=0, padx=10, pady=5, sticky="w")
similarity_entry = ttk.Entry(main_frame)
similarity_entry.grid(row=row + 1, column=1, padx=10, pady=5, sticky="w")


submit_button = tk.Button(main_frame, text="Submeter", command=submit_form)
submit_button.grid(row=row + 6, column=1, columnspan=2, pady=20)

root.mainloop()