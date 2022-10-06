from allennlp_models.pretrained import load_predictor
 

def predictor():
    return load_predictor("coref-spanbert")

def fuckyou():
    return "fuck you"