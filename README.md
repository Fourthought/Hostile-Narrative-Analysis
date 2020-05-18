# Conflict Narrative Detection Pipeline - CND Pipeline
This repository is for developing a spaCy pipeline for Conflict Narrative Detection.

Guided by theories of violence from Peace Studies, this research proposes a natural language processing (NLP) spaCy pipeline to enable an idea of “Conflict Narrative Detection”. Related to this research is “Hate Speech Detection” that seeks to detect abusive language in online platforms. A 2019 review of this field by the Alan Turing Institute, however, finds, “at present, the data, tools, processes and systems needed to effectively and accurately monitor online abuse are not fully available and the field is beset with terminological,
methodological, legal and theoretical challenges” [9]. Accordingly, to address these challenges, we seek to reconceptualise Hate Speech
Detection as Conflict Narrative Detection with novel NLP pipeline.

In conceptualising Conflict Narrative Detection, we are guided by sociological theory for technological design. The defining theory we use is “cultural violence”, which seeks to explain the processes of violence legitimisation. Derived from this theorywe have developed
a novel methodology for detecting and measuring cultural violence in natural language. This methodology is then used as a structure
for the proposed NLP pipeline for which we have conducted several experiments to inform its technical development.

The methodology's objectives are as follows:

Obj 0. Pre-processing of text
Obj 1. Detect the ingroup and outgroup of an orator’s text
Obj 2. Detect and classify phrases as ingroup elevation terms.
Obj 3. Detect and classify phrases as outgroup othering terms.
Obj 4. Infer intergroup differentiation using measurement schema.

We curated a dataset comprising Hitler’s “Mein Kampf”, Martin Luther King’s “I Have a Dream” speech, and political speeches from George Bush and Osama bin Laden during the “War on Terror”. With the exception of Luther King, these texts have been used for the legitimisation of violence to bring about change, therefore, they can be regarded as culturally violent. As he sought for non-violent change, the inclusion of Luther King may provide some insight into the variables of a text that make it culturally violent. For the experimentation, this dataset is used to create test data, and since the ingroup and outgroup of each are well understood, results can be assessed by observation.

These objectives then provide a structure for the experimentation:

| Objective #   | Objective                                                 | Technology Tests                  |
| ------------- | --------------------------------------------------------- | --------------------------------- |
| Obj 0.        | Pre-processing of text                                    |                                   |
| Obj 0.1       | tokenize texts                                            | spaCy Tokenizer                   |
| Obj 0.2       | Tag texts                                                 | spaCy Tagger                      |
| Obj 0.3       | Parse texts                                               | spaCy Depedency Parse             |
| Obj 0.4       | Named Entity recognition                                  | spaCy ner                         |
| Obj 0.5       | Named Concept recognition                                 | spaCy custom attribute            |
| ------------- | --------------------------------------------------------- | --------------------------------- |
| Obj 1.        | Detect the ingroup and outgroup of an orator’s text       |                                   |
|               | Experiment 1.1 - Sentiment Analysis                       | TextBlob, IBM Watson, GoogleNLU   |
|               | Experiment 1.2 - Word Embeddings                          | Word2Vec                          |
|               | Experiment 1.3 - Hearst Patterns                          | regex, spaCy Matcher              |
| ------------- | --------------------------------------------------------- | --------------------------------- |
| Obj 2.        | Detect and classify phrases as ingroup elevation terms.   |                                   |
| ------------- | --------------------------------------------------------- | --------------------------------- |
| Obj 3.        | Detect and classify phrases as outgroup othering terms.   |                                   |
| ------------- | --------------------------------------------------------- | --------------------------------- |
| Obj 4.        | Infer intergroup differentiation using measurement schema.|                                   |
