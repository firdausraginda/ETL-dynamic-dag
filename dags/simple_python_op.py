# Import DAG object
from airflow.models import DAG
# Import the PythonOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import pandas as pd

# Define the default_args dictionary
default_args = {
  'owner': 'airflow',
  'start_date': datetime(year=2021, month=1, day=1),
  'retries': 2,
}

def print_string(message):
    df = pd.DataFrame(data={"msg": [message]})
    print(df.head())

with DAG(
    # Define DAG id
    'simple_python_operator',
    default_args=default_args,
    description='echoing simple string',
    tags=['explore-airflow', 'python-operator'],
    # To enabled/disabled backfilling, set the catchup property
    catchup=False,
    schedule_interval='@daily'
) as dag:
    first_task = PythonOperator(
        task_id='first_task',
        python_callable=print_string,
        op_kwargs={'message': 'This message will shown in logs'},
        dag=dag
    )

    # Define task depedencies
    first_task
