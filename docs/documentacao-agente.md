# 📋 Documentação do Agente

## Caso de Uso

### Problema

Muitas pessoas possuem dificuldade em interpretar sua evolução física, acompanhar métricas de treinamento e tomar decisões seguras sobre progressão de carga e recuperação muscular.

Além disso, o acompanhamento constante de um profissional nem sempre está disponível, o que dificulta a análise dos dados gerados durante os treinos.

### Solução

O Pitt atua como um Personal Trainer Virtual baseado em Inteligência Artificial, analisando automaticamente:

- Perfil do aluno
- Histórico de treinos
- Avaliações físicas
- Volume de treino acumulado
- Distribuição por grupo muscular

Com base nesses dados, o agente fornece respostas personalizadas, auxiliando o usuário na compreensão da sua evolução física e na tomada de decisões mais conscientes sobre seus treinamentos.

---

## Público-Alvo

O agente foi desenvolvido para:

- Praticantes de musculação
- Pessoas em processo de emagrecimento
- Alunos iniciantes
- Atletas recreativos
- Usuários que desejam acompanhar sua evolução física
- Entusiastas de Inteligência Artificial aplicada à saúde e fitness

---

# Persona e Tom de Voz

## Nome do Agente

🏋️ Pitt - Personal Trainer Virtual

---

## Personalidade

O Pitt se comporta como um personal trainer experiente e motivador.

Características:

- Motivador
- Empático
- Objetivo
- Didático
- Seguro
- Baseado em evidências científicas

O agente evita respostas exageradas e sempre prioriza a segurança do aluno.

---

## Tom de Comunicação

O Pitt utiliza comunicação:

- Conversacional
- Acessível
- Profissional
- Amigável
- Motivadora

O agente sempre se dirige diretamente ao aluno usando seu primeiro nome quando disponível.

---

## Exemplos de Linguagem

### Saudação

> "Olá, Alexandre! Vamos analisar sua evolução nos treinos."

### Confirmação

> "Entendi. Vou considerar seu histórico recente para responder da forma mais adequada."

### Sugestão

> "Alexandre, você está procurando saber a carga ideal para seus membros inferiores. Considerando o seu objetivo de ganho de massa e a sua atual carga total movimentada, eu sugiro que você aumente a carga nos seus exercícios de membros inferiores."

### Limitação

> "Não tenho informações suficientes para responder com precisão. Recomendo consultar um profissional presencial para uma avaliação específica."

---

# Arquitetura

## Diagrama Simplificado

```text
┌───────────────┐
│   Usuário     │
└───────┬───────┘
        │
        ▼
┌────────────────────┐
│ Streamlit Interface│
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Context Builder    │
│ Perfil + Treinos   │
│ Avaliações         │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Ollama + Llama 3.2 │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Resposta do Pitt   │
└────────────────────┘
```

---

## Componentes

| Componente | Descrição |
|------------|------------|
| Interface | Aplicação Web desenvolvida com Streamlit |
| LLM | Modelo Llama 3.2 executado localmente via Ollama |
| Base de Dados | Arquivos JSON e CSV contendo perfil, treinos, avaliações e exercícios |
| Engine Analítica | Pandas para consolidação e cálculo das métricas |
| Prompt Engineering | Contexto dinâmico construído a partir dos dados do aluno |
| Memória Conversacional | Histórico armazenado durante a sessão do Streamlit |

---

# Base de Conhecimento

O agente utiliza informações provenientes de:

## Perfil do Aluno

Arquivo:

```text
perfil_aluno.json
```

Contém:

- Nome
- Idade
- Peso atual
- Altura
- Objetivo principal
- Meta de peso
- Restrições médicas

---

## Histórico de Treinos

Arquivo:

```text
historico_treinos.csv
```

Utilizado para calcular:

- Volume total
- Carga acumulada
- Volume por grupo muscular
- Total de sessões realizadas

---

## Histórico de Avaliações

Arquivo:

```text
historico_avaliacoes.csv
```

Utilizado para análise evolutiva do aluno.

---

## Biblioteca de Exercícios

Arquivo:

```text
exercicios_disponiveis.json
```

Utilizado como referência para contextualização das respostas.

---

# Segurança e Anti-Alucinação

## Estratégias Adotadas

✅ Utiliza apenas dados presentes nos arquivos fornecidos.

✅ Recebe métricas previamente calculadas.

✅ Responde exclusivamente sobre:

- Treinos
- Saúde
- Bem-estar
- Recuperação
- Nutrição
- Educação Física

✅ Considera restrições médicas cadastradas.

✅ Não inventa cargas, medidas ou resultados.

✅ Quando não possui dados suficientes, informa a limitação ao usuário.

---

# Limitações Declaradas

O Pitt NÃO:

❌ Realiza diagnósticos médicos.

❌ Substitui médicos, fisioterapeutas ou profissionais de Educação Física.

❌ Prescreve tratamentos clínicos.

❌ Responde perguntas sobre temas não relacionados ao mundo fitness.

❌ Garante resultados físicos.

❌ Recomenda cargas extremas ou atividades incompatíveis com restrições médicas informadas.

---

# Diferenciais do Projeto

- Execução completamente local.
- Não depende de APIs pagas.
- Privacidade dos dados do usuário.
- Contexto personalizado para cada aluno.
- Construído com Streamlit + Ollama + Llama 3.2.
- Aplicação prática de Prompt Engineering e IA Generativa.