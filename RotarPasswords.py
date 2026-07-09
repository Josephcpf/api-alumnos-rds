import boto3
import pymysql
import os
import random
import string

def generar_password(longitud=14):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))

def lambda_handler(event, context):
    connection = None

    ssm = boto3.client("ssm")

    # Parámetros desde variables de entorno
    host_param = os.environ["DB_HOST_PARAM"]
    admin_user = os.environ["DB_ADMIN_USER"]
    admin_password_param = os.environ["DB_ADMIN_PASSWORD_PARAM"]

    usuarios = ["user_dev", "user_test", "user_prod"]

    # Obtener host desde Parameter Store
    host_response = ssm.get_parameter(
        Name=host_param,
        WithDecryption=True
    )
    host = host_response["Parameter"]["Value"]

    # Obtener password del usuario administrador
    admin_password_response = ssm.get_parameter(
        Name=admin_password_param,
        WithDecryption=True
    )
    admin_password = admin_password_response["Parameter"]["Value"]

    try:
        connection = pymysql.connect(
            host=host,
            user=admin_user,
            password=admin_password,
            connect_timeout=5
        )

        with connection.cursor() as cursor:
            for usuario in usuarios:
                nuevo_password = generar_password()

                # Cambiar password en MySQL
                sql = f"ALTER USER '{usuario}'@'%' IDENTIFIED BY '{nuevo_password}';"
                cursor.execute(sql)

                # Guardar nuevo password en Parameter Store
                parametro_password = f"/rds_mysql_alumnos/{usuario}/password"

                ssm.put_parameter(
                    Name=parametro_password,
                    Value=nuevo_password,
                    Type="SecureString",
                    Overwrite=True
                )

        connection.commit()

        return {
            "statusCode": 200,
            "body": "Passwords rotados correctamente para user_dev, user_test y user_prod"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e)
        }

    finally:
        if connection:
            connection.close()
