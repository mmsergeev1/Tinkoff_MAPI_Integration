import process


def main():
    try:
        payment_id, get_state_response = process.send_eacq_init()
        print(f'Response: {get_state_response}')
        print()
        print(f'Payment id: {payment_id}')
    except process.WebError:
        raise process.WebError
    except process.RequestError:
        raise process.RequestError

    status = process.eacq.get_status()
    print(f"Status: {status}")
    if status == 'AUTHORIZED':
        try:
            print("Status is not confirmed. Sending Confirm.")
            confirm_response = process.send_eacq_confirm(payment_id)
            print(f"Response: {confirm_response}")
        except process.WebError:
            raise process.WebError
        except process.RequestError:
            raise process.RequestError


if __name__ == '__main__':
    main()
