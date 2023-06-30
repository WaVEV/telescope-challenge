# ChatBot

docker build -t chat-bot .

docker run -it -v $(pwd)/downloads:/downloads -v $(pwd)/chromadb:/chromadb -e "OPENAI_API_KEY=<OPENAI_API_KEY>" chat-bot
