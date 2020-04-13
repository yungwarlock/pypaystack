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


class TestCustomerAPI(TestCase):

    def setUp(self):
        super(TestCustomerAPI, self).setUp()
        self.assertIsNotNone(test_auth_key)
        self.customer = Customer(authorization_key=test_auth_key)

    def test_customer_setup_and_update(self):
        # using random generator for email id to ensure email is unique, thus ensuring success on retests
        user_email = f"{uuid4()}@mail.com"
        user_data = {"email": user_email,
                     "first_name": "Test",
                     "last_name": "Customer",
                     "phone": "08012345678"}
        updated_user_data = {
            "email": user_email,
            "first_name": "Updated",
            "last_name": "Customer",
            "phone": "080987654321"}

        def create_customer():
            (status_code, status, response_msg, created_customer_data) = self.customer.create(
                email=user_data['email'], first_name=user_data['first_name'], last_name=user_data['last_name'], phone=user_data['phone'])
            self.assertEqual(status_code, 200)
            self.assertEqual(status, True)
            self.assertEqual(response_msg, 'Customer created')
            self.assertDictContainsSubset(user_data, created_customer_data)
            return created_customer_data

        def update_customer():
            (status_code, status, response_msg, updated_customer_data) = self.customer.update(user_id=created_customer_data['id'],
                                                                                              email=user_data['email'],
                                                                                              first_name=updated_user_data[
                'first_name'],
                last_name=updated_user_data['last_name'],
                phone=updated_user_data['phone'])
            self.assertEqual(status_code, 200)
            self.assertEqual(status, True)
            self.assertEqual(response_msg, 'Customer updated')
            self.assertDictContainsSubset(
                updated_user_data, updated_customer_data)

        created_customer_data = create_customer()
        update_customer()

    def test_customers_records(self):
        def retrieve_all_customers():
            (status_code, status, response_msg,
             customers_list) = self.customer.getall()
            self.assertEqual(status_code, 200)
            self.assertEqual(status, True)
            self.assertEqual(response_msg, 'Customers retrieved')
            self.assertIsInstance(customers_list, list)
            return customers_list

        def retrieve_one_customer():
            customer = customers_list[0]
            (status_code, status, response_msg,
             customer_data) = self.customer.getone(customer['id'])
            self.assertEqual(status_code, 200)
            self.assertEqual(status, True)
            self.assertEqual(response_msg, 'Customer retrieved')
            self.assertDictContainsSubset(customer, customer_data)
            pass

        customers_list = retrieve_all_customers()
        retrieve_one_customer()


# Todo: Finish this tests and actually test....:-(
