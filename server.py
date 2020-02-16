from concurrent import futures
import grpc
import helloworld_pb2
import helloworld_pb2_grpc
import mysql.connector
from mysql.connector import Error

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        try:
            mydb = mysql.connector.connect(host="localhost",user="root",passwd="",database='grpc')
            cursor = mydb.cursor(buffered=True)
            sql_select_query = """select * from grpc_data where client_response = %s"""
            cursor.execute(sql_select_query, (request.name,))
            row = cursor.fetchone()
            if row:
                response_client=helloworld_pb2.HelloReply(error_messages='user, %s! Already Exist' % request.name)
            else:
                response_client=helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)
                cursor.execute("INSERT INTO grpc_data(client_response,server_response) VALUES (%s,%s)",(str(request.name),str(response_client)))
                mydb.commit()
        except mysql.connector.Error as error:
            print("Failed to get record from MySQL table: {}".format(error))
        return response_client

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()