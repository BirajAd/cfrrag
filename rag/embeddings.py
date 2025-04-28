import google.generativeai as genai
import numpy as np
import pandas as pd
import textwrap
from typing import Tuple

def embed_text(text, title, model="models/text-embedding-004"):
  """
    Embeds text with given title using provided model
  """
  return genai.embed_content(model=model,
    content=text,
    task_type="retrieval_document",
    title=title
  ).get("embedding")

def find_relevant_row(query, df, model="models/text-embedding-004"):
  """
    finds the top most relevant row from dataframe based on the query
  """
  query_embedding = genai.embed_content(
    model=model,
    content=query,
    task_type="retrieval_query"
  ).get("embedding")

  dot_products = np.dot(np.stack(df["embeddings"]), query_embedding)
  idx = np.argmax(dot_products)

  return df.iloc[idx]

def all_texts_under_section(df, section_number):
  """
    Returns the concatenated content string that belong to the same section_number
  """
  return df[df["section_number"] == section_number].content_text.str.cat(sep="")

def create_prompt(query, relevant_passage):
  prompt = textwrap.dedent(f"""You are a helpful and informative bot that answers questions using text from the reference context included below. \
  Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
  However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
  strike a friendly and converstional tone. \
  If the passage is irrelevant to the answer, you may ignore it.
  QUESTION: '{query}'
  CONTEXT: '{relevant_passage}'

  ANSWER:
  """)

  return prompt

def answer_question(
  query: str,
  df: pd.DataFrame
) -> Tuple[pd.Series, str, str]:
  """
  Retrieve an answer for a user’s question from a DataFrame.

  Args:
    query (str): The user’s question.
    df (pd.DataFrame): DataFrame containing all documents and metadata.

  Returns:
    source (pd.Series): The DataFrame row used as the source for the answer.
    passage (str): The text passage passed to the model.
    answer (str): The model’s response to the query.
  """
  source = find_relevant_row(query, df)
  section_number = source.section_number

  passage = all_texts_under_section(df, section_number)

  model = genai.GenerativeModel("models/gemini-2.0-flash")

  prompt = create_prompt(query, passage)

  answer = model.generate_content(prompt)

  return source, passage, answer.text