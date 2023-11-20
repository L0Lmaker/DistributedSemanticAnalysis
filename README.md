# Distributed Semantic Analysis/Monitoring System Design Document

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

The purpose of this document is to outline the design for a Distributed Semantic Analysis/Monitoring system, which analyzes public sentiment across various dimensions in articles related to specific topics over time. The system aims to demonstrate improved processing speed and efficiency by using a distributed approach compared to a synchronous single-node system.

## System Architecture

```mermaid
flowchart TB
    internet(Internet) -->|Articles| LB[Load Balancer]
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

    classDef kvstore fill:#f96;
    class KV1,KV2,KV3 kvstore;
```
This diagram represents a high-level view of the system's architecture where each node has its own JSON KV Store for state data. The Paxos consensus mechanism synchronizes the updates across the nodes.

## Node Design
Each node is responsible for:

1. Creating a campaign with default MDims.
2. Processing articles by extracting MDims and aggregating these into the existing values.
3. Handling consensus through Paxos to ensure each node's view of the JSON KV Store is consistent.
4. Aggregated MDim Calculation

### When a new MDim value is processed, the node will:

Retrieve the current MDim value and the count of processed values for the date.
Aggregate the new value using the formula: 


![Equation](https://quicklatex.com/cache3/b3/ql_90e82a9f045228076eff61b28b3e83b3_l3.png)


Update the MDim value and increment the processed count.
Share this processed information with other nodes during the Paxos consensus stage.

## Paxos Consensus Process

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

#### Lifecycle Diagram
```mermaid
sequenceDiagram
    participant I as Initiator
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
  * If a proposal is rejected during the Prepare or Accept phases, the proposer must to reach 3 attempts

* Network Partitions
  * Paxos is designed to tolerate network partitions to a certain extent. However, prolonged partitions may require additional mechanisms for reconciliation.

### Integration with System States
#### Consensus Handling State
The Paxos consensus process is initiated within the "Consensus Handling" state of the system, specific to updating MDims for sentiment analysis.

#### Transitions
Transitions to other states (e.g., Article Processing) depend on the outcomes of the Paxos consensus process.

### Advantages and Considerations
#### Sentiment Analysis Integration
Paxos ensures that updates to MDims for sentiment analysis are consistent across nodes, providing a unified view and increased fault tolerance of the system.

#### MDim Writing in Append-Only Mode
The MDims are appended in an append-only mode in the distributed JSON KV Store, as processing order is not a requirement.

#### Comparing MDims
The system is able to query the system before processing with GPT to ensure that the document has not already been processed for a campaign in the past thereby boosting processing times.


## Networking and Communication
The system will use HTTP/REST for communication between nodes due to its simplicity and ease of implementation. Each node will have a RESTful API that allows for creating campaigns, processing articles, and reading the current state of MDims.

## Load Balancing Strategy
The system will use a round-robin algorithm implemented within the Load Balancer to distribute incoming article processing requests evenly across available nodes.

## Storage and Log Management
The system will adopt simple JSON files as a key-value store for node state data, including campaign information and processed MDims. Each node will maintain an append-only log file to record operations, which will be compressed and snapshot periodically to update the JSON KV Store.

```mermaid
sequenceDiagram
    autonumber
    participant A as Article Stream
    participant LB as Load Balancer
    participant N as Node
    participant G as GPT Model
    participant L as Append Log
    participant S as Snapshot Function
    participant J as JSON KV Store
    participant P as Paxos Consensus
    A ->> LB: New Article
    LB ->> N: Assign Article Processing
    N ->> G: Send Content for Analysis
    G -->> N: Return MDim Values
    N ->> L: Record Operation
    N ->> J: Aggregate MDims
    J -->> P: Share Update
    P -->> J: Synchronize State
    S ->> J: Perform Periodic Snapshot
    S -->> L: Trigger Log Clearance
    L -->> N: Confirm Log Cleared
    N -->> S: Confirm Snapshot Completion
```
This sequence diagram elaborates on the storage management and synchronization process involving Paxos consensus.

## Metadata Extraction
During the PoC phase, the metadata extraction will simply return random values between 0 and 1 for the MDims. For full implementation, metadata extraction would involve analyzing the article content to obtain sentiment scores relevant to each MDim. The specifics of NLP integration will be explored post-PoC.

## API Endpoints
POST /createCampaign
Creates a new campaign with a given topic and default MDims. Request Body:

```json
{ "topic": "string" }
```
Response:

```json
{ "campaignId": "string" }
```
POST /processArticle
Processes an article and updates MDims for the relevant campaign and date. Request Body:

```json
{ "campaignId": "string", "articleContent": "string", "publishedDate": "string" }
```
Response:

```
{ "success": boolean, "newMDims": { "mdim1": float, ... } }
```
GET /readMDims
Returns the MDims for a given campaign and date. Query Parameters: campaignId=string&date=string Response:

```
{ "MDims": { "direction_quality": float, ... } }
```

## Performance Benchmarking
Performance benchmarking will be carried out using a custom-built tool to simulate article streaming and measure throughput across both the distributed system and a synchronous single-node reference configuration. The metrics collected will include articles processed per second, latency, and error rate.

## Future Considerations
Post-PoC, the system design will be revised to consider scaling, robust metadata extraction using NLP, real-time monitoring and alerting, data persistence scalability, and system resilience. The design will also incorporate user feedback and address performance bottlenecks identified during the PoC phase.

## Story Point Estimation
| Task                         | Description                                                                                      | Estimated Points |
|------------------------------|--------------------------------------------------------------------------------------------------|------------------|
| System Architecture          | Overall design, including node architecture and data flow diagrams.                              | 5                |
| Node Design                  | Define the responsibilities, functionalities, and state management of an individual node.        | 3                |
| Networking and Communication | Specify communication protocols and mechanisms for data exchange between nodes.                  | 3                |
| Load Balancing Strategy      | Develop the algorithm or strategy for distributing workloads across nodes.                       | 2                |
| Storage and Log Management   | Design the JSON KV store, log file functioning, and snapshotting mechanism.                      | 3                |
| Metadata Extraction          | Plan a simplified approach for MDims extraction and propose a mock implementation for the PoC.   | 2                |
| API Endpoints                | Detail each API endpoint, including expected inputs, outputs, and error handling.                | 3                |
| Performance Benchmarking     | Formulate a plan for how to benchmark the system and analyze its performance.                    | 5                |
| Future Considerations        | Outline potential enhancements, scalability options, and other considerations for post-PoC.     | 1                |
| Overall Documentation        | Writing, formatting the document, and creating diagrams.                                        | 8                |

## Conclusion
This detailed design document provides the foundation for implementing the Distributed Semantic Analysis/Monitoring system from scratch. It outlines the architecture, components, and processes necessary for a PoC that can be scaled and enhanced based on future requirements and findings.
