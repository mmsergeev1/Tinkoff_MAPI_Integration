import process


def main():
    payment_id, get_state_response = process.send_eacq_init()
    print(f'Response: {get_state_response}')
    print()
    print(f'Payment id: {payment_id}')

    status = process.eacq.get_status()
    print(f"Status: {status}")
    if status == 'AUTHORIZED':
        print("Status is not confirmed. Sending Confirm.")
        confirm_response = process.send_eacq_confirm(payment_id)
        print(f"Response: {confirm_response}")

    status = process.eacq.get_status()
    print(f"Status: {status}")
    if status == 'CONFIRMED':
        print('Cancelling')
        cancel_response = process.send_eacq_cancel(payment_id)
        print(f"Response: {cancel_response}")

    status = process.eacq.get_status()
    print(f"Status: {status}")


if __name__ == '__main__':
    main()
