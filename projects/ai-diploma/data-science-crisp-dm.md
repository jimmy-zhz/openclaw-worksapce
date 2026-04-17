# Data Science - CRISP-DM Methodology

**Topic:** Data science based on CRISP-DM (Cross-Industry Standard Process for Data Mining)
**File Alias:** `crisp-dm` (easy to remember name)
**Discussion Started:** April 17, 2026
**Related to:** AI Diploma coursework

## CRISP-DM Overview
CRISP-DM is a 6-phase process model for data mining projects:

1. **Business Understanding**
2. **Data Understanding**
3. **Data Preparation**
4. **Modeling**
5. **Evaluation**
6. **Deployment**

## Current Focus Areas

### 1. Business Understanding
- Defining project objectives from business perspective
- Translating to data mining problem definition
- Success criteria

### 2. Data Understanding
- Initial data collection
- Data quality assessment
- Data exploration
- Hypothesis generation

### 3. Data Preparation
- Data cleaning
- Feature engineering
- Dataset construction
- Train/test/validation splits

### 4. Modeling
- Algorithm selection
- Model training
- Parameter tuning
- Model documentation

### 5. Evaluation
- Model performance assessment
- Business objective review
- Deployment readiness

### 6. Deployment
- Model integration
- Monitoring plan
- Maintenance strategy
- Documentation

## Jimmy's Context
- **Background:** 10 years Java/IT experience
- **Current:** AI student at University of Winnipeg PACE
- **Strengths:** Technical implementation, system thinking
- **Learning focus:** Applying CRISP-DM to real projects

## Coursework Applications
- How CRISP-DM fits into AI diploma curriculum
- Assignment requirements related to CRISP-DM
- Project ideas using CRISP-DM framework

## Resources Needed
- CRISP-DM documentation
- Case studies
- Tools (Python/R, Jupyter, ML libraries)
- University course materials

## Database Sources for Data Analysis
**Discussion Date:** April 17, 2026
**Topic:** Real-world database systems used for data ingestion in CRISP-DM Data Understanding phase

### Common Database Types in Industry

#### 1. Relational Databases (SQL)
- **PostgreSQL** - Open source, feature-rich, JSON support
- **MySQL/MariaDB** - Web applications, e-commerce
- **Microsoft SQL Server** - Enterprise, Windows ecosystems
- **Oracle Database** - Large enterprises, financial systems
- **SQLite** - Embedded, mobile apps, local storage

#### 2. Data Warehouses
- **Snowflake** - Cloud-native, separation of storage/compute
- **Amazon Redshift** - AWS ecosystem, petabyte-scale
- **Google BigQuery** - Serverless, analytics-focused
- **Azure Synapse Analytics** - Microsoft ecosystem
- **Teradata** - Traditional enterprise data warehousing

#### 3. NoSQL Databases
- **MongoDB** - Document store, flexible schema
- **Cassandra** - Wide-column, high write throughput
- **Redis** - In-memory, caching, real-time
- **Elasticsearch** - Search engine, log analytics
- **DynamoDB** - AWS managed NoSQL

#### 4. Time-Series Databases
- **InfluxDB** - Metrics, monitoring, IoT
- **TimescaleDB** - PostgreSQL extension for time-series
- **Prometheus** - Monitoring, Kubernetes ecosystems

#### 5. Graph Databases
- **Neo4j** - Relationship-heavy data (social networks, fraud detection)
- **Amazon Neptune** - Managed graph database

### Data Ingestion Patterns in CRISP-DM

#### Phase 2: Data Understanding
1. **Direct Database Connection**
   - Python: SQLAlchemy, psycopg2, pyodbc
   - R: DBI, RODBC, RPostgreSQL
   - Jupyter: %sql magic, ipython-sql

2. **ETL/ELT Pipelines**
   - Apache Airflow
   - dbt (data build tool)
   - Apache NiFi
   - AWS Glue / Azure Data Factory

3. **API-based Ingestion**
   - REST APIs
   - GraphQL
   - Streaming (Kafka, Kinesis)

### Considerations for Your Java Background
Your 10 years of Java experience gives you advantages:
- **JDBC knowledge** - Direct database connectivity
- **ORM experience** - Hibernate, JPA concepts translate to SQLAlchemy
- **System integration** - Understanding how databases fit in architecture
- **Performance tuning** - Query optimization experience

### Learning Path Recommendations
1. **Start with PostgreSQL + Python** - Most versatile combination
2. **Learn SQL for analytics** - Window functions, CTEs, aggregations
3. **Practice with cloud data warehouses** - Snowflake/BigQuery (free tiers)
4. **Understand data modeling** - Star/snowflake schemas for analytics

### Tools & Libraries to Learn
- **Python:** pandas, SQLAlchemy, psycopg2-binary
- **R:** dplyr, DBI, dbplyr
- **Notebooks:** Jupyter, RStudio
- **Visualization:** Tableau, Power BI, Superset

## Notes
_This file will be updated as we discuss data science and CRISP-DM methodology_