import process
import TinkoffEACQ

eacq = TinkoffEACQ.EACQ()


def main():
    try:
        payment_id, get_state_response = process.send_eacq_init()
        print(f'Response: {get_state_response}')
        print()
        print(f'Payment id: {payment_id}')
    except process.WebError:
        raise Exception


if __name__ == '__main__':
    main()
