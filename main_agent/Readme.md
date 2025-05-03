# main_agent

### How to run?
You have to have a Docker on your device. Run this command to build and run the agent service:
```bash
    docker run --build
```


### Development and testing

1. You have to install poetry. It's a python package manager.

2. Install all dependencies:
```bash
    poetry install
```

3. Create and fill up the .env file:
```bash
    PORT=8000
    SEED="123456"
    ASI1_API_KEY="ASI1_KEY"
    WAVER_ADDRESS="localhost:5000" # service that able to generate .wav file 
```

4. Run the agent in dev mode: 
```bash
    ./dev_run.sh
```

5. Test the agent by test.py
```bash
    poetry run python test.py
```