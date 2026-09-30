from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from email_alert import send_email_failure_alert

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'email_on_failure': False,  # Tat co mac dinh, dung custom callback ben duoi
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
    'on_failure_callback': send_email_failure_alert,  # <-- Tu dong gui mail khi bat ky task nao fail
}

def log_pipeline_start():
    print(">>> [Pipeline Event] Bat dau chu trinh E-Commerce Data Lakehouse Pipeline...")

with DAG(
    dag_id='ecom_unified_lakehouse_orchestration',
    default_args=default_args,
    description='Automated End-to-End E-Commerce Data Pipeline',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['ecommerce', 'lakehouse', 'dbt'],
) as dag:

    task_notify_start = PythonOperator(
        task_id='notify_pipeline_start',
        python_callable=log_pipeline_start
    )

    task_dbt_run = BashOperator(
        task_id='dbt_run_transformation',
        bash_command='cd /opt/airflow/dbt_ecom && dbt run --profiles-dir .'
    )

    task_dbt_snapshot = BashOperator(
        task_id='dbt_snapshot_orders',
        bash_command='cd /opt/airflow/dbt_ecom && dbt snapshot --profiles-dir .'
    )

    task_dbt_test = BashOperator(
        task_id='dbt_test_quality',
        bash_command='cd /opt/airflow/dbt_ecom && dbt test --profiles-dir .'
    )

    task_notify_start >> task_dbt_run >> task_dbt_snapshot >> task_dbt_test