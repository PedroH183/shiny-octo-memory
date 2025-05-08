import boto3
import os
import psycopg2
from uuid import uuid4
from datetime import datetime as dt
from abc import abstractmethod
from flask import jsonify
import logging

logger = logging.getLogger("database")


class DynamoDatabase:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")

    @abstractmethod
    def get_item(self, key):
        # Implement the logic to get an item from the DynamoDB table
        pass

    @abstractmethod
    def put_item(self, item):
        # Implement the logic to put an item into the DynamoDB table
        pass


class RDSDatabase:
    """Class to handle RDS database connection"""

    def get_pg_connection(self):
        return psycopg2.connect(
            host=os.getenv("RDS_HOST"),
            database=os.getenv("RDS_DB"),
            user=os.getenv("RDS_USER"),
            password=os.getenv("RDS_PASSWORD"),
        )


class S3Database:
    """Class to handle S3 database connection"""

    def __init__(self):
        self.s3 = boto3.client("s3")
        self.s3_bucket = os.getenv("S3_BUCKET")

    def upload(self, file_obj, bucket, key):
        self.s3.upload_fileobj(file_obj, bucket, key)


def database_accessor(func):
    """Decorator to access the database connection"""

    def wrapper(cls, *args, **kwargs):
        with RDSDatabase().get_pg_connection() as conn:
            with conn.cursor() as cursor:
                cls.cur = cursor
                return func(*args, **kwargs)

        return func(*args, **kwargs)

    return wrapper


class ProductsDatabase(DynamoDatabase, RDSDatabase):
    def __init__(self):
        super().__init__()
        self.products_table = self.dynamodb.Table("Products")  # type: ignore

    @database_accessor
    def get_item(self, product_id):
        item = self.products_table.get_item(Key=product_id)  # type: ignore

        if not item:
            return jsonify({"error": "Product not found"}), 404

        self.cur.execute(  # type: ignore
            "INSERT INTO access_logs (product_id, action, timestamp) VALUES (%s, %s, %s)",
            (product_id, "CREATE", dt.now()),
        )
        return jsonify(item)

    @database_accessor
    def put_item(self, item_json: dict):
        """Insert a new item into the DynamoDB table"""

        logger.warning("0o0o0o0o0o Creating new product. 0o0o0o00o0o0o0o")

        name = str(item_json.get("name", None))
        image = str(item_json.get("image", None))
        description = str(item_json.get("description", None))

        if not all([name, description, image]):
            return jsonify({"error": "Missing fields"}), 400

        product_id = str(uuid4())
        image_key = f"products/{product_id}/{name}.jpg"

        s3_bucket_name = os.getenv("S3_BUCKET")

        S3Database().upload(image, s3_bucket_name, image_key)
        image_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{image_key}"

        self.products_table.put_item(
            Item={
                "id": product_id,
                "name": name,
                "image_url": image_url,
                "description": description,
            }
        )

        self.cur.execute(  # type: ignore
            "INSERT INTO access_logs (product_id, action, timestamp) VALUES (%s, %s, %s)",
            (product_id, "CREATE", dt.now()),
        )

        return jsonify({"message": "Product created successfully"}), 201


class AccessLogsDatabase(DynamoDatabase):
    def __init__(self):
        super().__init__()
        self.logs_table = self.dynamodb.Table("AccessLogs")  # type: ignore

    def get_item(self, key):
        """Get an item from the DynamoDB table"""
        raise NotImplementedError("This method is not implemented yet.")

    @database_accessor
    def get_logs(self):
        """Get access logs from the database"""
        logger.warning("0o0o0o0o0o Getting access logs. 0o0o0o00o0o0o0o")

        self.cur.execute(  # type: ignore
            "SELECT * FROM access_logs ORDER BY timestamp DESC LIMIT 50"
        )
        logs = self.cur.fetchall()  # type: ignore

        if not logs:
            return jsonify({"error": "No logs found"}), 404

        logs_list = []
        for log in logs:
            logs_list.append(
                {
                    "id":         log[0],
                    "product_id": log[1],
                    "action":     log[2],
                    "timestamp":  log[3],
                }
            )
        return jsonify(logs_list), 200
