# Conflict Narrative Detection Pipeline - CND Pipeline

Guided by theories of violence from Peace Studies, this PhD research proposes a natural language processing (NLP) spaCy pipeline to enable an idea of “Conflict Narrative Detection”.

In conceptualising Conflict Narrative Detection, we are guided by sociological theory for technological design. The defining theory we use is “cultural violence”, which seeks to explain the processes of violence legitimisation. Derived from this theory, we have developed a novel methodology for detecting and measuring cultural violence in natural language. This methodology provides a structure for the proposed NLP pipeline for which we have conducted several experiments to inform its technical development.

The methodology and experimentation are structured are as follows (to be updated as the research develops):

| Objective #   | Objective                                                 | Technology Tests                  |
| ------------- | --------------------------------------------------------- | --------------------------------- |
| Obj 0.        | Pre-processing of text                                    |                                   |
| Obj 0.1       | tokenize texts                                            | spaCy Tokenizer                   |
| Obj 0.2       | Tag texts                                                 | spaCy Tagger                      |
| Obj 0.3       | Parse texts                                               | spaCy Depedency Parse             |
| Obj 0.4       | Experiment 0.1 - Named Entity recognition                 | spaCy ner                         |
| Obj 0.5       | Experiment 0.2 - Named Concept recognition                | spaCy custom component            |
| Obj 0.6       | Experiment 0.3 - Entity Resolution                        | Custom component                  |
| Obj 0.7       | Experiment 0.4 - Coreference Resolution                   | Hugging Face coref                |
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
| ------------- | --------------------------------------------------------- | --------------------------------- |

For developing the pipeline, we curated a dataset comprising Hitler’s “Mein Kampf”, Martin Luther King’s “I Have a Dream”, and political speeches from George Bush and Osama bin Laden during the “War on Terror”. Except for Luther King, these texts have been used for the legitimisation of violence to bring about change, therefore, they should be regarded as culturally violent. As he sought for non-violent change, the inclusion of Luther King as a control to the other speeches may provide some insight into the variables of a text that make it culturally violent. Since the ingroup and outgroup of each text are well understood, this dataset is a good source of test data since results can be assessed by observation.

This research is funded by the Engineering and Physical Sciences Research Council (EPSCR) through the Web Science Doctoral Training Centre (DTC) at Southampton University. Supervisors:
- Dr George Konstantinidis
- Dr Craig Webber

In developing this pipeline big thanks go to:
- Mark Neumann
- mmichelsonIF
- especially the excellent explosion.ai team for creating the spaCy library without which none of this would be possible.

I have only been coding for 18 months; any suggestions, comments or feedback are very welcome.
