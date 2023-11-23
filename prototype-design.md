# Distributed Semantic Analysis/Monitoring System Prototype Design Document

The purpose of this document is to outline the design for the prototype we are building to illustrate the speed improvements that results from
the Distributed Semantic Analysis/Monitoring System.

## Prototype Goals

1. Should be able to create a new Campaign with a topic of interest
    1. Example: "How are people liking the new Martin Scorcese movie: Killers of the Flower Moon"
2. Should accept a Document and a CampaignID as an input to queue for processing
3. Should be able to query the results based on CampaignID and a date

## Some Prototype Simplifications
In the interest of time, we will be making some simplifications to our complete design to implement the prototype.

1. Shared KV store
   1. No paxos consensus
2. Concurrency library will be used


## Information Pipeline

### Stages of Creating a new Campaign 
```mermaid
flowchart TD
    QI[New Campaign Question]
    ND((Node))
    GPT[GPT]
    MDIMS[MDims]
    FT[Filter]
    
    QI --> |Send to| ND
    ND --> |Generate MDims| GPT
    ND --> |Generate Filter| GPT
    GPT --> |generates| MDIMS
    GPT --> |generates| FT
    MDIMS --> |campaignID| SharedKV[(Shared KV Store)]
    FT --> |campaignID| SharedKV[(Shared KV Store)]
    
    classDef kvstore fill:#f96;
    class SharedKV kvstore;
```

### Stages of Document Processing
```mermaid
flowchart TD
    DOC[Incoming Document]
    NODE((Node))
    GPT_FILTER[GPT Filter Assessment]
    FILT_CHECK{Filter Check}
    GPT_MDim[GPT Metalanguage Dimensions `MDim` Assessment]

    DOC --> NODE
    NODE --> GPT_FILTER
    GPT_FILTER --> FILT_CHECK
    FILT_CHECK -->|If Not Filtered| GPT_MDim
    FILT_CHECK -->|If Filtered| END[End Process]
    GPT_MDim --> SharedKV[(Shared KV Store)]

    classDef filtered fill:#f96;
    class END filtered;
    
    classDef kvstore fill:#f96;
    class SharedKV kvstore;
```

### Stages of Querying Results
```mermaid
flowchart TD
    QI[New Query]
    ND((Node))
    
    QI --> |campaignID, date| ND
    ND --> SharedKV[(Shared KV Store)]
    SharedKV[(Shared KV Store)] --> ND
    ND --> |Result| QI
    
    classDef kvstore fill:#f96;
    class SharedKV kvstore;
```

### Load Balancer
For all three user actions
```mermaid
flowchart LR
    REQ[Incoming Requests] --> LB[Load Balancer]
    LB --> Q[Queue]
    Q --> R1[Request 1]
    Q --> R2[Request 2]
    Q --> R3[Request 3]
    R1 --> ND((Node 1))
    R2 --> ND((Node 2))
    R3 --> ND((Node 3))
    ND1 <--> |Process| SharedKV[(Shared KV Store)]
    ND2 <--> |Process| SharedKV
    ND3 <--> |Process| SharedKV

    classDef kvstore fill:#f96;
    class SharedKV kvstore;
```

## Notes
 