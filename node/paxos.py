# Code based on https://github.com/malfusion/paxos/blob/master/paxos.py

class PaxosNode:
    def __init__(self, nodeid, comm):
        self.nodeId = nodeid
        self.comm = comm
        self.consensusValue = None

        #Proposer
        self.mesgValue = None
        self.ctr = 0
        self.permAccepts = {}
        self.proposalAccepts = {}

        #Acceptor
        self.lastPromised = None
        self.lastAccepted = None
        self.lastAcceptedValue = None

        def hasReachedConsensus(self):
            return self.consensusValue is not None