FROM apache/airflow:2.8.0-python3.8

# INSTALL PYTHON REQUIREMENTS
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# AIRFLOW CONFIGURATION
ENV AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG=3
ENV AIRFLOW__CORE__PARALLELISM=4
ENV AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG=10

ENV AIRFLOW__WEBSERVER__DEFAULT_UI_TIMEZONE=Asia/Jakarta

ENV AIRFLOW__SCHEDULER__MIN_FILE_PROCESS_INTERVAL=30
ENV AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL=120
