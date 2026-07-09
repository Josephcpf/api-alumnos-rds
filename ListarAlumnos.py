import boto3
import pymysql
import os
import json

def lambda_handler(event, context):
    connection = None

    # Variables de entorno
    secret_name = os.environ['DB_SECRET_NAME']
    user = os.environ['DB_USER']
    database = os.environ['DB_NAME']

    # Recuperar secreto desde AWS Secrets Manager
    secrets_client = boto3.client('secretsmanager')

    response = secrets_client.get_secret_value(
        SecretId=secret_name
    )

    secret = json.loads(response['SecretString'])

    host = secret['host']
    password = secret['password']

    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=database,
            connect_timeout=5
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM alumnos;")
            results = cursor.fetchall()

        return {
            "statusCode": 200,
            "body": str(results)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e)
        }

    finally:
        if connection:
            connection.close()
