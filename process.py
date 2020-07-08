import random
import time
import string
import MAPI_EACQ
import webbrowser

eacq = MAPI_EACQ.EACQ()


def gen_order_id(order_id_length=8):
    letters = string.ascii_letters + '1234567890'
    return ''.join(random.choice(letters) for i in range(order_id_length))


def send_eacq_init():
    order_id = gen_order_id()

    try:

        answer_code, init_response = eacq.init(order_id, two_step=True)

        payment_url = init_response["PaymentURL"]
        eacq.set_status(init_response["Status"])
        payment_id = init_response["PaymentId"]
        webbrowser.open_new(payment_url)
        time.sleep(20)

        get_state_response = eacq.get_state(payment_id)
        eacq.set_status(get_state_response[1]["Status"])

        return payment_id, get_state_response

    except MAPI_EACQ.WebError:
        raise MAPI_EACQ.WebError
    except MAPI_EACQ.RequestError:
        raise MAPI_EACQ.RequestError
    except MAPI_EACQ.PaymentStatusError:
        raise MAPI_EACQ.PaymentStatusError


def send_eacq_confirm(payment_id):

    try:

        answer_code, confirm_response = eacq.confirm(payment_id)
        eacq.set_status(confirm_response["Status"])

        return confirm_response

    except MAPI_EACQ.WebError:
        raise MAPI_EACQ.WebError
    except MAPI_EACQ.RequestError:
        raise MAPI_EACQ.RequestError
    except MAPI_EACQ.PaymentStatusError:
        raise MAPI_EACQ.PaymentStatusError


def send_eacq_cancel(payment_id, full_cancel=True):
    try:

        answer_code, cancel_response = eacq.cancel(payment_id)
        eacq.set_status(cancel_response["Status"])

        return cancel_response

    except MAPI_EACQ.WebError:
        raise MAPI_EACQ.WebError
    except MAPI_EACQ.RequestError:
        raise MAPI_EACQ.RequestError
    except MAPI_EACQ.PaymentStatusError:
        raise MAPI_EACQ.PaymentStatusError
