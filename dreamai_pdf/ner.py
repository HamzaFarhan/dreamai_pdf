# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_ner.ipynb.

# %% auto 0
__all__ = ['load_ner_model', 'load_job_model', 'proc_ner', 'job_ner', 'edu_ner', 'work_ner', 'is_valid_jner', 'is_valid_tner']

# %% ../nbs/02_ner.ipynb 2
from .imports import *
from .core import *
from .extract import *


# %% ../nbs/02_ner.ipynb 3
def load_ner_model(model_name='tner/deberta-v3-large-ontonotes5', device='cpu'):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)
    return pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple", device=device)

def load_job_model(model_name='ismail-lucifer011/autotrain-job_all-903929564', device='cpu'):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)
    return pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple", device=device)


# def proc_ner(txt, ner, ner_dict={'institute':'', 'date':''}):
#     ner_dict = copy.deepcopy(ner_dict)
#     mapper = {'institute':['ORG', 'FAC', 'GPE', 'LOC'], 'company':['ORG', 'FAC', 'GPE', 'LOC'],
#               'role':['Job'], 'degree':['WORK_OF_ART'], 'date':['DATE']}
#     ner_dict['text'] = txt
#     for d in ner:
#         eg = d['entity_group']
#         w = ' ' + d['word'].strip()
#         for k,v in mapper.items():
#             if eg in v and ner_dict.get(k, None) is not None and '##' not in w:
#             # if eg in v and k in ner_dict and '##' not in w:
#                 ner_dict[k] = (ner_dict[k] + w).strip()
                
#                 # if eg == 'DATE':
#                 # elif len(ner_dict[k]) == 0:
#                 #     ner_dict[k] = (ner_dict[k] + w).strip()
#                 # else:
#                 #     ner_list.append(ner_dict)
#                 #     ner_dict = {k:'' for k in ner_dict.keys()}
#                 #     ner_dict['text'] = txt
                    
#     return ner_dict

def proc_ner(txt, ner, ner_dict={'institute':'', 'date':''}, thresh=3):
    ner_dict = copy.deepcopy(ner_dict)
    org_key = 'institute' if 'institute' in ner_dict else 'company'
    mapper = {'ORG':org_key, 'FAC':org_key, 'GPE':org_key, 'LOC':org_key, 'Job':'role', 'WORK_OF_ART':'degree', 'DATE':'date'}
    ner_dict['text'] = txt
    for d in ner:
        eg = d['entity_group']
        w = ' ' + d['word'].strip()
        k = mapper.get(eg, None)
        if k is not None and ner_dict.get(k, None) is not None and not w.startswith('##'):
            ner_dict[k] = (ner_dict[k] + w).strip()
    res = {k:v for k,v in ner_dict.items() if len(v) > thresh}
    if res.get(org_key, None) is None:
        return {}
    return res

def job_ner(txt, tner, jner):
    return tner(txt) + jner(txt)

def edu_ner(txt, tner, ner_dict={'institute':'', 'date':''}):
    ner = tner(txt)
    return proc_ner(txt, ner, ner_dict)

def work_ner(txt, tner, jner, ner_dict={'company':'', 'date':''}):
    ner = job_ner(txt, tner, jner)
    return proc_ner(txt, ner, ner_dict)

def is_valid_jner(ner, thresh=3):
    return ner.get('company', None) is not None
    # rc = len(ner['company'])
    # rl = len(ner.get('role', 'RANDOM ROLE'))
    # dl = len(ner.get('date', 'RANDOM DATE'))
    # return (rc > thresh) and dl > thresh# and rl > thresh

def is_valid_tner(ner, thresh=3):
    return ner.get('institute', None) is not None
    # if ner.get('institute', None) is None:
    #     return False
    # il = len(ner['institute'])
    # dl = len(ner.get('degree', 'RANDOM DEGREE'))
    # dl2 = len(ner.get('date', 'RANDOM DATE'))
    # return il > thresh and (dl > 0 or dl2 > 0)
