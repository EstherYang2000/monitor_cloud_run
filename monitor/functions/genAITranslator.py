#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import vertexai
from vertexai.language_models import TextGenerationModel

def interview(prompt: str):
    vertexai.init(project="tsmccareerhack2024-icsd-grp2",location="us-central1")
    parameters = {
        "temperature": 0.8,  # Temperature controls the degree of randomness in token selection.
        "max_output_tokens": 2048,  # (2048)Token limit determines the maximum amount of text output.
        "top_p": 0.8,  # (0.8)Tokens are selected from most probable to least until the sum of their probabilities equals the top_p value.
        "top_k": 20,  # (20)A top_k of 1 means the selected token is the most probable among all tokens.
    }

    model = TextGenerationModel.from_pretrained("text-bison@002")
    response = model.predict(
        prompt,
        **parameters,
    )

    return response.text
