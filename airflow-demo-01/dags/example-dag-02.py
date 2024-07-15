from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.email_operator import EmailOperator
from s3_plugins import CopyFilesToS3Operator
from airflow.models import Variable
import tempfile
from datetime import datetime, date

run_date = "{{ ds }}"
temp_dir = tempfile.gettempdir()

source_bucket_key_prefix = 'kafka-s3-demo-hourly-partitioner/mockaroo.sample.events/year=2021/month=02/day=08/hour=20/'
dest_bucket_key_prefix = 'kafka-s3-demo-hourly-partitioner/mockaroo.sample.events/year=2021/month=02/day=08/hour=20/test/'
acl_policy = 'bucket-owner-full-control'

default_args = {
    'owner': 'airflow',
    'description': 'Airflow DAG to test custom s3 operators',
    'depends_on_past': True,
    'start_date': datetime(2022, 1, 1),
    'email': 'test@example.com',
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}


def branch_func(**context):

    env_code = Variable.get('ENV_CODE')

    if ((env_code == 'dev') or (env_code == 'stage') or (env_code == 'prod')):
        return 's3_copy'
    else:
        return 'dummy_task'


with DAG('example-dag-02',
         default_args=default_args,
         schedule_interval='00 1 * * *',
         catchup=False,
         max_active_runs=1) as dag:

    s3_decision_to_copy = BranchPythonOperator(
        task_id='s3_decision_to_copy',
        provide_context=True,
        python_callable=branch_func
    )

    s3_copy = CopyFilesToS3Operator(
        task_id='s3_copy',
        aws_conn_id='aws_s3_demo_connection',
        source_bucket_name=Variable.get('S3_BUCKET_FOR_DEMO'),
        dest_bucket_name=Variable.get('S3_BUCKET_FOR_DEMO'),
        source_bucket_key_prefix=source_bucket_key_prefix,
        dest_bucket_key_prefix=dest_bucket_key_prefix
    )
