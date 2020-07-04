import random
import time
import string
import TinkoffEACQ
import webbrowser

eacq = TinkoffEACQ.EACQ()


class WebError(Exception):
    pass


class RequestError(Exception):
    pass


def gen_order_id(order_id_length=8):
    letters = string.ascii_letters + '1234567890'
    return ''.join(random.choice(letters) for i in range(order_id_length))


def send_eacq_init():
    order_id = gen_order_id()
    answer_code, init_response = eacq.init(order_id)

    if answer_code.status_code == 200 and init_response["Success"] and init_response["ErrorCode"] == '0':
        payment_url = init_response["PaymentURL"]
        eacq.set_status(init_response["Status"])
        payment_id = init_response["PaymentId"]
        webbrowser.open_new(payment_url)
        time.sleep(20)

        get_state_response = eacq.get_state(payment_id)
        eacq.set_status(get_state_response[1]["Status"])

        return payment_id, get_state_response

    elif answer_code.status_code != 200:
        raise WebError(f"Код ответа от сервера неуспешный: {answer_code}")
    elif not init_response["Success"] or init_response["ErrorCode"] != '0':
        raise RequestError(f"Запрос отбился ошибкой, код: {init_response['ErrorCode']}, "
                           f"сообщение: {init_response['Message']}")
