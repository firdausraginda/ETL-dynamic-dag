# Import DAG object
from airflow.models import DAG
# Import the BashOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime

# Define the default_args dictionary
default_args = {
  'owner': 'airflow',
  'start_date': datetime(year=2023, month=12, day=26),
  'retries': 2,
}

with DAG(
    # Define DAG id
    'simple_bash_operator',
    default_args=default_args,
    description='echoing simple string',
    tags=['explore-airflow', 'bash-operator'],
    # To enabled/disabled backfilling, set the catchup property
    catchup=False,
    schedule_interval='@daily'
) as dag:

    # Define the BashOperator
    first_task = BashOperator(
        task_id='first_task',
        # Define the bash_command
        bash_command='echo "testing first bash operator"',
        dag=dag
    )

    # Define the BashOperator 
    second_task = BashOperator(
        task_id='second_task',
        # Define the bash_command
        bash_command='echo "testing second bash operator"',
        dag=dag
    )

    # Define task depedencies
    first_task >> second_task