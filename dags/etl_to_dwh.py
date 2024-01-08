import json
import os
import pathlib
import sqlparse
import yaml
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor
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
        client = bigquery.Client(credentials=credentials,
                                project=credentials.project_id)

        client = bigquery.Client(credentials=credentials)
    
    except Exception as e:
        raise e
    
    else:
        print("successfully created BQ client")
    
    return client

def load_query_result_to_bq(dict_config):

    try:
        bq_client = init_bq_client()
        time_partitioning = bigquery.table.TimePartitioning(field=dict_config["partition_column"]) \
            if dict_config["partition_column"] \
                else None
        job_config = bigquery.QueryJobConfig(
            allow_large_results=True, 
            destination=dict_config['destination_table'],
            write_disposition=dict_config["write_disposition"],
            create_disposition="CREATE_IF_NEEDED",
            time_partitioning=time_partitioning)
        query_job = bq_client.query(dict_config["sql_query"], job_config=job_config)
        query_job_res = query_job.result()

    except Exception as e:
        raise e

    else:
        print(f"successfully load data to {dict_config['destination_table']}")

def get_config_yaml(path_config_yaml):
    
    with open(path_config_yaml) as file_config_yaml:
        config_yaml = yaml.load_all(file_config_yaml, Loader=yaml.CLoader)
        for item in config_yaml:
            dict_yaml = item
        
        dict_config = {}
        dict_config["destination_table"] = dict_yaml.get("destination_table")
        dict_config["write_disposition"] = dict_yaml.get("write_disposition")
        dict_config["partition_column"] = dict_yaml.get("partition_column")
        dict_config["external_task_dependencies"] = dict_yaml.get("external_task_dependencies")
        dict_config["internal_task_dependencies"] = dict_yaml.get("internal_task_dependencies")

    return dict_config

def get_query_sql(path_query_sql):

    with open(path_query_sql) as file_query_sql:
        str_query_sql = file_query_sql.read()
        str_query_parsed = sqlparse.format(str_query_sql, reindent=True, keyword_case='upper')

    return str_query_parsed


with DAG(
    "etl_to_dwh",
    schedule_interval="0 2 * * *",
    default_args=default_args,
    tags=["dwh"]
    ) as dag:

    list_dict_task_dwh = []
    current_path = pathlib.Path(__file__).absolute()
    config_dir_path = current_path.parent.parent.joinpath("data/daily_dwh")
    dwh_files = os.listdir(config_dir_path)
    for dwh_file in dwh_files:
        path_config_yaml = config_dir_path.joinpath(dwh_file).joinpath('config.yaml')
        path_config_query = config_dir_path.joinpath(dwh_file).joinpath('query.sql')
        dict_config = get_config_yaml(path_config_yaml)
        dict_config["sql_query"] = get_query_sql(path_config_query)

        task_dwh = PythonOperator(
            task_id=f'{dwh_file}',
            pool_slots=1,
            python_callable=load_query_result_to_bq,
            op_kwargs={
                "dict_config": dict_config
            })

        list_dict_task_dwh.append({
            "task_dwh": task_dwh,
            "list_internal_task_dependency": dict_config["internal_task_dependencies"]
        })

        if dict_config["external_task_dependencies"]:
            for ext_task_depen in dict_config["external_task_dependencies"]:
                task_wait_ext_depen = ExternalTaskSensor(
                    task_id=f'wait_{ext_task_depen["dag_id"]}_{ext_task_depen["task_id"]}',
                    external_dag_id=ext_task_depen["dag_id"],
                    external_task_id=ext_task_depen["task_id"],
                    allowed_states=["success"],
                    execution_delta=timedelta(minutes=ext_task_depen["minute_delta"])
                )

                task_dwh.set_upstream(task_wait_ext_depen)

    for dict_task_dwh in list_dict_task_dwh:
        list_dependency = [item["task_dwh"] for item in list_dict_task_dwh if item["task_dwh"].task_id in dict_task_dwh["list_internal_task_dependency"]]
        dict_task_dwh["task_dwh"].set_upstream(list_dependency)