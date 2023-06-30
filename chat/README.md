# QA Bot

This mini project focuses on the creation of a QA bot that retrieves data from Google Drive. The bot utilizes the New York Times articles, which are part of the Socially-Informed Timeline Generation Corpus (first released in March 2015).

## Process Description

The project utilizes prompt engineering as the technique to generate queries while providing relevant articles as context to a Language Model (LLM). This enables the LLM to answer queries based on the information in the articles. Due to resource limitations, it is not feasible to provide all the documents as context simultaneously.

### Download from Drive

To download data from Google Drive, the project utilizes the `googleapiclient` library. An application was created in the Google Cloud console, and a service account was set up to use the SDK.

### Document Retrieval (Contexts)

To retrieve the most relevant document, both the query and the documents undergo vectorization. The nearest articles are then selected based on cosine similarity.

### QA with Context

The query and the context are added to the prompt, and the answer is read from the model.

## Execution

To simplify the execution process, a Dockerfile is provided to build and run the QA bot.

To build the Docker image, use the following command:

```bash
docker build -t chat-bot .
```


To run the QA bot, execute the following command in your terminal:

```bash
docker run -it -v <dirname_download>/downloads:/downloads -v <dirname_db>/chromadb:/chromadb -e "OPENAI_API_KEY=<OPENAI_API_KEY>" chat-bot
```


Notes:
- `<dirname_download>` refers to the directory where the articles will be stored.
- `<dirname_db>` refers to the directory where the vectorized articles will be stored.
- `<OPENAI_API_KEY>` is the OpenAI token.


### Considerations

In this project, Langchain, a language modeling framework, was utilized along with specific models provided by OpenAI. The project also involves a service account that facilitates the data download from Google Drive. However, only a small portion of the Socially-Informed Timeline Generation Corpus dataset was tokenized for this project. To make these documents accessible for downloading by the service account user, they were uploaded to my personal Google Drive.
