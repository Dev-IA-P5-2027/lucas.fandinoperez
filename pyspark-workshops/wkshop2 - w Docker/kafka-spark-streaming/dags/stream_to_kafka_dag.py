from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from stream_to_kafka import start_streaming

default_args = {
    "owner": "airflow",
    "start_date": datetime(2018, 12, 21, 12, 12),
    "retries": 1,
    "retry_delay": timedelta(seconds=5),
}

with DAG(
    dag_id="random_people_names",
    default_args=default_args,
    schedule="0 1 * * *",
    catchup=False,
) as dag:
    data_stream_task = PythonOperator(
        task_id="kafka_data_stream",
        python_callable=start_streaming,
    )
