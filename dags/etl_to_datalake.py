import json
import os
import pathlib
import sqlparse
import yaml
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from google.oauth2 import service_account
from airflow.hooks.base_hook import BaseHook
from google.cloud import bigquery
from airflow.models import Connection


default_args = {
    'start_date': datetime(2024, 1, 6),
    'retries': 2,
    'catchup': False,
    'depends_on_past': False}

def init_bq_client():

    try:
        conn = Connection.get_connection_from_secrets(conn_id='dwh-creds')
        service_account_json = json.loads(conn.extra_dejson['keyfile_dict'])
        credentials = service_account.Credentials.from_service_account_info(
            service_account_json)
        credentials = credentials.with_scopes(["https://www.googleapis.com/auth/cloud-platform"])
        client = bigquery.Client(credentials=credentials)
    
    except Exception as e:
        raise e
    
    else:
        print("successfully created BQ client")
    
    return client

def load_query_result_to_bq(sql, write_disposition,
                            destination_table, partition_column=None):

    try:
        bq_client = init_bq_client()
        time_partitioning = bigquery.table.TimePartitioning(field=partition_column) \
            if partition_column \
                else None
        job_config = bigquery.QueryJobConfig(
            allow_large_results=True, 
            destination=destination_table,
            write_disposition=write_disposition,
            create_disposition="CREATE_IF_NEEDED",
            time_partitioning=time_partitioning)
        query_job = bq_client.query(sql, job_config=job_config)
        query_job_res = query_job.result()

    except Exception as e:
        raise e

    else:
        print(f"successfully load data to {destination_table}")

def process_datalake(path_config_yaml, path_query_sql):

    dict_config = {}
    with open(path_config_yaml) as file_config_yaml:
        config_yaml = yaml.load_all(file_config_yaml, Loader=yaml.CLoader)
        for item in config_yaml:
            dict_yaml = item
        dict_config["destination_table"] = dict_yaml.get("destination_table")
        dict_config["write_disposition"] = dict_yaml.get("write_disposition")
        dict_config["partition_column"] = dict_yaml.get("partition_column")
    
    with open(path_query_sql) as file_query_sql:
        query_sql = file_query_sql.read()
        dict_config["sql"] = sqlparse.format(query_sql, reindent=True, keyword_case='upper')
    
    load_query_result_to_bq(dict_config["sql"], dict_config["write_disposition"], 
                            dict_config["destination_table"], dict_config["partition_column"])


with DAG(
    'etl_to_datalake',
    schedule_interval='@daily',
    default_args=default_args,
    tags=['datalake']
    ) as dag:

    current_path = pathlib.Path(__file__).absolute()
    config_dir_path = current_path.parent.parent.joinpath("data/daily_datalake")
    datalake_files = os.listdir(config_dir_path)
    for datalake_file in datalake_files:
        path_config_yaml = config_dir_path.joinpath(datalake_file).joinpath('config.yaml')
        path_query_sql = config_dir_path.joinpath(datalake_file).joinpath('query.sql')
        task_process_datalake = PythonOperator(
            task_id=f'{datalake_file}',
            pool_slots=1,
            python_callable=process_datalake,
            op_kwargs={
                'path_config_yaml': path_config_yaml,
                'path_query_sql': path_query_sql
            })
