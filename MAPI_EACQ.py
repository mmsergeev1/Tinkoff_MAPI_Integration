import getpass
import hashlib
import json
import requests

test_terminal_key = 'TinkoffBankTest'
test_environment_url = 'https://rest-api-test.tinkoff.ru/v2/'
prod_environment_url = 'https://securepay.tinkoff.ru/v2/'
test_terminal_token_password = 'TinkoffBankTest'


def get_token(request_dict, token_password):
    request_dict["Password"] = token_password
    concatenated_token_string = ''
    for key in sorted(request_dict.keys()):
        concatenated_token_string += str(request_dict[key])
    token = hashlib.sha256(concatenated_token_string.encode('utf-8')).hexdigest()
    del request_dict["Password"]
    return token


def send_request(request_dict, request_url):
    request_json = json.dumps(request_dict)

    headers = {'Content-type': 'application/json',
               'Content-Encoding': 'utf-8'}

    server_answer = requests.post(request_url, data=request_json, headers=headers)
    response = server_answer.json()
    return server_answer, response


class WebError(Exception):
    pass


class RequestError(Exception):
    pass


class PaymentStatusError(Exception):
    pass


class EACQ:
    def __init__(self):
        self.terminal_key = ''
        self.token_password = ''
        self.receipt = {}
        self.used_url = ''
        self.data = {}
        self.description = ""
        self.status = 'None'
        self.pay_type = 'O'

    def set_status(self, new_status):
        self.status = new_status

    def set_url(self, url=test_environment_url):
        self.used_url = url
        return self.used_url

    def set_terminal(self, new_terminal_key=test_terminal_key, new_token_password=test_terminal_token_password):
        self.terminal_key = new_terminal_key
        self.token_password = new_token_password

    def get_status(self):
        return self.status

    def set_description(self, value=f"Тестовый заказ от {getpass.getuser()}"):
        self.description = value

    def set_receipt(self, receipt_email='a@test.com', company_email='b@test.ru',
                    receipt_phone='+79031234567', taxation='osn'):
        self.receipt = {
            "Email": receipt_email,
            "Phone": receipt_phone,
            "EmailCompany": company_email,
            "Taxation": taxation,
            "Items": [
                {
                    "Name": "Наименование товара 1",
                    "Price": 10000,
                    "Quantity": 1.00,
                    "Amount": 10000,
                    "PaymentMethod": "full_prepayment",
                    "PaymentObject": "commodity",
                    "Tax": "vat10",
                    "Ean13": "0123456789"
                },
                {
                    "Name": "Наименование товара 2",
                    "Price": 20000,
                    "Quantity": 2.00,
                    "Amount": 40000,
                    "PaymentMethod": "prepayment",
                    "PaymentObject": "service",
                    "Tax": "vat20"
                },
                {
                    "Name": "Наименование товара 3",
                    "Price": 30000,
                    "Quantity": 3.00,
                    "Amount": 90000,
                    "Tax": "vat10"
                }
            ]
        }  # TODO: make dynamic receipt

    def set_data(self, data_phone="+71234567890",
                 data_email=f"{getpass.getuser()}@tinkoff.ru"):
        self.data = {
            "Phone": data_phone,
            "Email": data_email
        }

    def init(self, order_id, terminal_key=test_terminal_key, token_password=test_terminal_token_password,
             amount=100, url=test_environment_url, two_step=False, init_token_required=False, recurrent=False):

        self.set_terminal(terminal_key, token_password)

        request_url = self.set_url(url) + 'Init'

        if two_step:
            self.pay_type = 'T'
        elif not two_step:
            self.pay_type = 'O'

        request_dict = {
            "TerminalKey": self.terminal_key,
            "Amount": amount,
            "OrderId": order_id,
            "PayType": self.pay_type
        }

        if recurrent:
            request_dict["Recurrent"] = 'Y'

        if self.description:
            request_dict["Description"] = self.description

        if init_token_required:
            token = get_token(request_dict, self.token_password)
            request_dict["Token"] = token

        if self.data:
            request_dict["DATA"] = self.data

        if self.receipt:
            request_dict["Receipt"] = self.receipt

        answer_code, response = send_request(request_dict, request_url)
        return answer_code, response

    def get_state(self, payment_id):
        request_url = self.used_url + 'GetState'

        request_dict = {
            "TerminalKey": self.terminal_key,
            "PaymentId": payment_id
        }

        token = get_token(request_dict, self.token_password)
        request_dict["Token"] = token

        response_list = send_request(request_dict, request_url)
        return response_list

    def confirm(self, payment_id):
        if self.status not in ['CONFIRMED', 'None']:
            request_url = self.used_url + 'Confirm'

            request_dict = {
                "TerminalKey": self.terminal_key,
                "PaymentId": payment_id
            }

            token = get_token(request_dict, self.token_password)
            request_dict["Token"] = token

            response_list = send_request(request_dict, request_url)
            return response_list
        else:
            raise PaymentStatusError(f"Status is not valid for Confirm. Status: {self.status}.")

    def cancel(self, payment_id, cancel_amount, full_cancel=True):
        if self.status in ['NEW', 'AUTHORIZED', 'CONFIRMED']:
            request_url = self.used_url + 'Cancel'

            request_dict = {
                "TerminalKey": self.terminal_key,
                "PaymentId": payment_id
            }

            if not full_cancel:
                request_dict["Amount"] = cancel_amount

            token = get_token(request_dict, self.token_password)
            request_dict["Token"] = token

            if not full_cancel:
                if self.receipt:
                    request_dict["Receipt"] = self.receipt

            response_list = send_request(request_dict, request_url)
            return response_list

        else:
            raise PaymentStatusError(f"Status is not valid for Cancel. Status: {self.status}.")

    def charge(self, payment_id, rebill_id):
        if self.status in ['NEW']:
            request_url = self.used_url + 'Charge'

            request_dict = {
                "TerminalKey": self.terminal_key,
                "PaymentId": payment_id,
                "RebillId": rebill_id
            }

            token = get_token(request_dict, self.token_password)
            request_dict["Token"] = token

            response_list = send_request(request_dict, request_url)

            return response_list
        elif self.status not in ['NEW']:
            raise PaymentStatusError(f"Status is not valid for Charge. Status: {self.status}.")