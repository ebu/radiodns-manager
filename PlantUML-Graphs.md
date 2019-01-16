#PlantUML Graphs for RadioVIS

## Processes and flow inside RadioVIS Server

    @startuml
    
    title RadioDNS - VIS Server and Fallback
    footer EBU.io, 2015
    header
      Processes and data flow inside RadioVIS Server
    end header
    
    state RadioDNSDatabase {
      state Channels {
        Channel1:/fm/4000/09120/
        Channel2:/fm/4000/*/
      }
      state Stations {
        StationsX --> Channels
      }
    }
    
    
    [*] -> RadioVISServer
    [*] -> Fallback
    
    state RadioVISServer {
      [*] -> InitVIS
      InitVIS: initialisation of VIS Server
    
      [*] -> Connect
      Connect: client connects to STOMP
      Connect --> Subscribe: subscribe
      Connect --> Publish: publish
      Subscribe: Subscribe to topic /topic/fm/4e1/4000/09100/
    
      state Publish {
        DispatchToAllClients -> Dispatch
        DispatchToAllClients: to /topic/fm/4e1/4000/*/
      }
    
      state Clients {
        state Subscribe {
          [*] -> CheckEcc
          CheckEcc --> CheckChannelExists
          CheckEcc: Check if ISO is used, if so use ECC instead
          CheckChannelExists: Check if Channel is in Cache, if not check for Wildcard
          CheckChannelExists --> RegisterSubscription
          RegisterSubscription --> RegisteredTopics: append
          RegisterSubscription: add topic to registration of client
        }
        state Dispatch {
          [*] -> CheckIfRegistered
          RegisteredTopics --> CheckIfRegistered: if
          CheckIfRegistered --> DispatchMessage: yes
        }
    
        state RegisteredTopics {
          Topic: /topic/fm/4e1/4000/*/
        }
      }
    }
    
    
    state Fallback {
      [*] -> Every5Minutes
      Every5Minutes -> Every5Minutes: loop
      Every5Minutes: fallback loop resetting default pictures and updating cache
    }
    
    state MemCache {
      UpdateCache --> ChannelCache : update
      UpdateCache --> ECCCache : update
      Channels --> UpdateCache: retrieve
      ChannelCache --> CheckChannelExists : get
      ChannelCache: MemCached list
      ECCCache --> CheckEcc : get
      ECCCache: MemCached list
    
      InitVIS --> UpdateCache : initial
      Every5Minutes --> UpdateCache : fallback
    }
    
    @enduml