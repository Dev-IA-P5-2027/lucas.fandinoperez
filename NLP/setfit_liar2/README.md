---
tags:
- setfit
- sentence-transformers
- text-classification
- generated_from_setfit_trainer
widget:
- text: Scores of politicians and others are on a "list" of sex cases from newly unsealed
    Ghislaine Maxwell court documents.
- text: We are only inches away from ceasing to be a free market economy.
- text: My campaign alone has created more jobs in the state of Rhode Island than
    Narragansett Beer.
- text: Says Sen. Kay Hagan "has missed half of the (Senate Armed Services) Committee's
    hearings in 2014.
- text: Says Democratic leaders aren't wearing masks or social distancing in private
metrics:
- accuracy
- precision
- recall
- f1
pipeline_tag: text-classification
library_name: setfit
inference: true
base_model: sentence-transformers/paraphrase-mpnet-base-v2
model-index:
- name: SetFit with sentence-transformers/paraphrase-mpnet-base-v2
  results:
  - task:
      type: text-classification
      name: Text Classification
    dataset:
      name: Unknown
      type: unknown
      split: test
    metrics:
    - type: accuracy
      value: 0.592
      name: Accuracy
    - type: precision
      value: 0.6105
      name: Precision
    - type: recall
      value: 0.592
      name: Recall
    - type: f1
      value: 0.592
      name: F1
---

# SetFit with sentence-transformers/paraphrase-mpnet-base-v2

This is a [SetFit](https://github.com/huggingface/setfit) model that can be used for Text Classification. This SetFit model uses [sentence-transformers/paraphrase-mpnet-base-v2](https://huggingface.co/sentence-transformers/paraphrase-mpnet-base-v2) as the Sentence Transformer embedding model. A [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) instance is used for classification.

The model has been trained using an efficient few-shot learning technique that involves:

1. Fine-tuning a [Sentence Transformer](https://www.sbert.net) with contrastive learning.
2. Training a classification head with features from the fine-tuned Sentence Transformer.

## Model Details

### Model Description
- **Model Type:** SetFit
- **Sentence Transformer body:** [sentence-transformers/paraphrase-mpnet-base-v2](https://huggingface.co/sentence-transformers/paraphrase-mpnet-base-v2)
- **Classification head:** a [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) instance
- **Maximum Sequence Length:** 512 tokens
- **Number of Classes:** 2 classes
<!-- - **Training Dataset:** [Unknown](https://huggingface.co/datasets/unknown) -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Repository:** [SetFit on GitHub](https://github.com/huggingface/setfit)
- **Paper:** [Efficient Few-Shot Learning Without Prompts](https://arxiv.org/abs/2209.11055)
- **Blogpost:** [SetFit: Efficient Few-Shot Learning Without Prompts](https://huggingface.co/blog/setfit)

### Model Labels
| Label | Examples                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|:------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0     | <ul><li>'In the past, President Obama has refused to meet with representatives from Cuban exile organizations.'</li><li>'Says a photo shows a "lithium mine for hybrid cars.'</li><li>'Says North Carolina bill "would allow politically active 501(c)(4) organizations to hide major donors while using their money to support or oppose candidates and political issues.'</li></ul>                                                                                                                                                                              |
| 1     | <ul><li>'Top U.S. intelligence officials have told\xa0"every member of Congress, including the president, we\'re about to be attacked in a serious way because (of) the threat emanating from Syria and Iraq.'</li><li>'Says Gov. Scott Walker\'s proposed reduction in university spending is "about the size of the one" under Democratic Gov. Jim Doyle, but Democrats didn\'t treat Doyle\'s cut as so dire.'</li><li>'91 percent of Latinos support the DREAM Act, which allows undocumented youth to attend college," but Marco Rubio opposes it.'</li></ul> |

## Evaluation

### Metrics
| Label   | Accuracy | Precision | Recall | F1    |
|:--------|:---------|:----------|:-------|:------|
| **all** | 0.592    | 0.6105    | 0.592  | 0.592 |

## Uses

### Direct Use for Inference

First install the SetFit library:

```bash
pip install setfit
```

Then you can load this model and run inference.

```python
from setfit import SetFitModel

# Download from the 🤗 Hub
model = SetFitModel.from_pretrained("setfit_model_id")
# Run inference
preds = model("We are only inches away from ceasing to be a free market economy.")
```

<!--
### Downstream Use

*List how someone could finetune this model on their own dataset.*
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Set Metrics
| Training set | Min | Median | Max |
|:-------------|:----|:-------|:----|
| Word count   | 10  | 20.0   | 31  |

| Label | Training Sample Count |
|:------|:----------------------|
| 0     | 8                     |
| 1     | 8                     |

### Training Hyperparameters
- batch_size: (16, 16)
- num_epochs: (2, 2)
- max_steps: -1
- sampling_strategy: oversampling
- body_learning_rate: (2e-05, 1e-05)
- head_learning_rate: 0.01
- loss: CosineSimilarityLoss
- distance_metric: cosine_distance
- margin: 0.25
- end_to_end: False
- use_amp: False
- warmup_proportion: 0.1
- l2_weight: 0.01
- seed: 42
- eval_max_steps: -1
- load_best_model_at_end: True

### Training Results
| Epoch  | Step | Training Loss | Validation Loss |
|:------:|:----:|:-------------:|:---------------:|
| 0.1111 | 1    | 0.4434        | -               |
| 1.0    | 9    | -             | 0.2677          |
| 2.0    | 18   | -             | 0.2658          |

### Framework Versions
- Python: 3.13.3
- SetFit: 1.1.3
- Sentence Transformers: 5.5.1
- Transformers: 4.57.6
- PyTorch: 2.12.0
- Datasets: 5.0.0
- Tokenizers: 0.22.2

## Citation

### BibTeX
```bibtex
@article{https://doi.org/10.48550/arxiv.2209.11055,
    doi = {10.48550/ARXIV.2209.11055},
    url = {https://arxiv.org/abs/2209.11055},
    author = {Tunstall, Lewis and Reimers, Nils and Jo, Unso Eun Seo and Bates, Luke and Korat, Daniel and Wasserblat, Moshe and Pereg, Oren},
    keywords = {Computation and Language (cs.CL), FOS: Computer and information sciences, FOS: Computer and information sciences},
    title = {Efficient Few-Shot Learning Without Prompts},
    publisher = {arXiv},
    year = {2022},
    copyright = {Creative Commons Attribution 4.0 International}
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->