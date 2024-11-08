# leuphana-ai-assistant

## API KEY
In ```chat/src/app.py```, you should set up your own OpenAI API Key and Langchain API Key.

```
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = "sk-"
```

## How to run 

Step 1: Start scraper container and crawling web pages.

```
docker compose up scraper
```

Step 2: Start RAG chat container 

```
docker compose up chat
```

Step 3: Start HAWKI UI container 

```
docker compose up hawki
```