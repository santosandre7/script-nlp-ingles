import spacy
from collections import Counter

def ler_arquivos(nomes_arquivos):
    texto_completo = []
    for nome_arquivo in nomes_arquivos:
        with open(nome_arquivo, 'r', encoding='utf-8') as file:
            texto_completo.append((file.read(), nome_arquivo))
    return texto_completo

def extrair_estruturas_e_frases(docs, verbos_filtro):
    frases_por_verbo = {}
    
    for doc, nome_arquivo in docs:
        for sentenca in doc.sents:
            frase = sentenca.text.strip()
            for token in sentenca:
                if token.pos_ == "VERB" and token.lemma_ in verbos_filtro:
                    # Estrutura de verbo com objeto direto
                    if any(filho.dep_ in ["dobj", "obj"] for filho in token.children):
                        estrutura = f"{token.lemma_} {next(filho.text for filho in token.children if filho.dep_ in ['dobj', 'obj'])}"
                        if token.lemma_ not in frases_por_verbo:
                            frases_por_verbo[token.lemma_] = set()  # Usar set para garantir frases únicas
                        frases_por_verbo[token.lemma_].add((estrutura, frase, nome_arquivo))
                    # Estrutura de sujeito e verbo
                    if any(filho.dep_ in ["nsubj", "nsubjpass"] for filho in token.children):
                        sujeito = next(filho.text for filho in token.children if filho.dep_ in ['nsubj', 'nsubjpass'])
                        estrutura = f"{sujeito} {token.lemma_}"
                        if token.lemma_ not in frases_por_verbo:
                            frases_por_verbo[token.lemma_] = set()  # Usar set para garantir frases únicas
                        frases_por_verbo[token.lemma_].add((estrutura, frase, nome_arquivo))
                    
    return frases_por_verbo

def destacar_formas_verbais(frase, verbo, doc):
    """Destaca todas as formas do verbo em uma frase."""
    frase_destacada = frase
    for token in doc:
        if token.lemma_ == verbo and token.text in frase:
            frase_destacada = frase_destacada.replace(token.text, f"<span class='highlight'>{token.text}</span>")
    return frase_destacada

def salvar_frases_mais_usadas_html(frases_por_verbo, docs, arquivo_saida):
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("<html>\n<head>\n<title>Frases mais usadas</title>\n")
        f.write("<style>\n.highlight { color: red; font-weight: bold; }\n</style>\n")
        f.write("</head>\n<body>\n")

        for verbo, frases in frases_por_verbo.items():
            # Agrupar frases por estrutura
            estruturas = Counter(estrutura for estrutura, frase, _ in frases)
            estruturas_mais_comuns = estruturas.most_common(5)
            
            f.write(f"<h2>Verbo: {verbo}</h2>\n")
            for estrutura, _ in estruturas_mais_comuns:
                f.write(f"<h3>Estrutura: {estrutura}</h3>\n")
                f.write(f"<ul>\n")
                frases_incluidas = set()  # Usar set para garantir frases únicas no HTML
                for estrutura_atual, frase, nome_arquivo in frases:
                    if estrutura_atual == estrutura and frase not in frases_incluidas:
                        # Encontrar o documento correspondente
                        doc = next(doc for doc, arquivo in docs if arquivo == nome_arquivo)
                        # Destacar todas as formas do verbo na frase
                        frase_destacada = destacar_formas_verbais(frase, verbo, doc)
                        f.write(f"<li>{frase_destacada} <em>(<b>{nome_arquivo}</b>)</em></li>\n")
                        frases_incluidas.add(frase)
                f.write(f"</ul>\n")
        
        f.write("</body>\n</html>")

# Lista de arquivos para análise
nomes_arquivos = ['episodio1.txt', 'episodio2.txt', 'episodio3.txt', 'episodio4.txt']

# Ler e combinar o texto dos arquivos
textos_e_arquivos = ler_arquivos(nomes_arquivos)

# Carregar modelo de linguagem inglês do spacy
nlp = spacy.load("en_core_web_sm")

# Processar os textos
docs = [(nlp(texto), nome_arquivo) for texto, nome_arquivo in textos_e_arquivos]

# Obter tokens e remover pontuações e stopwords
tokens = [token.text.lower() for doc, _ in docs for token in doc if token.is_alpha and not token.is_stop]

# Frequência das palavras
freq_dist = Counter(tokens)

# Identificação dos verbos, independentemente da forma
verbos = [token.lemma_ for doc, _ in docs for token in doc if token.pos_ == "VERB"]

# Frequência dos verbos
freq_verbos = Counter(verbos)

# Identificação dos verbos mais usados
verbos_mais_usados = [verbo for verbo, _ in freq_verbos.most_common(15)]

# Identificação das estruturas de frases
frases_por_verbo = extrair_estruturas_e_frases(docs, verbos_mais_usados)

# Resultados
palavras_mais_repetidas = freq_dist.most_common(100)
freq_verbos_mais_usados = freq_verbos.most_common(15)

print("Palavras mais repetidas:")
print(palavras_mais_repetidas)

print("\nVerbos mais usados:")
print(freq_verbos_mais_usados)

# Salvar as 5 frases mais utilizadas de cada verbo em um arquivo HTML
salvar_frases_mais_usadas_html(frases_por_verbo, docs, 'frases_mais_usadas_v4.html')

print("Frases mais usadas foram salvas em 'frases_mais_usadas.html'")
