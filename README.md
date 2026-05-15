# Data Engineering Project

## Prerequisites

- Python 3.9 or higher
- pip package manager
- A text editor or IDE
- Git

## Getting Started with Databricks

### Creating a Free Databricks Account

1. Visit [databricks.com](https://databricks.com)
2. Sign up for a free community edition account
3. Verify your email and complete registration

### Generating an Access Token

1. Log in to your Databricks workspace
2. Click your **profile icon** (top right)
3. Select **User Settings**
4. Navigate to **Access tokens**
5. Click **Generate new token**
6. Copy and securely store your token
7. Add to your project's `.env` file:
    ```
    DATABRICKS_TOKEN=your_token_here
    DATABRICKS_HOST=https://your-workspace-url
    ```

## Configuring a Source

1. Create a `config/sources.yml` file
2. Define your data source:
    ```yaml
    source:
      name: my_source
      type: csv
      path: /path/to/data
    ```

## Current Functionality

This repository currently provides integration scaffolding:
- setting up Databricks access
- configuring a source definition
- creating a job script placeholder
- storing job parameters in `config/jobs.yml`

It does not yet run actual data transformations. A Python script in `jobs/` can be created and may later contain transformation logic, but the current tool is focused on simple integration setup rather than executing or managing transformations.

## Running the Project

```bash
python -m jobs.main
```
