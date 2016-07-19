import time

class Logger(object):
    def log_client_message(self, username, ip, port, message):
        with open('client_log', 'a') as log:
            log.write(str(msg_type) + '\t' + str(time.ctime()) + '\t' + str(username) + '\t' + str(message) + '\n')

    def log_server_message(self, msg_type, username, ip, port, message):
        with open('server_log', 'a') as log:
            log.write(str(msg_type) + '\t' + str(time.ctime()) + '\t' + str(username) + '\t' + str(ip) + '\t' + str(port) + '\t' + str(message) + '\n')
