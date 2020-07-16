import logger
import random
import time
import string
import MAPI_EACQ
import webbrowser

eacq = MAPI_EACQ.EACQ()


def gen_order_id(order_id_length: int = 8) -> str:
    """Returns random string of len=order_id_length.
    It can be used as order id"""
    letters = string.ascii_letters + '1234567890'
    return ''.join(random.choice(letters) for i in range(order_id_length))


def send_eacq_init() -> tuple:
    """Sends Init and handles possible answers and exceptions.
    Can be used as example of realization only.
    """
    order_id = gen_order_id()

    try:

        answer_code, init_response = eacq.init(order_id, two_step=True)

        payment_url = init_response["PaymentURL"]
        eacq.set_internal_payment_status(init_response["Status"])
        payment_id = init_response["PaymentId"]
        webbrowser.open_new(payment_url)
        time.sleep(20)

        get_state_response = eacq.get_state(payment_id)
        eacq.set_internal_payment_status(get_state_response[1]["Status"])

        return payment_id, get_state_response

    except ConnectionError:
        logger.log_into_file('send_eacq_init', 'Error', message='Connection error')
        logger.log_exception(ConnectionError, exc_info=True)
    except MAPI_EACQ.RequestError:
        logger.log_into_file('send_eacq_init', 'Error', message='Request was not successful')
        logger.log_exception(MAPI_EACQ.RequestError, exc_info=True)
    except MAPI_EACQ.PaymentStatusError:
        logger.log_into_file('send_eacq_init', 'Error', message='Connection error')
        logger.log_exception(MAPI_EACQ.PaymentStatusError, exc_info=True)


def send_eacq_confirm(payment_id: str) -> dict:
    """
    Sends Confirm and handles possible answers and exceptions.
    Can be used as example of realization only.

    :param payment_id: str
    :return: payment gateway response dictionary
    """

    try:

        answer_code, confirm_response = eacq.confirm(payment_id)
        eacq.set_internal_payment_status(confirm_response["Status"])

        return confirm_response

    except ConnectionError:
        logger.log_into_file('send_eacq_confirm', 'Error', message='Connection error')
        logger.log_exception("Exception occurred", exc_info=True)
    except MAPI_EACQ.RequestError:
        logger.log_into_file('send_eacq_init', 'Error', message='Request was not successful')
        logger.log_exception(MAPI_EACQ.RequestError, exc_info=True)
    except MAPI_EACQ.PaymentStatusError:
        logger.log_into_file('send_eacq_init', 'Error', message='Connection error')
        logger.log_exception(MAPI_EACQ.PaymentStatusError, exc_info=True)


def send_eacq_cancel(payment_id: str) -> dict:
    """
    Sends Cancel and handles possible answers and exceptions.
    Can be used as example of realization only.

    :param payment_id: str
    :return: payment gateway response dictionary
    """
    try:

        answer_code, cancel_response = eacq.cancel(payment_id, full_cancel=True)
        eacq.set_internal_payment_status(cancel_response["Status"])

        return cancel_response

    except ConnectionError:
        logger.log_into_file('send_eacq_cancel', 'Error', message='Connection error')
        logger.log_exception("Exception occurred", exc_info=True)
    except MAPI_EACQ.RequestError:
        logger.log_into_file('send_eacq_init', 'Error', message='Request was not successful')
        logger.log_exception(MAPI_EACQ.RequestError, exc_info=True)
    except MAPI_EACQ.PaymentStatusError:
        logger.log_into_file('send_eacq_init', 'Error', message='Connection error')
        logger.log_exception(MAPI_EACQ.PaymentStatusError, exc_info=True)
