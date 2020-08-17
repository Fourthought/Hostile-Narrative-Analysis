# Objective 1 - Detecting the Ingroup and Outgroup of a Text
In this folder are a series of experiments for determining how to detect the ingroup and outgroup of a text as part of the Hostile Narrative Analysis methodology.

The folder contains the following contents:
- Creating the Benchmark dataset
- Experiment 1.1 - Regex Hearst Patterns
- Experiment 1.2 - spaCy Hearst Patterns

The experiments begin with a regex pattern detector developed by @mmichelsonIF
- https://github.com/mmichelsonIF/hearst_patterns_python/blob/master/hearstPatterns/hearstPatterns.py

This code is refactored to create a Hearst Pattern detection pipeline component for spaCy.

The Hearst Pattern pipeline component works by adding the following custom attributes to a Token:
- is_hypernym : Boolean statement for whether a Token is a hypernym
- has_hyponyms : list of Token object for Token's hyponyms
- is_hyponym : Boolean statement for whether a Token is a hyponym
- has_hypernym : Token object for Token's hypernym

Identifying whether a Token entity is ingroup or outgroup is achieved by accessing the following property

`
    if Token._.span_type and Token._.has_hypernym:
        if Token._.has_hypernym._.ATTRIBUTE == "outgroup":
`

## Refactoring spaCy's in-built noun-chunker

In creating pipeline component, the in-built noun chunker has also been refactored to create a custom chunker document extension. 

Firstly, spaCy's in-built noun chunker works by capturing the leftward facing tokens within the dependency tree of a noun or proper noun. Only capturing the leftward facing tokens, however, misses many adpositional chunks, which are important for the dataset. For example:
- in-built chunker: weapon
- custom chunker: weapon of mass destruction

Secondly, there are many named entities the in-built chunker does now capture. For example:
- in-built chunker: "American", "people" = ""
- custom chunker: "American people" = "NORP"

Thirdly, there are a number of stop words captured in a noun chunk that also form part of a Hearst Pattern. These stop words need to be removed from the noun chunk for Hearst Pattern detection to work. For example:
- such
- particuarly

Finally, noun chunks have to be annotated with the custom attributes of CONCEPT, ATTRIBUTE, IDEOLOGY and span_type for named concept recognition. For example:
- custom chunker: "American people" => "CONCEPT" = "SOCIALGROUP" => "ATTRIBUTE" = "identity" => "IDEOLOGY" = "social"

With the new custom chunk extension, a merge custom chunk component has also been developed. The merge custom chunk component merges custom chunk Spans to a single Token while also capturing the custom attributes.

As shown with in the custom chunker notebook, this refactored noun chunk detection component yields a 44% increase in accuracy for the gold dataset. 

## Getting Started
Source code for regex pattern detection:
- https://github.com/Fourthought/CNDPipeline/blob/master/cndlib/hpregex.py

Source code for spaCy pattern detection:
- https://github.com/Fourthought/CNDPipeline/blob/master/cndlib/hpspacy.py 

Source code for custom chunker:
- https://github.com/Fourthought/CNDPipeline/blob/master/cndlib/customchunks.py


## Test Data
A number of test for each experiment have been completed.

### Creating custom chunk pipeline component
In-built chunker success rate: 50.0%
Custom chunker success rate: 94.0%
A 44.0% improvement in using the new chunker

### Creating the Benchmark dataset
Total number of named entities: 529
Total number of detectable named entities: 97
Total number of non-detectable named entities: 359

### Comparing number of detected hypernymic relations between each method for the datasets:

Orator              | regex | spaCy |
------------------- | ----- | ----- |
George Bush         | 39    | 92    |
Martin Luther King  | 22    | 53    |
Osama Bin Laden     | 29    | 71    | 

### ingroup/outgroup detection

## Authors
@fourthought

## License
This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments
Big thank you to @mmichelsonIF for the regex source code
Big thank you also to @DeNeutoy for the idea