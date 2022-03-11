import glob
import logging
import string
from airflow.models import BaseOperator
from airflow.hooks.S3_hook import S3Hook
from airflow.utils.decorators import apply_defaults


class UploadFilesToS3Operator(BaseOperator):

    template_fields = ('aws_conn_id', 'bucket_name',
                       'local_files_path', 'target_files_path')

    @apply_defaults
    def __init__(self,
                 aws_conn_id='',
                 bucket_name='',
                 local_files_path='',
                 target_files_path='',
                 *args, **kwargs):

        super(UploadFilesToS3Operator, self).__init__(*args, **kwargs)
        self.aws_conn_id = aws_conn_id
        self.bucket_name = bucket_name
        self.local_files_path = local_files_path
        self.target_files_path = target_files_path

    def execute(self, context):

        s3_hook = S3Hook(aws_conn_id=self.aws_conn_id)

        s_local_files_path = f"{self.local_files_path}"
        s_target_files_path = f"{self.target_files_path}"

        self.log.info(f'starting to upload files to {self.bucket_name}...')
        self.log.info(f's_local_files_path {s_local_files_path} ...')
        self.log.info(f's_target_files_path {s_target_files_path} ...')

        file_count = 0
        for file_count, s_filepath in enumerate(glob.glob(s_local_files_path)):
            s_fname = s_filepath.split('/')[-1]
            s_s3path = s_target_files_path

            s3_hook.load_file(
                filename=s_filepath,
                bucket_name=self.bucket_name,
                replace=True,
                key=s_s3path+s_fname)

        if file_count != 0:
            self.log.info(f'uploaded {file_count + 1} files...')
        else:
            self.log.info(f'no files found for upload...')


class CopyFilesToS3Operator(BaseOperator):

    template_fields = ('aws_conn_id', 'source_bucket_key_prefix', 'dest_bucket_key_prefix',
                       'source_bucket_name', 'dest_bucket_name', 'acl_policy')

    @apply_defaults
    def __init__(self,
                 aws_conn_id='',
                 source_bucket_key_prefix='',
                 dest_bucket_key_prefix='',
                 source_bucket_name='',
                 dest_bucket_name='',
                 acl_policy='',
                 *args, **kwargs):

        super(CopyFilesToS3Operator, self).__init__(*args, **kwargs)
        self.aws_conn_id = aws_conn_id
        self.source_bucket_key_prefix = source_bucket_key_prefix
        self.dest_bucket_key_prefix = dest_bucket_key_prefix
        self.source_bucket_name = source_bucket_name
        self.dest_bucket_name = dest_bucket_name
        self.acl_policy = acl_policy

    def execute(self, context):
        s3_hook = S3Hook(aws_conn_id=self.aws_conn_id)

        self.log.info(
            f'starting to copy files from source s3 bucket {self.source_bucket_name}/{self.source_bucket_key_prefix} to destination s3 bucket {self.dest_bucket_name}/{self.dest_bucket_key_prefix}')

        keys = s3_hook.list_keys(
            self.source_bucket_name, prefix=self.source_bucket_key_prefix)

        file_count = 0
        for key in keys:
            logging.info(
                f"now processing s3://{self.source_bucket_name}/{key}")

            object_name = str(key).split('/')[-1]
            file_count = file_count + 1

            s3_hook.copy_object(
                source_bucket_name=self.source_bucket_name,
                source_bucket_key=key,
                dest_bucket_name=self.dest_bucket_name,
                dest_bucket_key=self.dest_bucket_key_prefix+object_name,
                acl_policy=self.acl_policy
            )

        if file_count != 0:
            self.log.info(f'copied {file_count} files to destination bucket')
        else:
            self.log.info(f'no files found for upload')
