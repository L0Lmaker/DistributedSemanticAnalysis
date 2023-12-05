# Distributed System Performance Demonstration

This project demonstrates the improved performance of a distributed system compared to a centralized system. The code compares the time it takes to process documents with both systems and also includes a CLI to interact with the data.

## Getting Started

Before running the code, ensure you have Python installed on your system. This project has been tested with Python 3.
8 and above. Additionally, if you encounter any missing dependencies, install them via `pip`.

`movie-review-data` contains the article information to be processed. Add more documents to this folder to increase 
the number of documents as required.

## Running The Code

To run the code, open a terminal, navigate to the folder containing `main.py`, and execute:

```bash
python main.py
```

## How The Code Works

The `main.py` script performs the following operations:

1. Measures the runtime performance of processing 8 documents with 1 worker (a simulation of a centralized system).
2. Measures the runtime performance of processing the same 8 documents with multiple workers (a simulation of a distributed system).
3. Launches a command-line interface (CLI) to interact with the data post-processing.

## CLI Usage

Once `main.py` has completed its performance measurements, it will present a CLI with the following options:

```
1. Get Campaign Details
2. Get Campaign ID List
3. Get Article IDs for Campaign
4. Get Date List
5. Get By Date
6. Get By Article ID
7. Exit
```

To use the CLI:

- Enter the number corresponding to the action you want to perform.
- Follow the prompts to enter additional information as required (e.g., Campaign ID, Article ID, Date, etc.)
- The output will be presented directly in the terminal.
- To exit the CLI, enter `7` when prompted for a choice.

## Project Design

The project design document can be found in `project-design-document.md`. Although we haven't implemented the 
complete system, the prototype demonstrates the performance improvements of a distributed system over a centralized 
one.

## Some Items that were not implemented
1. GPT connection (to save on cost)
2. Paxos consensus (currently there is a shared KV Store)
3. Read-Repair (currently there is a shared KV Store)
