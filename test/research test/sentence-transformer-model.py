from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

sentence = "We are looking for a backend engineer for our financial department..."
labels = {
    "Location": "Is a location mentioned?",
    "Job Title": "Is a job title mentioned?",
    "Years of Experience": "Does it mention years of experience?",
    "Industry": "Is an industry or department mentioned?",
    "Skills": "Does it mention any skills?"
}

results = []
sentence_embedding = model.encode(sentence, convert_to_tensor=True)

for label, prompt in labels.items():
    prompt_embedding = model.encode(prompt, convert_to_tensor=True)
    sim = util.cos_sim(sentence_embedding, prompt_embedding).item()
    results.append({
        "label": label,
        "containsCriteria": sim > 0.45  # 可调整阈值
    })

print(results)


import spacy
nlp = spacy.load("en_core_web_sm")

doc = nlp("We are looking for a backend engineer for our financial department...")

contains_job_title = any(ent.label_ == "JOB" or "engineer" in ent.text.lower() for ent in doc.ents)



import spacy
nlp = spacy.load("en_core_web_sm")

doc = nlp("We are looking for a backend engineer for our financial department...")

for ent in doc.ents:
    print(ent.text, ent.label_)


from InstructorEmbedding import INSTRUCTOR
from sentence_transformers import util

model = INSTRUCTOR('hkunlp/instructor-xl')  # 你也可以选 small 版

sentence = "We are looking for a backend engineer for our financial department. We hope this candidate have more than 5 years."

labels = {
    "Location": "Classify if the sentence mentions a location.",
    "Job Title": "Classify if the sentence mentions a job title.",
    "Years of Experience": "Classify if the sentence mentions years of experience.",
    "Industry": "Classify if the sentence mentions an industry or department.",
    "Skills": "Classify if the sentence mentions any skills or technologies."
}

sentence_emb = model.encode([["Classify this sentence", sentence]])
results = []

for label, instruction in labels.items():
    label_emb = model.encode([[instruction, sentence]])
    sim = util.cos_sim(sentence_emb, label_emb).item()
    results.append({
        "label": label,
        "containsCriteria": sim > 0.5  # 可以根据需要微调
    })

from pprint import pprint
pprint(results)