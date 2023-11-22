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

## High Level Interface

#### Description
The user is able to take 3 different actions.
1. Campaign Creation
2. Article Processing
3. Read Requests

```mermaid
graph LR
    User1(User) -- "createCampaign(topic)" --> DS((Distributed System))
    User1(User) -- "processArticle<br/>(campaignId, articleContent, publishDate)" --> DS((Distributed System))
    DS((Distributed System)) -- "readMetalanguageDimension<br/>(campaignId, date)" --> User2(User)
```


## Main Components

| Components                | Description                                                                                                                                                                                 |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Client                    | Initiates requests to the Distributed System.                                                                                                                                               |
| Article/Document          | The document being analyzed in the Distributed System. Can be used interchangeably.                                                                  <br/>                                  |
| Load Balancer             | Connects Clients to a Node that is ready to consume Requests                                                                                                                                |
| Node                      | Handles campaigns creation, article processing, and read requests. Initiates Paxos Consensus to share new information with all the other nodes.                                             |
| Topic                     | Research question that Clients want to find answers to.                                                                                                                                     |
| Campaign                  | An active topic that has been defined in the Distributed System. Each Campaign has an associated set of Metalanguage Dimensions.                                                            |
| Metalanguage Dimensions   | A set of parameters, that represents features that are being assessed about a <br/><br/>document. each MDim is expressed as a value between 0-1 to indicate the strength of that dimension. |
| MDims Keys                | Refers to the dimensions themselves and not the values.                                                                                                                                     |
| MDims Values              | Refers to the values for each key in the MDims Keys.                                                                                                                                        |
| Filter                    | The process via which an article is determined to be related to a research topic or not.                                                                                                    |
| KV Store                  | Where active campaigns are tracked and results of article processing is stored.                                                                                                             |
| Paxos Consensus Mechanism | Orchestrates the synchronization of updates across nodes to ensure a consistent view of the KV Store.                                                                                       |

#### Metalanguage Dimensions Example

If we create a campaign with the topic: "What is the impression of Bitcoin in my documents?"

The MDims Keys may be the following:
```
["generalAttitudeTowardsBitcoin", "trustInBitcoin", "investmentPotential", "futureOutlookOfBitcoin", "usabilityOfBitcoin"]
```

These MDim keys are automatically obtained via GPT when a campaign is created. When an article is processed the MDim 
Values are obtained via GPT as well.

#### Filters Example

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
flowchart LR
    DOC((New <br/> Document))
    NODE((Node))
    NODE2((Node))
    GPT_FILTER[GPT Engine Run 1]
    GPT_MDIMS[GPT Engine Run 2]
    FILT_CHECK{Filter}
    
    DOC --> |1. Send To| NODE
    NODE --> |2. Run Filter Check| GPT_FILTER
    GPT_FILTER --> |3. Response| NODE 
    NODE --> FILT_CHECK
    FILT_CHECK -->|If Passes Check| NODE2
    NODE2 --> |4. Generate MDim Values| GPT_MDIMS
    GPT_MDIMS --> |5. Response| NODE2
    FILT_CHECK -->|If Fails Check| END[End Process <br/> and <br/> Notify Client]
    NODE2 --> |6. Store MDim Values|SharedKV[(KV Store)]
    NODE2 --> |7. Respond to Client| DOC

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
flowchart LR
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

## Potential System Failures

1. **Node Failure:**
    - A node may fail during various stages, such as campaign creation, article processing, or the Paxos consensus
      process.

2. **Proposal Rejection:**
    - Proposals during the Paxos process may be rejected, leading to the need for the proposer to adapt and propose a
      new update.

3. **Network Partitions:**
    - Network partitions may occur, disrupting communication between nodes. Paxos is designed to tolerate partitions to
      some extent, but prolonged partitions may pose challenges.

4. **Duplicate Operations:**
    - Nodes must ensure that duplicate operations are not processed. This is critical during the Paxos consensus process
      and in handling article processing requests.

5. **Invalid Article Processing Request:**
    - The system needs to handle cases where an article processing request is invalid or contains incorrect parameters.

6. **OPENAI API Connection Failure:**
    - Failures in establishing a connection to the OPENAI API during the article processing phase could occur.

7. **MDim Retrieval Failure:**
    - Issues in retrieving MDims or counting processed values for a specified date may lead to failures in the
      aggregation process.

8. **Consensus Process Failure:**
    - Failures during the Paxos consensus process may prevent the synchronization of updates across nodes.

9. **Load Balancer Failure:**
    - Issues with the load balancer may impact the even distribution of article processing requests across nodes.

10. **JSON KV Store Failure:**
    - Failures in the JSON KV store, where state data is maintained, could lead to data inconsistencies.

11. **Campaign ID Generation Failure:**
    - Failure to generate a unique campaign ID during campaign creation could lead to conflicts.

12. **Article Content Extraction Failure:**
    - Errors in extracting MDims from the article content during the article processing phase.

## Future Considerations

Post-PoC, the system design will be revised to consider scaling, real-time
monitoring and alerting, data persistence scalability, and system resilience. The design will also incorporate user
feedback and address performance bottlenecks identified during the PoC phase.

The current design does not deal with nodes that lag behind on information. For example, if a node goes offline for 
a wihle and then comes back online, there is currently no mechanism to retrieve the missed updates. This would need 
to be looked at in the future.

## Conclusion

This detailed design document provides the foundation for implementing the Distributed Semantic Analysis/Monitoring
system from scratch. It outlines the architecture, components, and processes necessary for a PoC that can be scaled and
enhanced based on future requirements and findings.

Moreover, this design can be made more generic to perform a wider variety of actions across large natural language 
datasets. 
