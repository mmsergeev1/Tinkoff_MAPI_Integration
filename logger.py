import logging


log_file_name = 'payment.log'
logging.basicConfig(level=logging.DEBUG, filename=log_file_name, filemode='a',
                        format='%(name)s - %(asctime)s.%(msecs)03d - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


def log_exception(exception, exc_info=True):
    logging.exception(exception, exc_info=exc_info)


def log_into_file(answer_code=None, response=None, method_name='', level='Debug', request_dict=None, message='None'):
    if level == 'Debug':
        logging.debug(f"Method: {method_name}")
        logging.debug(f"Request: {request_dict}")
        logging.debug(f"Answer code: {answer_code}")
        logging.debug(f"Response: {response}")
        logging.debug(f"Message: {message}")
    if level == 'Info':
        logging.info(f"Method: {method_name}")
        logging.info(f"Request: {request_dict}")
        logging.info(f"Answer code: {answer_code}")
        logging.info(f"Response: {response}")
        logging.info(f"Message: {message}")
    if level == 'Warning':
        logging.warning(f"Method: {method_name}")
        logging.warning(f"Request: {request_dict}")
        logging.warning(f"Answer code: {answer_code}")
        logging.warning(f"Response: {response}")
        logging.warning(f"Message: {message}")
    if level == 'Error':
        logging.error(f"Method: {method_name}")
        logging.error(f"Request: {request_dict}")
        logging.error(f"Answer code: {answer_code}")
        logging.error(f"Response: {response}")
        logging.error(f"Message: {message}")
    if level == 'Critical':
        logging.critical(f"Method: {method_name}")
        logging.critical(f"Request: {request_dict}")
        logging.critical(f"Answer code: {answer_code}")
        logging.critical(f"Response: {response}")
        logging.critical(f"Message: {message}")
