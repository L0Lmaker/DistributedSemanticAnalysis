# Word Crunching: Distributed Semantic Analysis/Monitoring System Design Document

## Table of Contents

- [Introduction](#introduction)
- [System Architecture](#system-architecture)
- [Node Design](#node-design)
- [Networking and Communication](#networking-and-communication)
- [Load Balancing Strategy](#load-balancing-strategy)
- [Storage and Log Management](#storage-and-log-management)
- [Metadata Extraction](#metadata-extraction)
- [API Endpoints](#api-endpoints)
- [Performance Benchmarking](#performance-benchmarking)
- [Future Considerations](#future-considerations)
- [Story Point Estimation](#story-point-estimation)

## Introduction

If I were to ask you a question, "What is the public perception of company X through 2023?" and gave you a related set
of Articles, Social Media Posts, and YouTube video transcripts (published in 2023), how would we go about answering that
question?

## Background and Related Work
The paper [1] highlights the significance of semantic analysis in extracting meaning from language structures and discusses the challenges of using large-scale data. It introduces Distributed Semantic Analysis (DSA), a novel model that combines distributed computing with semantic analysis, addressing scalability issues. Most of the times, the scalability issues are solved by using distributed systems. Some of the ways in which distributed systems can help solve scalability challenges are as follows:

    1. Parallelism and Load Balancing: Distributed systems enable parallel processing, where tasks are divided among multiple nodes, allowing them to be executed simultaneously. This helps in distributing the workload and increasing overall system performance. Distributing the incoming workload evenly across multiple nodes ensures that no single node becomes a bottleneck. Load balancing algorithms help in optimizing resource utilization and maintaining system responsiveness.

    2. Data Partitioning: Distributing data across multiple nodes prevents any single node from becoming a bottleneck for data access. Various partitioning strategies, such as sharding, help in dividing the data into smaller subsets. Physically partitioning and distributing the Web across millions of servers enables efficient handling of a vast number of documents, contributing to the scalability of the World Wide Web [2].
    
    3. Data Replication: Replicating data across multiple nodes ensures fault tolerance and improved read performance. This way, if one node fails, the data can still be accessed from other replicas. Improves system availability, balances the load between components, and enhances overall performance [2].

    4. Caching: Caching frequently accessed data in distributed systems can significantly reduce the load on the backend servers. Caching results in making a copy of a resource, generally in the proximity of the client accessing that resource [2].

    5. Fault Tolerance: Distributed systems often incorporate redundancy and replication to ensure fault tolerance. If a node fails, another node can take over its responsibilities, minimizing the impact on the overall system.

After solving the scalability issues of a system, the next step is to design the distributed system. The solution of paper [3] is based on the Replicated Worker Paradigm, utilizing dynamically created tasks during the execution of the master/coordinator process. Replicated workers, identical on each machine and assigned to separate physical processors, enable parallel decomposition of processing operations, enhancing fault tolerance. The architecture includes distributed work pools controlling task allocation to workers, with each work pool representing a collection of tasks awaiting execution by a single worker. Workers register to the master, await task assignments, and, upon completion, send results back to the master while retrieving new tasks from their work pools. The master signals worker termination after completing all tasks in the input folder. Communication relies on message queues for an event-driven approach, utilizing Apache's ActiveMQ message broker. Load balancing is ensured by the master assigning new tasks to workers as they become available, following a First Come First Served (FCFS) strategy. The solution is optimized not only for distributed computation but also for continuous monitoring and task resubmission in case of failure, contributing to a best-effort approach in chat processing tasks.

Moreover, a very important concept of distributed systems is the "Paxos Concensus Process". Leslie Lamport introduced the Paxos algorithm in the paper called "Paxos Made Simple" [4], which is a family of protocols designed to achieve consensus in a distributed system. The Paxos algorithm addresses the problem of reaching agreement among a group of distributed processes or nodes, even if some of them may fail or deliver messages out of order. The algorithm ensures that a group of nodes can agree on a single value, even in the presence of failures, by using a process of proposal and acceptance.

Taking inspirations from these papers, we are designing our distributed system with the help of load balancing. The primary objective is to demonstrate improved processing speed and increased fault tolerance compared to a synchronous single-node system. Our system introduces a novel approach to campaign creation, article processing, and result retrieval. By leveraging distributed nodes and a robust key-value store synchronized through the Paxos consensus mechanism, we aim to provide users with a highly efficient and resilient tool for analyzing a myriad of topics with ease.

### Naive Approach
In order to monitor a topic of interest, we need to observe information related to the topic across a few 
parameters or dimensions. If we are to stick
to the same example of company X, perhaps the following would be inferred from the articles in the form of a value 
between 0-1.

1. Overall User Satisfaction
2. Trust in X
3. Usability of X
4. Relevance of X
5. Future Outlook of X

If we can obtain values between 0-1 for these **Metalanguage Dimensions** for our articles published in 2023, we could
sufficiently answer the question. The information may also be used to obtain plots of data.

This analysis would traditionally happen via a manual review and labelling of articles, but it can also be done via 
sentiment analysis algorithms (1 node system).

Today, we can use a tool like GPT to analyse any form of text content. The naive approach would involve sequentially 
retrieving the Metalanguage Dimension values and coming up with answer based on the values obtained.

### Our Proposal
We propose a Distributed System that is able to process a large set of articles to answer questions that would
traditionally require a large number of human operators labelling articles manually in order to produce an answer. The
system aims to demonstrate improved processing speed and increased fault tolerance by using a distributed approach compared to a
synchronous single-node system. This design document outlines the design for this Distributed System.

The project scope involves creating a distributed system capable of semantic analysis on a large dataset of text documents. Users can initiate campaigns with specific topics, and the system processes and analyzes each document to extract pre-defined sentiment metrics using GPT models. Meanwhile, the system ensures reliability and fault tolerance through a network of distributed nodes that synchronize data using the Paxos consensus algorithm. It is designed for scalability, allowing for additional nodes to manage larger workloads effectively. The system's technical infrastructure will use a key-value store for data persistence and a RESTful API for operations like creating campaigns and retrieving results. The initial scope does not include real-time processing capabilities, comprehensive data security measures, data backup strategies, or adherence to extensive regulatory compliance.

## High Level Interface

#### Description
The user is able to take 3 different actions.

1. Campaign Creation
2. Article Processing
3. Read Results

```mermaid
graph LR
    User1(User) -- "createCampaign(topic)" --> DS((Distributed System))
    User1(User) -- "processArticle<br/>(campaignId, articleContent, publishDate)" --> DS((Distributed System))
    DS((Distributed System)) -- "readMetalanguageDimension<br/>(campaignId, date)" --> User2(User)
```


## Main Components

| Components                                | Description                                                                                                                                                                                 |
|-------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Client                                    | Initiates requests to the Distributed System.                                                                                                                                               |
| Article <br/> /Document                   | The document being analyzed in the Distributed System. Can be used interchangeably.                                                                  <br/>                                  |
| Load Balancer                             | Connects Clients to a Node that is ready to consume Requests                                                                                                                                |
| Node                                      | Handles campaigns creation, article processing, and read requests. Initiates Paxos Consensus to share new information with all the other nodes.                                             |
| Topic                                     | Research question that Clients want to find answers to.                                                                                                                                     |
| Campaign                                  | An active topic that has been defined in the Distributed System. Each Campaign has an associated set of Metalanguage Dimensions.                                                            |
| Metalanguage Dimensions                   | A set of parameters, that represents features that are being assessed about a <br/><br/>document. each MDim is expressed as a value between 0-1 to indicate the strength of that dimension. |
| MDims Keys                                | Refers to the dimensions themselves and not the values.                                                                                                                                     |
| MDims Values                              | Refers to the values for each key in the MDims Keys.                                                                                                                                        |
| Filter                                    | The process via which an article is determined to be related to a research topic or not.                                                                                                    |
| KV Store                                  | Where active campaigns are tracked and results of article processing is stored.                                                                                                             |
| Paxos Consensus Mechanism                 | Orchestrates the synchronization of updates across nodes to ensure a consistent view of the KV Store.                                                                                       |

#### Metalanguage Dimensions Example:

If we create a campaign with the topic: "What is the impression of Bitcoin in my documents?"

The MDims Keys may be the following:
```json
[
  "generalAttitudeTowardsBitcoin",
  "trustInBitcoin",
  "investmentPotential",
  "futureOutlookOfBitcoin",
  "usabilityOfBitcoin"
]
```

These MDim keys are automatically obtained via GPT when a campaign is created. When an article is processed the MDim 
Values are obtained via GPT as well.

#### Filters Example:

Not all documents that are processed for a given campaign may actually be related to the campaign topic. For example,
if my research topic was about Bitcoin and the document I pass is about Donald Trump, it is probably not related to 
the campaign, in which case, it should be rejected and the client should be notified.

The filter check also utilizes GPT. We define a system message such that the response is a fixed JSON which looks 
like this:
```json
{
  "isRelevant": true 
}
```
Note: the return would be false if the document was not related to the campaign.

## KV Store Schema
The following is the schema of the KV store that each Node maintains:
```json
{
  "Campaigns": {
    "<campaignId>": {
      "topic": "string",
      "creationDate": "string",
      "mDimsKeys": ["mdim1", "mdim2", ...],
    },
    ...
  },
  "Articles": {
    "<campaignId>": {
      "<articleId>": {
        "publishedDate": "string",
        "mDimsValues": {
          "mdim1": float, // Value between 0-1
          "mdim2": float,
          ...
        },
        "isRelevant": boolean // The result of the filter check.
      },
      ...
    }
  },
  "MDimValuesByDate": {
    "<campaignId>": {
      "<date>": {
        "<articleId>": {
          "mDimsValues": {
            "mdim1": float,
            "mdim2": float,
            ...
          }
        },
        ...
      }
    }
  }
}
```
The KV store is synced between nodes via a Paxos Consensus Mechanism. It is triggered when new campaigns are being 
created and when article processing results needs to be stored.


// Add GPT on each node assumption

## Properties of our System

1. New MDim Values that are processed are consistent across nodes, providing a unified view.
2. New MDim Values are stored in an append-only mode.
3. Only if the document being processed

## Operations

### Campaign Creation

- **Purpose:** Each campaign defines the set of metalanguage dimensions that articles will be assessed on. Each 
  campaign can be associated to 1 research question.
- **Inputs:**
    - topic: string
    - topic is the question that is being asked in natural language
- **Actions Taken:**
    -  **Generate MDim Keys to assess**
        - using GPT
    - **Generate Campaign ID:**
        - Generate a unique identifier (campaignId) for the new campaign.
    - **Initialize Campaign:**
        - Set up the new campaign in the KV Store with MDims Keys.
        - Use Paxos to sync campaign information (includes topic and MDim Keys) across 
          nodes

### Article Processing

- **Purpose:** To process an article based on the campaign it is being assessed for.
- **Inputs:**
    - campaignId: string
    - articleContent: string
    - publishDate: date
- **Actions:**
    - **Run Filter Check**
        - using GPT 
    -  **Generate MDim Values**
        - using GPT
    - **Store Result**
        - In KV Store
        - Use Paxos to sync across Nodes

### Reading Results

- **Purpose:** To query the system to retrieve results based on campaign and date
- **Inputs:**
    - campaignId: string
    - publishDate: date
- **Actions:**
    - Runs a round of Paxos Read
    - returns set of MDim calculations with article Ids for the date specified

## System Architecture

```mermaid
flowchart TB
    internet(Data Source) -->|Articles| LB[Load Balancer]
    LB --> N1[Node 1]
    LB --> N2[Node 2]
    LB --> N3[Node 3]
    N1 --> KV1[(KV Store 1)]
    N2 --> KV2[(KV Store 2)]
    N3 --> KV3[(KV Store 3)]
    PAXOS{{"Paxos Consensus"}}
    N1 <-->|Sync| PAXOS
    N2 <-->|Sync| PAXOS
    N3 <-->|Sync| PAXOS
    GPT <-.-> N1
    GPT <-.-> N2
    GPT <-.-> N3
    classDef kvstore fill:#f96;
    class KV1,KV2,KV3 kvstore;
```

This diagram represents a high-level view of the system's architecture where each node has its own KV Store for
data storage. The Paxos consensus mechanism synchronizes the updates across the nodes as information is added to the 
system.

## Information Pipeline

### Stages of Creating a new Campaign 
 
The following diagram shows the steps that are taken when creating a new campaign in the system. We assume that the 
Load Balancer has assigned us a Node that will respond to requests.
```mermaid
flowchart TD
    QI((New <br/> Campaign <br/> Topic))
    ND((Node))
    GPT[GPT Engine]
    MDIMS((MDim Keys))
    SharedKV[(KV Store)]

    QI --> |1. Send Topic| ND
    ND --> |2. Request MDim Keys| GPT
    GPT --> |3. Creates MDim Keys| MDIMS
    MDIMS --> |4. Return MDim Keys| ND
    ND --> |5. Store Campaign Information| SharedKV
    ND --> |6. Respond to Client| QI

    classDef kvstore fill:#f96;
    class SharedKV kvstore;
```


### Stages of Document Processing
The following diagram shows the steps that are taken when processing a new document in the system. 
We assume that the Load Balancer has assigned us a Node that will respond to requests.

Note that the two nodes in the diagram refer to the same node. It is split up for readability.
```mermaid
flowchart TD
    DOC((New <br/> Document))
    NODE((Node))
    NODE2((Node))
    GPT_FILTER[GPT Engine Run 1]
    GPT_MDIMS[GPT Engine Run 2]
    FILT_CHECK{Filter}
    
    DOC --> |1. Send To| NODE
    NODE --> |2. Run Filter Check| GPT_FILTER
    GPT_FILTER --> |3. Response| NODE 
    NODE --> |4. Run Filter Check|FILT_CHECK
    FILT_CHECK -->|If Passes Check| NODE2
    NODE2 --> |5. Generate MDim Values| GPT_MDIMS
    GPT_MDIMS --> |6. Response| NODE2
    FILT_CHECK -->|If Fails Check| END[End Process <br/> and <br/> Notify Client]
    NODE2 --> |7. Store MDim Values|SharedKV[(KV Store)]
    NODE2 --> |8. Respond to Client| DOC

    classDef filtered fill:#f96;
    class END filtered;
    
    classDef kvstore fill:#f96;
    class SharedKV kvstore;
```

### Stages of Querying Results
The following diagram shows the steps that are taken when a read request is issued in the system. 
We assume that the Load Balancer has assigned us a Node that will respond to requests.
```mermaid
flowchart TD
    QI[New Query]
    ND((Node))
    
    QI --> |1. Get Information for <br/> campaignID, date| ND
    ND --> |2. Request information| SharedKV[(Shared KV Store)]
    SharedKV[(KV Store)] --> |3. Return information| ND
    ND --> |4. Return Result| QI
    
    classDef kvstore fill:#f96;
    class SharedKV kvstore;
```
To increase confidence in the results returned, we can run a round of Paxos Read. i.e query a set of nodes and take 
the union of the set of values. This would ensure that if there are nodes that are not fully up to date, they can 
receive the missed information from the other nodes. Note that the read speed would slow down in this case.

### Load Balancer
For all three user actions.
```mermaid
flowchart TD
    REQ[Incoming Requests] --> LB[Load Balancer]
    HB[Heartbeat Monitor] -.->|Heartbeat Checks| N1[Node 1]
    HB -.->|Heartbeat Checks| N2[Node 2]
    HB -.->|Heartbeat Checks| N3[Node 3]
    LB -->|Distribute to Queues| Q1[Queue Node 1]
    LB -->|Distribute to Queues| Q2[Queue Node 2]
    LB -->|Distribute to Queues| Q3[Queue Node 3]
    Q1 -->|Process Next Req| ND1((Node 1))
    Q2 -->|Process Next Req| ND2((Node 2))
    Q3 -->|Process Next Req| ND3((Node 3))
    ND1 <--> |Store & Sync| SKV1[(Shared KV Store 1)]
    ND2 <--> |Store & Sync| SKV2[(Shared KV Store 2)]
    ND3 <--> |Store & Sync| SKV3[(Shared KV Store 3)]

    LB -.->|Reassign on Failure| MQ[Move Queue]
    MQ -.->|Update Allocation| LB

    classDef kvstore fill:#f96;
    class SKV1,SKV2,SKV3 kvstore;
    classDef heartbeat fill:#f00, stroke:#333, stroke-width:2px;
    class HB heartbeat;
```
The Load Balancer is periodically snapshot and persisted such that on failure, we know where to pick up from again.  

## Node Design

Each node is capable of:

1. Creating a campaign by generating MDim Keys.
2. Processing articles by extracting MDim Values.
3. Handling consensus through Paxos to ensure each node's view of the JSON KV Store is consistent.
4. Reading values from its KV store to respond to queries.

## Paxos Consensus Process

There is a Paxos consensus process initiated for 2 out of 3 operations in our Distributed System. 

1. Campaign Creation: after generating the relevant MDim Keys for a topic, it needs to be shared across nodes in order 
   for all the nodes to independently be able to process articles for that campaignId.
2. Article Processing: after extracting the MDim values for an article, the results need to be shared across nodes 
   so any node is able to respond to queries about that article.

### Stages

1. Prepare (proposers --> acceptors)
    * Initiated on client `write` request
    * Send **All Nodes** `prepare` message with `seq_num`
2. Promise (acceptors --> proposers)
    * **All Nodes** `promise` with `success` or `fail` with `highest_seq_accepted`
    * Based on Quorum, proceeds to *Accept* if Quorum attained else, retry *Prepare* with `highest_seq_accepted + 1`
3. Accept (proposers --> acceptors)
    * When Quorum achieved for `sequence_number`, send `accept` message with `value` to append and `key` to append to.
    * 50% quorum for acceptance
4. Commitment (acceptors --> learners)
    * acceptors share learnings with **All Nodes**

### Paxos Lifecycle Diagram
Every node in our Distributed System will play all 3 roles of Proposer, Acceptor and Learner. 
```mermaid
sequenceDiagram
    participant I as Node
    participant P as Proposer
    participant A as Acceptor
    participant L as Learner
    I ->> P: Initiate Paxos<br/>Consensus
    P ->> A: Prepare<br/>(seq_num)
    A -->> P: Promise<br/>(Accept | Reject)
    P -->> I: Fail after<br/>3 retries
    P ->> A: Accept Proposal<br/>(seq_num, MDims)
    A ->> L: Commit Proposal<br/>(MDims)
    P -->> I: Success
    Note right of P: Proposer gets MDims from GPT <br/> after sentiment analysis
    Note right of A: Acceptor checks local state,<br/>promises if valid
    Note right of L: Learner updates KV Store<br/>with MDims
```

### Handling Failures

* Node Failure
    * If a node fails during the consensus process, the client should be notified of failure so they may try again

* Proposal Rejection
    * If a proposal is rejected during the Prepare or Accept phases, the proposer must attempt to reach 3 attempts 
      before failure

* Network Partitions
    * Paxos is designed to tolerate network partitions to a certain extent. However, prolonged partitions may require
      additional mechanisms for reconciliation.

## Networking and Communication

The system will use HTTP/REST for communication between nodes due to its simplicity and ease of implementation. Each
node will have a RESTful API that allows for creating campaigns, processing articles, and reading the current state of
MDims.

## Load Balancing Strategy

The system will use a round-robin algorithm implemented within the Load Balancer to distribute incoming article
processing requests evenly across available nodes. The Load Balancer will run periodic Heartbeat checks to all nodes 
to obtain status of nodes. If nodes do not respond, the process queue will be moved to a different active node.

## Storage and Log Management

The system will adopt simple JSON files as a key-value store for node state data, including campaign information and
processed MDims. Results of Article Processing is appended to the date in the KV store.

```mermaid
sequenceDiagram
    autonumber
    participant A as Article Stream
    participant LB as Load Balancer
    participant N as Node
    participant G as GPT Model
    
    
    participant J as JSON KV Store
    participant P as Paxos Consensus
    A ->> LB: New Article
    LB ->> N: Assign Article Processing
    N ->> G: Send Content for Analysis
    G -->> N: Return MDim Values
    N ->> J: Store Result (append)
    J -->> P: Share Update
    P -->> J: Synchronize State
```

This sequence diagram illustrates the information flow from when a new article is queued to the MDims being stored 
in the KV store.

## GPT Usage

There are three parts to this:
- Filter Checks
- MDim Keys
- MDim Values

For all three, we will use the OpenAI API to generate the MDim Keys and MDim Values. The filter check will be a 
simple JSON response that responds with relevance. 

For example, if the research topic was: "What is the public perception of the new Martin Scorcese movie: Killers of 
the Flower Moon", the MDim Keys that GPT may generate is the following:

1. Film Direction Quality
2. Performance Quality
3. Set Design Quality
4. etc...

For each article we process in this campaign, we will need a value between 0-1 to describe the effectiveness of the 
movie to answer our original research question.

## API Endpoints
### POST /createCampaign
Creates a new campaign with a given topic and a set of MDims. 

Request Body:

```json
{
  "topic": "string"
}
```

Response:

```json
{
  "campaignId": "string"
}
```

Side-effects:
1. Store MDim Keys in KV Store
2. Sync across Nodes

### POST /processArticle
Processes an article and updates MDims for the relevant campaign and date. 

#### Request Body:

```json
{
  "campaignId": "string",
  "articleContent": "string",
  "publishedDate": "string"
}
```

#### Response:

```
{ "success": boolean }
```

#### Side-effects:
1. Store MDim Values in KV Store
2. Sync across Nodes


### GET /readMDims
Returns the MDims for a given campaign and date. 

#### Query Parameters: 
campaignId=string&date=string 

#### Response:

```
{ "MDims": [{ "articleId": string, mDims: {direction_quality": float, ...}}] }
```

## Performance Benchmarking

Performance benchmarking will be carried out using a custom-built tool to simulate article streaming and measure
throughput across both the distributed system and a synchronous single-node reference configuration. The metrics
collected will include articles processed per second, latency, and error rate.

## Potential System Risks/Challenges

1. **Node Failure:**
    - A node may fail during various stages, such as campaign creation, article processing, or the Paxos consensus
      process.

      **Mitigations**: - Heartbeat checks for timely detection and automated response to unresponsive nodes, while optimizing system resilience through load balancing, redundancy strategies, and replicating critical components

2. **Proposal Rejection:**
    - Proposals during the Paxos process may be rejected, leading to the need for the proposer to adapt and propose a
      new update.

      **Mitigations:** - Retry till sequence number obtained <br> - A timeout mechanism to avoid potential deadlocks
 
3. **Network Partitions:**
    - Network partitions may occur, disrupting communication between nodes.

      **Mitigations:** - Paxos is designed to tolerate partitions to some extent, but prolonged partitions may pose challenges.

4. **Duplicate Operations:**
    - Nodes must ensure that duplicate operations are not processed. This is critical during the Paxos consensus process
      and in handling article processing requests.

      **Mitigations:** - An internal Key-Value (KV) store that is consulted before processing an operation to check for the presence of a previous occurrence. <br> - If the operation is found in the KV store, indicating a duplicate, the node can discard or appropriately handle the redundant request, ensuring that each operation is processed only once in both the Paxos consensus process and article processing.

5. **Invalid Article Processing Request:**
    - The system needs to handle cases where an article processing request is invalid or contains incorrect parameters.

    **Mitigations:** - Respond to client with failures

9. **Load Balancer Failure:**
    - Issues with the load balancer may impact the even distribution of article processing requests across nodes.

    **Mitigations:** - A system that periodically takes snapshots of the load balancing state and persists the information <br> - In the event of a load balancer failure, the system can refer to the latest snapshot to understand the state prior to the failure and resume even distribution from the last known point, ensuring continued stability and efficiency in handling requests.

10. **JSON KV Store Failure:**
    - Failures in the JSON KV store, where state data is maintained, could lead to data inconsistencies.

    **Mitigations:** - A protocol where information is shared only after successful processing and storage in the JSON KV store. <br> - By adopting this strategy, the system ensures that data inconsistencies are minimized, as shared information reflects a state that has been successfully updated in the KV store, reducing the impact of potential failures on overall data integrity.

12. **Unavailability of GPT:**
    - Single point of failure since the sentiment is calculated based on responses from the GPT. But we are assuming that each of the nodes will have their own custom GPT model with robust error handling.

    - Failures in establishing a connection to the OPENAI API during the article processing phase could occur.

## Future Considerations

Post-PoC, the system design will be revised to consider scaling, real-time
monitoring and alerting, data persistence scalability, and system resilience. The design will also incorporate user
feedback and address performance bottlenecks identified during the PoC phase.

Moving forward, additional operations such as deleting and updating will be seamlessly integrated into the system's functionality:

- Deleting Operations:

  A secure and efficient deletion mechanism will be introduced, allowing users to remove outdated or unnecessary data. This feature will be implemented with careful consideration for data integrity and user access permissions.

- Updating Operations:

  The system will incorporate robust updating capabilities, enabling users to modify existing data as needed. This includes implementing version control mechanisms to track changes and ensuring seamless integration with the overall data processing workflow.

## Conclusion

This detailed design document provides the foundation for implementing the Distributed Semantic Analysis/Monitoring
system from scratch. It outlines the architecture, components, and processes necessary for a PoC that can be scaled and
enhanced based on future requirements and findings.

Moreover, this design can be made more generic to perform a wider variety of actions across large natural language 
datasets. 

## References
[1] Hieu, N. T., Francesco, M. D., and Ylä-Jääski, A. 2013. Extracting Knowledge from Wikipedia Articles through Distributed Semantic Analysis. In Proceedings of the 13th International Conference on Knowledge Management and Knowledge Technologies (i-Know '13). Association for Computing Machinery, New York, NY, USA, Article 6, 1–8. https://doi.org/10.1145/2494188.2494195

[2] van Steen, M., Tanenbaum, A.S. A brief introduction to distributed systems. Computing 98, 967–1009 (2016). https://doi.org/10.1007/s00607-016-0508-7

[3] Dascalu, Mihai & Dobre, Ciprian & Trausan-Matu, Stefan & Cristea, Valentin. (2011). Beyond Traditional NLP: A Distributed Solution for Optimizing Chat Processing - Automatic Chat Assessment Using Tagged Latent Semantic Analysis. Proceedings - 2011 10th International Symposium on Parallel and Distributed Computing, ISPDC 2011. 133-138. 10.1109/ISPDC.2011.28. 

[4] Lamport, L. (2001). Paxos Made Simple.