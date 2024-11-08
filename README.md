# leuphana-ai-assistant

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