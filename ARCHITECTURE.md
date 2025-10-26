# Boba BI System Architecture

## High-Level Multi-Agent Architecture

```mermaid
graph TB
    User[Business Owner Query] --> Orchestrator[Orchestrator Agent]
    
    Orchestrator --> DataAnalyst[Data Analyst Agent]
    Orchestrator --> Weather[Weather Agent]
    Orchestrator --> Scheduler[Scheduler Agent]
    
    DataAnalyst --> POS[(POS Data<br/>100 weeks)]
    DataAnalyst --> Analysis[Traffic Pattern<br/>Analysis]
    
    Weather --> WebSearch[web_search Tool]
    Weather --> Forecast[Weather Forecast<br/>& Impact Analysis]
    
    Scheduler --> Employees[(Employee Data<br/>10 employees)]
    Scheduler --> Constraints[Constraint Solver<br/>Max Hours, Min Staff]
    
    Analysis --> Orchestrator
    Forecast --> Orchestrator
    Constraints --> Orchestrator
    
    Orchestrator --> Report[Final Report]
    Report --> CSV[CSV Export]
    Report --> UI[Web UI Display]
    
    style Orchestrator fill:#667eea,color:#fff
    style DataAnalyst fill:#48bb78,color:#fff
    style Weather fill:#ed8936,color:#fff
    style Scheduler fill:#4299e1,color:#fff
    style Report fill:#9f7aea,color:#fff
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Orchestrator
    participant DataAnalyst
    participant Weather
    participant Scheduler
    
    User->>Orchestrator: "How should I schedule for next week?"
    
    Orchestrator->>DataAnalyst: Analyze historical traffic
    DataAnalyst->>DataAnalyst: Process 100 weeks POS data
    DataAnalyst->>DataAnalyst: Calculate peak hours by day/shift
    DataAnalyst-->>Orchestrator: Traffic patterns & recommendations
    
    Orchestrator->>Weather: Get weather forecast for 7 days
    Weather->>Weather: web_search("San Diego weather next week")
    Weather->>Weather: Analyze impact (+20% hot, -30% rain)
    Weather-->>Orchestrator: Weather impact predictions
    
    Orchestrator->>Scheduler: Create optimal schedule
    Scheduler->>Scheduler: Apply constraints (40hr max, 2 min)
    Scheduler->>Scheduler: Match employee preferences
    Scheduler->>Scheduler: Optimize staffing levels
    Scheduler-->>Orchestrator: 7-day schedule with assignments
    
    Orchestrator->>Orchestrator: Compile final report
    Orchestrator-->>User: Schedule CSV + insights
```

## Component Architecture

```mermaid
graph LR
    subgraph Backend Core
        Main[boba_bi.py]
        Data[Data Generators]
        Tools[Tool Functions]
        Agents[Multi-Agent System]
    end
    
    subgraph API Layer Optional
        API[api_server.py]
        Endpoints[REST Endpoints]
    end
    
    subgraph Frontend Optional
        UI[demo_frontend.html]
        Display[Schedule Display]
    end
    
    subgraph External
        Claude[Claude API]
        Weather[Weather APIs]
    end
    
    Main --> Data
    Main --> Tools
    Main --> Agents
    
    Agents --> Claude
    Agents --> Weather
    
    Main --> API
    API --> Endpoints
    Endpoints --> UI
    UI --> Display
    
    style Main fill:#667eea,color:#fff
    style API fill:#48bb78,color:#fff
    style UI fill:#ed8936,color:#fff
    style Claude fill:#9f7aea,color:#fff
```

## Agent Communication Pattern

```mermaid
graph TD
    Query[Business Query] --> Orchestrator{Orchestrator<br/>Agent}
    
    Orchestrator -->|Parallel Execution| Agent1[Data Analyst]
    Orchestrator -->|Parallel Execution| Agent2[Weather Agent]
    
    Agent1 -->|Results| Merge[Result<br/>Synthesis]
    Agent2 -->|Results| Merge
    
    Merge --> Orchestrator
    
    Orchestrator -->|Sequential| Agent3[Scheduler Agent]
    
    Agent3 -->|Schedule| Output[Final Report<br/>Generation]
    
    Output --> CSV[CSV File]
    Output --> Console[Console Display]
    Output --> API[API Response]
    
    style Orchestrator fill:#667eea,color:#fff
    style Agent1 fill:#48bb78,color:#fff
    style Agent2 fill:#ed8936,color:#fff
    style Agent3 fill:#4299e1,color:#fff
    style Output fill:#9f7aea,color:#fff
```

## Scheduling Algorithm Flow

```mermaid
flowchart TD
    Start([Start Scheduling]) --> Init[Initialize employee hours = 0]
    
    Init --> LoopDay{For each<br/>of 7 days}
    
    LoopDay -->|Next Day| LoopShift{For each<br/>shift}
    
    LoopShift -->|Morning/Evening| CalcDemand[Calculate staff demand<br/>orders_per_hour / 15]
    
    CalcDemand --> Weather[Apply weather multiplier<br/>+20% hot, -30% rain]
    
    Weather --> Filter[Get available employees<br/>check availability & preferences]
    
    Filter --> Sort[Sort by preference score<br/>and current hours]
    
    Sort --> Assign{Assign staff<br/>while needed}
    
    Assign -->|More needed| CheckHours{Employee<br/>hours < 40?}
    
    CheckHours -->|Yes| Add[Add to schedule<br/>increment hours]
    CheckHours -->|No| Skip[Skip employee]
    
    Add --> Assign
    Skip --> Assign
    
    Assign -->|Complete| Record[Record shift in schedule]
    
    Record --> LoopShift
    LoopShift -->|All shifts done| LoopDay
    LoopDay -->|All days done| Output[Generate CSV & Report]
    
    Output --> End([End])
    
    style Start fill:#48bb78,color:#fff
    style CalcDemand fill:#667eea,color:#fff
    style Weather fill:#ed8936,color:#fff
    style Assign fill:#4299e1,color:#fff
    style Output fill:#9f7aea,color:#fff
    style End fill:#48bb78,color:#fff
```

## Technology Stack

```mermaid
graph LR
    subgraph AI Layer
        Claude[Claude 4 Sonnet]
        Functions[Function Calling]
    end
    
    subgraph Backend
        Python[Python 3.8+]
        SDK[Anthropic SDK]
        Flask[Flask Optional]
    end
    
    subgraph Data
        Synthetic[Synthetic Data<br/>Generator]
        CSV[CSV Export]
    end
    
    subgraph Frontend Optional
        HTML[HTML/CSS/JS]
        API[REST API]
    end
    
    Claude --> Functions
    Functions --> SDK
    SDK --> Python
    Python --> Synthetic
    Python --> Flask
    Synthetic --> CSV
    Flask --> API
    API --> HTML
    
    style Claude fill:#9f7aea,color:#fff
    style Python fill:#667eea,color:#fff
    style Synthetic fill:#48bb78,color:#fff
    style HTML fill:#ed8936,color:#fff
```

---

## Usage in Presentations

### For Slide Decks
1. Copy the Mermaid code into [Mermaid Live Editor](https://mermaid.live/)
2. Export as PNG/SVG
3. Insert into PowerPoint/Google Slides

### For Documentation
- These diagrams render automatically in:
  - GitHub README.md
  - GitLab
  - VS Code (with Mermaid extension)
  - Notion
  - Obsidian

### For Hackathon Judges
Print these diagrams to show:
- System complexity
- Multi-agent coordination
- Scalable architecture
- Professional design thinking
