- [DEMO-02 - Airflow Manual Install](#demo-02---airflow-manual-install)
  - [Airflow Setup](#airflow-setup)

# DEMO-02 - Airflow Manual Install 

## Airflow Setup

- Install Python 3.6+

- Install System dependencies
  ```bash
  sudo apt-get install -y --no-install-recommends \
        freetds-bin \
        krb5-user \
        ldap-utils \
        libffi6 \
        libsasl2-2 \
        libsasl2-modules \
        libssl1.1 \
        locales  \
        lsb-release \
        sasl2-bin \
        sqlite3 \
        unixodbc
  ```
  
  - Installing Apache Airflow
  ```bash
  pip install apache-airflow --constraint https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt
  ```

  - Initialize Airflow
    ```bash
    export AIRFLOW_HOME=/opt/airflow
    airflow db init
    ```