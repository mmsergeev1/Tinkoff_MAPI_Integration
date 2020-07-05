import random
import time
import string
import TinkoffEACQ
import webbrowser

eacq = TinkoffEACQ.EACQ()
WebError = TinkoffEACQ.WebError
RequestError = TinkoffEACQ.RequestError


def gen_order_id(order_id_length=8):
    letters = string.ascii_letters + '1234567890'
    return ''.join(random.choice(letters) for i in range(order_id_length))


def send_eacq_init():
    order_id = gen_order_id()
    answer_code, init_response = eacq.init(order_id, two_step=True)

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


def send_eacq_confirm(payment_id):
    answer_code, confirm_response = eacq.confirm(payment_id)
    if answer_code.status_code == 200 and confirm_response["Success"] and confirm_response["ErrorCode"] == '0':
        eacq.set_status(confirm_response["Status"])

        return confirm_response

    elif answer_code.status_code != 200:
        raise WebError(f"Код ответа от сервера неуспешный: {answer_code}")
    elif not confirm_response["Success"] or confirm_response["ErrorCode"] != '0':
        raise RequestError(f"Запрос отбился ошибкой, код: {confirm_response['ErrorCode']}, "
                           f"сообщение: {confirm_response['Message']}")
