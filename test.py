import os
from uuid import uuid4
from unittest import TestCase, TestSuite, TextTestRunner
from pypaystack import Customer, Transaction, Plan

BASE_URL = "https://api.paystack.co"

test_auth_key = os.getenv('PAYSTACK_AUTHORIZATION_KEY')


class TestTransactionAPI(TestCase):
    test_amount = 1000*100
    test_email = "test_customer@mail.com"

    def setUp(self):
        super(TestTransactionAPI, self).setUp()
        TestCase.assertIsNotNone(
            test_auth_key, "PAYSTACK_AUTHORIZATION_KEY not Found")
        self.transaction = Transaction(authorization_key=test_auth_key)

    def test_charge_and_verify(self):
        def initialize_transaction():
            (status_code, status, response_msg, initialized_transaction_data) = self.transaction.initialize(
                email=self.test_email, amount=self.test_amount)
            self.assertEqual(status_code, 200)
            self.assertEqual(status, True)
            self.assertEqual(response_msg, 'Authorization URL created')
            return initialized_transaction_data

        def verify_transaction():
            (status_code, status, response_msg, response_data) = self.transaction.verify(
                reference=initialized_transaction_data['reference'])
            self.assertEqual(status_code, 200)
            self.assertEqual(status, True)
            self.assertEqual(response_msg, 'Verification successful')
            # Verification status should be failed as initialized transaction is not paid by customer
            self.assertEqual(response_data.get('customer')
                             ['email'], self.test_email)

        initialized_transaction_data = initialize_transaction()
        verify_transaction()

    def test_transaction_records(self):
        def retrieve_all_transactions():
            (status_code, status, response_msg,
             all_transactions) = self.transaction.getall()
            self.assertEqual(status_code, 200)
            self.assertEqual(status, True)
            self.assertEqual(response_msg, 'Transactions retrieved')
            self.assertIsInstance(all_transactions, list)
            return all_transactions

        def retrieve_one_transaction():
            (status_code, status, response_msg, transaction_data) = self.transaction.getone(
                transaction_id=all_transactions[0]['id'])
            self.assertEqual(status_code, 200)
            self.assertEqual(status, True)
            self.assertEqual(response_msg, 'Transaction retrieved')
            # removing authorization field for assertion test
            del transaction_data['authorization']
            self.assertDictContainsSubset(
                transaction_data, all_transactions[0])

        all_transactions = retrieve_all_transactions()
        retrieve_one_transaction()


# Todo: Finish this tests and actually test....:-(
