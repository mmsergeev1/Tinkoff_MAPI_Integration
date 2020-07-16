import getpass
import logger
import hashlib
import json
import requests


def handle_exceptions(function):
    def wrapper(*args, **kwargs):
        attempt = 0
        while True:
            try:
                function(*args, **kwargs)
            except Exception:
                attempt += 1
                if attempt > 2:
                    logger.log_exception(Exception, exc_info=True)


# Todo: use handler in functions that can catch not handled errors


def get_token(request_dict: dict, token_password: str) -> str:
    """Generates token for request signature
    https://oplata.tinkoff.ru/develop/api/request-sign/
    """
    request_dict["Password"] = token_password
    concatenated_token_string = ''
    for key in sorted(request_dict.keys()):
        concatenated_token_string += str(request_dict[key])
    token = hashlib.sha256(concatenated_token_string.encode('utf-8')).hexdigest()
    del request_dict["Password"]
    return token


def send_request(request_dict: dict, request_url: str) -> tuple:
    """Sending request using requests module"""
    request_json = json.dumps(request_dict)

    headers = {'Content-type': 'application/json',
               'Content-Encoding': 'utf-8'}

    server_answer = requests.post(request_url, data=request_json, headers=headers)
    response = server_answer.json()
    if server_answer.status_code == 200 and response["Success"] and response["ErrorCode"] == '0':
        return server_answer, response
    elif server_answer.status_code != 200:
        raise ConnectionError(f"HTTPS reason code is not successful. {server_answer}")
    elif not response["Success"] or response["ErrorCode"] != '0' or response["Message"] != 'OK':
        raise RequestError(f"Request is not successful. {response}")


class RequestError(Exception):
    pass


# TODO expand classes of exceptions


class PaymentStatusError(Exception):
    pass


class EACQ:
    test_terminal_key = 'TinkoffBankTest'
    test_environment_url = 'https://rest-api-test.tinkoff.ru/v2/'
    prod_environment_url = 'https://securepay.tinkoff.ru/v2/'
    test_terminal_token_password = 'TinkoffBankTest'

    def __init__(self):
        self.terminal_key = None
        self.token_password = None
        self.receipt = None
        self.used_payment_gate_url = None
        self.data = None
        self.description = None
        self.status = None
        self.pay_type = None

    def set_internal_payment_status(self, new_status: str) -> None:
        """Sets internal payment status in instance of class in your system
        It can be used just not to request status via API
        """
        self.status = new_status

    def set_used_payment_gate_url(self, url: str = test_environment_url) -> None:
        """Sets url of environment you used on Init"""
        self.used_payment_gate_url = url

    def get_used_payment_gate_url(self) -> str:
        """Returns url of environment that was used"""
        return self.used_payment_gate_url

    def set_used_terminal_and_token_password(self, new_terminal_key: str = test_terminal_key,
                                             new_token_password: str = test_terminal_token_password) -> None:
        """Saves used on Init terminal key and token password"""
        self.terminal_key = new_terminal_key
        self.token_password = new_token_password

    def get_used_terminal_and_token_password(self, need_token_password: bool = False):
        """Returns used on Init terminal key and token password"""
        if need_token_password:
            return self.terminal_key, self.token_password
        elif not need_token_password:
            return self.terminal_key

    def get_status(self) -> str:
        """Returns internal payment status in your system"""
        return self.status

    def set_description(self, value=f"Тестовый заказ от {getpass.getuser()}") -> None:
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

    def set_data(self, data_phone: str = "+71234567890",
                 data_email: str = f"{getpass.getuser()}@gmail.com") -> None:
        """Sets extra payment data sent to payment gateway
        https://oplata.tinkoff.ru/develop/api/payments/init-request/
        """
        self.data = {
            "Phone": data_phone,
            "Email": data_email
        }

    def init(self, order_id: str, terminal_key: str = test_terminal_key,
             token_password: str = test_terminal_token_password, amount: int = 100, url: str = test_environment_url,
             two_step:  bool = False, init_token_required: bool = False, recurrent: bool = False) -> tuple:
        """Initialises payment session
        https://oplata.tinkoff.ru/develop/api/payments/init-description/
        """
        self.set_used_terminal_and_token_password(terminal_key, token_password)

        self.set_used_payment_gate_url(url)

        request_url = self.get_used_payment_gate_url() + 'Init'

        if two_step:
            self.pay_type = 'T'
        elif not two_step:
            self.pay_type = 'O'

        request_dict = {
            "TerminalKey": self.get_used_terminal_and_token_password(),
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

        logger.log_into_file(answer_code, response, 'Init', level='Debug', request_dict=request_dict)

        return answer_code, response

    def get_state(self, payment_id: str) -> tuple:
        """Gets payment status in acquiring system of bank
        https://oplata.tinkoff.ru/develop/api/payments/getstate-description/
        """
        request_url = self.used_payment_gate_url + 'GetState'

        request_dict = {
            "TerminalKey": self.terminal_key,
            "PaymentId": payment_id
        }

        token = get_token(request_dict, self.token_password)
        request_dict["Token"] = token

        response_list = send_request(request_dict, request_url)

        logger.log_into_file(response_list[0], response_list[1], 'GetState', level='Debug', request_dict=request_dict)

        return response_list

    def confirm(self, payment_id: str) -> tuple:
        """Confirms payment and transaction
        https://oplata.tinkoff.ru/develop/api/payments/confirm-description/
        """
        if self.status not in ['CONFIRMED', 'None']:
            request_url = self.used_payment_gate_url + 'Confirm'

            request_dict = {
                "TerminalKey": self.terminal_key,
                "PaymentId": payment_id
            }

            token = get_token(request_dict, self.token_password)
            request_dict["Token"] = token

            response_list = send_request(request_dict, request_url)

            logger.log_into_file(response_list[0], response_list[1], 'Confirm', level='Debug',
                                 request_dict=request_dict)

            return response_list
        else:
            raise PaymentStatusError(f"Status is not valid for Confirm. Status: {self.status}.")

    def cancel(self, payment_id: str, cancel_amount: int = 0, full_cancel: bool = True) -> tuple:
        """Cancels payment and refunds to card
        https://oplata.tinkoff.ru/develop/api/payments/cancel-description/
        """
        if self.status in ['NEW', 'AUTHORIZED', 'CONFIRMED']:
            request_url = self.used_payment_gate_url + 'Cancel'

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

            logger.log_into_file(response_list[0], response_list[1], 'Cancel', level='Debug',
                                 request_dict=request_dict)

            return response_list

        else:
            raise PaymentStatusError(f"Status is not valid for Cancel. Status: {self.status}.")

    def charge(self, payment_id: str, rebill_id: str) -> tuple:
        """Makes recurrent payment from pre-saved card
        https://oplata.tinkoff.ru/develop/api/autopayments/charge-description/
        """
        if self.status in ['NEW']:
            request_url = self.used_payment_gate_url + 'Charge'

            request_dict = {
                "TerminalKey": self.terminal_key,
                "PaymentId": payment_id,
                "RebillId": rebill_id
            }

            token = get_token(request_dict, self.token_password)
            request_dict["Token"] = token

            response_list = send_request(request_dict, request_url)

            logger.log_into_file(response_list[0], response_list[1], 'Charge', level='Debug',
                                 request_dict=request_dict)

            return response_list
        elif self.status not in ['NEW']:
            raise PaymentStatusError(f"Status is not valid for Charge. Status: {self.status}.")
