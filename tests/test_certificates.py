# Test all certificate combinations (rsa-rsa, rsa-dsa, dsa-rsa, etc.)
# Random values for fields, push specifications
# All exceptions
# to/from file and string
# Generated by ssh-keygen and decoded by script, created by script and verified by ssh-keygen

import os
import random
import shutil
import unittest

import faker

import src.sshkey_tools.cert as _CERT
import src.sshkey_tools.exceptions as _EX
import src.sshkey_tools.fields as _FIELD
import src.sshkey_tools.keys as _KEY

CERTIFICATE_TYPES = ["rsa", "dsa", "ecdsa", "ed25519"]


class TestCertificateFields(unittest.TestCase):
    def setUp(self):
        self.faker = faker.Faker()
        self.rsa_key = _KEY.RsaPrivateKey.generate(1024)
        self.dsa_key = _KEY.DsaPrivateKey.generate()
        self.ecdsa_key = _KEY.EcdsaPrivateKey.generate()
        self.ed25519_key = _KEY.Ed25519PrivateKey.generate()

    def assertRandomResponse(self, field_class, values=None, random_function=None):
        if values is None:
            values = [random_function() for _ in range(100)]

        fields = []

        bytestring = b""
        for value in values:
            bytestring += field_class.encode(value)

            field = field_class(value)
            fields.append(field)

        self.assertEqual(bytestring, b"".join(bytes(x) for x in fields))

        decoded = []
        while bytestring != b"":
            decode, bytestring = field_class.decode(bytestring)
            decoded.append(decode)

        self.assertEqual(decoded, values)

    def assertExpectedResponse(self, field_class, input, expected_output):
        self.assertEqual(field_class.encode(input), expected_output)

    def assertFieldContainsException(self, field, exception):
        for item in field.exception:
            if isinstance(item, exception):
                return True

        return False

    def test_boolean_field(self):
        self.assertRandomResponse(
            _FIELD.BooleanField, random_function=lambda: self.faker.pybool()
        )

    def test_invalid_boolean_field(self):
        field = _FIELD.BooleanField("SomeInvalidData")
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_bytestring_field(self):
        self.assertRandomResponse(
            _FIELD.BytestringField,
            random_function=lambda: self.faker.pystr(1, 100).encode("utf-8"),
        )

    def test_invalid_bytestring_field(self):
        field = _FIELD.BytestringField(ValueError)
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_string_field(self):
        self.assertRandomResponse(
            _FIELD.StringField, random_function=lambda: self.faker.pystr(1, 100)
        )

    def test_invalid_string_field(self):
        field = _FIELD.StringField(ValueError)
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_integer32_field(self):
        self.assertRandomResponse(
            _FIELD.Integer32Field,
            random_function=lambda: random.randint(2**2, 2**32),
        )

    def test_invalid_integer32_field(self):
        field = _FIELD.Integer32Field(ValueError)
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        field = _FIELD.Integer32Field(_FIELD.MAX_INT32 + 1)
        field.validate()

        self.assertFieldContainsException(field, _EX.IntegerOverflowException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_integer64_field(self):
        self.assertRandomResponse(
            _FIELD.Integer64Field,
            random_function=lambda: random.randint(2**32, 2**64),
        )

    def test_invalid_integer64_field(self):
        field = _FIELD.Integer64Field(ValueError)
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        field = _FIELD.Integer64Field(_FIELD.MAX_INT64 + 1)
        field.validate()

        self.assertFieldContainsException(field, _EX.IntegerOverflowException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_datetime_field(self):
        self.assertRandomResponse(
            _FIELD.DateTimeField, random_function=lambda: self.faker.date_time()
        )

    def test_invalid_datetime_field(self):
        field = _FIELD.DateTimeField(ValueError)
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_mp_integer_field(self):
        self.assertRandomResponse(
            _FIELD.MpIntegerField,
            random_function=lambda: random.randint(2**128, 2**512),
        )

    def test_invalid_mp_integer_field(self):
        field = _FIELD.MpIntegerField(ValueError)
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        field = _FIELD.MpIntegerField("InvalidData")
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_list_field(self):
        self.assertRandomResponse(
            _FIELD.ListField,
            random_function=lambda: [self.faker.pystr(0, 100) for _ in range(10)],
        )

    def test_invalid_list_field(self):
        field = _FIELD.ListField(ValueError)
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        field = _FIELD.ListField([ValueError, ValueError, ValueError])
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_key_value_field(self):
        self.assertRandomResponse(
            _FIELD.KeyValueField,
            random_function=lambda: {
                self.faker.pystr(1, 10): self.faker.pystr(1, 100) for _ in range(10)
            },
        )

    def test_invalid_key_value_field(self):
        field = _FIELD.KeyValueField(ValueError)
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        field = _FIELD.KeyValueField([ValueError, ValueError, ValueError])
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_pubkey_type_field(self):
        allowed_values = (
            (
                "ssh-rsa-cert-v01@openssh.com",
                b"\x00\x00\x00\x1cssh-rsa-cert-v01@openssh.com",
            ),
            (
                "rsa-sha2-256-cert-v01@openssh.com",
                b"\x00\x00\x00!rsa-sha2-256-cert-v01@openssh.com",
            ),
            (
                "rsa-sha2-512-cert-v01@openssh.com",
                b"\x00\x00\x00!rsa-sha2-512-cert-v01@openssh.com",
            ),
            (
                "ssh-dss-cert-v01@openssh.com",
                b"\x00\x00\x00\x1cssh-dss-cert-v01@openssh.com",
            ),
            (
                "ecdsa-sha2-nistp256-cert-v01@openssh.com",
                b"\x00\x00\x00(ecdsa-sha2-nistp256-cert-v01@openssh.com",
            ),
            (
                "ecdsa-sha2-nistp384-cert-v01@openssh.com",
                b"\x00\x00\x00(ecdsa-sha2-nistp384-cert-v01@openssh.com",
            ),
            (
                "ecdsa-sha2-nistp521-cert-v01@openssh.com",
                b"\x00\x00\x00(ecdsa-sha2-nistp521-cert-v01@openssh.com",
            ),
            (
                "ssh-ed25519-cert-v01@openssh.com",
                b"\x00\x00\x00 ssh-ed25519-cert-v01@openssh.com",
            ),
        )

        for value in allowed_values:
            self.assertExpectedResponse(_FIELD.PubkeyTypeField, value[0], value[1])

    def test_invalid_pubkey_type_field(self):
        field = _FIELD.PubkeyTypeField("HelloWorld")
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_nonce_field(self):
        randomized = _FIELD.NonceField(_FIELD.NonceField.DEFAULT())
        randomized.validate()

        self.assertEqual(randomized.exception, (True, True, True))

        specific = (
            "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz",
            b"\x00\x00\x004abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz",
        )

        self.assertExpectedResponse(_FIELD.NonceField, specific[0], specific[1])

    def test_pubkey_class_assignment(self):
        rsa_field = _FIELD.PublicKeyField.from_object(self.rsa_key.public_key)
        dsa_field = _FIELD.PublicKeyField.from_object(self.dsa_key.public_key)
        ecdsa_field = _FIELD.PublicKeyField.from_object(self.ecdsa_key.public_key)
        ed25519_field = _FIELD.PublicKeyField.from_object(self.ed25519_key.public_key)

        self.assertIsInstance(rsa_field, _FIELD.RsaPubkeyField)
        self.assertIsInstance(dsa_field, _FIELD.DsaPubkeyField)
        self.assertIsInstance(ecdsa_field, _FIELD.EcdsaPubkeyField)
        self.assertIsInstance(ed25519_field, _FIELD.Ed25519PubkeyField)

        self.assertTrue(rsa_field.validate())
        self.assertTrue(dsa_field.validate())
        self.assertTrue(ecdsa_field.validate())
        self.assertTrue(ed25519_field.validate())

    def assertPubkeyOutput(self, key_class, *opts):
        key = getattr(
            self, key_class.__name__.replace("PrivateKey", "").lower() + "_key"
        ).public_key
        raw_start = key.raw_bytes()
        field = _FIELD.PublicKeyField.from_object(key)
        byte_data = bytes(field)
        decoded = field.decode(byte_data)[0]

        self.assertTrue(field.validate())

        self.assertEqual(raw_start, decoded.raw_bytes())

        self.assertEqual(
            f'{key.__class__.__name__.replace("PublicKey", "")} {key.get_fingerprint()}',
            str(field),
        )

    def test_rsa_pubkey_output(self):
        self.assertPubkeyOutput(_KEY.RsaPrivateKey, 1024)

    def test_dsa_pubkey_output(self):
        self.assertPubkeyOutput(_KEY.DsaPrivateKey)

    def test_ecdsa_pubkey_output(self):
        self.assertPubkeyOutput(_KEY.EcdsaPrivateKey)

    def test_ed25519_pubkey_output(self):
        self.assertPubkeyOutput(_KEY.Ed25519PrivateKey)

    def test_serial_field(self):
        self.assertRandomResponse(
            _FIELD.SerialField, random_function=lambda: random.randint(0, 2**64 - 1)
        )

    def test_invalid_serial_field(self):
        field = _FIELD.SerialField("abcdefg")
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        field = _FIELD.SerialField(random.randint(2**65, 2**66))
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_certificate_type_field(self):
        self.assertExpectedResponse(_FIELD.CertificateTypeField, 1, b"\x00\x00\x00\x01")

        self.assertExpectedResponse(_FIELD.CertificateTypeField, 2, b"\x00\x00\x00\x02")

        self.assertExpectedResponse(
            _FIELD.CertificateTypeField, _FIELD.CERT_TYPE.USER, b"\x00\x00\x00\x01"
        )

        self.assertExpectedResponse(
            _FIELD.CertificateTypeField, _FIELD.CERT_TYPE.HOST, b"\x00\x00\x00\x02"
        )

    def test_invalid_certificate_field(self):
        field = _FIELD.CertificateTypeField(ValueError)
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        field = _FIELD.CertificateTypeField(3)
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        field = _FIELD.CertificateTypeField(0)
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_key_id_field(self):
        self.assertRandomResponse(
            _FIELD.KeyIdField, random_function=lambda: self.faker.pystr(8, 128)
        )

    def test_invalid_key_id_field(self):
        field = _FIELD.KeyIdField("")
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_principals_field(self):
        self.assertRandomResponse(
            _FIELD.PrincipalsField,
            random_function=lambda: [self.faker.pystr(8, 128) for _ in range(20)],
        )

        comparison = [self.faker.pystr(8, 128) for _ in range(20)]

        self.assertExpectedResponse(
            _FIELD.PrincipalsField, comparison, _FIELD.ListField.encode(comparison)
        )

    def test_invalid_principals_field(self):
        field = _FIELD.PrincipalsField([ValueError, ValueError, ValueError])
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_validity_start_field(self):
        self.assertRandomResponse(
            _FIELD.ValidAfterField, random_function=lambda: self.faker.date_time()
        )

    def test_invalid_validity_start_field(self):
        field = _FIELD.ValidAfterField(ValueError)
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_validity_end_field(self):
        self.assertRandomResponse(
            _FIELD.ValidBeforeField, random_function=lambda: self.faker.date_time()
        )

    def test_invalid_validity_end_field(self):
        field = _FIELD.ValidBeforeField(ValueError)
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_critical_options_field(self):
        valid_opts_dict = {
            "force-command": "sftp-internal",
            "source-address": "1.2.3.4/8,5.6.7.8/16",
            "verify-required": "",
        }

        valid_opts_list = ["force-command", "source-address", "verify-required"]

        verify_dict = _FIELD.CriticalOptionsField(valid_opts_dict)
        verify_list = _FIELD.CriticalOptionsField(valid_opts_list)

        encoded_dict = _FIELD.CriticalOptionsField.encode(valid_opts_dict)
        encoded_list = _FIELD.CriticalOptionsField.encode(valid_opts_list)

        decoded_dict = _FIELD.CriticalOptionsField.decode(encoded_dict)[0]
        decoded_list = _FIELD.CriticalOptionsField.decode(encoded_list)[0]

        self.assertTrue(verify_dict.validate())
        self.assertTrue(verify_list.validate())

        self.assertEqual(valid_opts_dict, decoded_dict)

        self.assertEqual(valid_opts_list, decoded_list)

    def test_invalid_critical_options_field(self):
        field = _FIELD.CriticalOptionsField([ValueError, "permit-pty", "unpermit"])
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        field = _FIELD.CriticalOptionsField("InvalidData")
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        field = _FIELD.CriticalOptionsField(["no-touch-required", "InvalidOption"])
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_extensions_field(self):
        valid_values = [
            "no-touch-required",
            "permit-X11-forwarding",
            "permit-agent-forwarding",
            "permit-port-forwarding",
            "permit-pty",
            "permit-user-rc",
        ]

        self.assertRandomResponse(
            _FIELD.ExtensionsField,
            values=[
                valid_values[0 : random.randint(1, len(valid_values))]
                for _ in range(10)
            ],
        )

    def test_invalid_extensions_field(self):
        field = _FIELD.CriticalOptionsField([ValueError, "permit-pty", b"unpermit"])
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        field = _FIELD.CriticalOptionsField("InvalidData")
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        field = _FIELD.CriticalOptionsField(["no-touch-required", "InvalidOption"])
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def test_reserved_field(self):
        self.assertExpectedResponse(_FIELD.ReservedField, "", b"\x00\x00\x00\x00")

    def test_invalid_reserved_field(self):
        field = _FIELD.ReservedField("InvalidData")
        field.validate()

        self.assertFieldContainsException(field, _EX.InvalidDataException)

        with self.assertRaises(_EX.InvalidDataException):
            field.encode(ValueError)

    def assertCAPubkeyField(self, type):
        key = getattr(self, f"{type}_key").public_key
        field = _FIELD.CAPublicKeyField.from_object(key)
        encoded = bytes(field)
        decoded = field.decode(encoded)[0]

        self.assertEqual(key.raw_bytes(), decoded.raw_bytes())

        self.assertEqual(f"{type.upper()} {key.get_fingerprint()}", str(field))


class TestCertificates(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir("tests/certificates"):
            os.mkdir("tests/certificates")

        self.faker = faker.Faker()

        self.rsa_ca = _KEY.RsaPrivateKey.generate(1024)
        self.dsa_ca = _KEY.DsaPrivateKey.generate()
        self.ecdsa_ca = _KEY.EcdsaPrivateKey.generate()
        self.ed25519_ca = _KEY.Ed25519PrivateKey.generate()

        self.rsa_user = _KEY.RsaPrivateKey.generate(1024).public_key
        self.dsa_user = _KEY.DsaPrivateKey.generate().public_key
        self.ecdsa_user = _KEY.EcdsaPrivateKey.generate().public_key
        self.ed25519_user = _KEY.Ed25519PrivateKey.generate().public_key

        self.cert_fields = _CERT.CertificateFields(
            serial=1234567890,
            cert_type=_FIELD.CERT_TYPE.USER,
            key_id="KeyIdentifier",
            principals=["pr_a", "pr_b", "pr_c"],
            valid_after=1968491468,
            valid_before=1968534668,
            critical_options={
                "force-command": "sftp-internal",
                "source-address": "1.2.3.4/8,5.6.7.8/16",
                "verify-required": "",
            },
            extensions=["permit-agent-forwarding", "permit-X11-forwarding"],
        )

    def tearDown(self):
        shutil.rmtree("tests/certificates")
        os.mkdir("tests/certificates")

    def test_cert_type_assignment(self):
        rsa_cert = _CERT.SSHCertificate.create(self.rsa_user)
        dsa_cert = _CERT.SSHCertificate.create(self.dsa_user)
        ecdsa_cert = _CERT.SSHCertificate.create(self.ecdsa_user)
        ed25519_cert = _CERT.SSHCertificate.create(self.ed25519_user)

        self.assertIsInstance(rsa_cert, _CERT.RsaCertificate)
        self.assertIsInstance(dsa_cert, _CERT.DsaCertificate)
        self.assertIsInstance(ecdsa_cert, _CERT.EcdsaCertificate)
        self.assertIsInstance(ed25519_cert, _CERT.Ed25519Certificate)

    def assertCertificateCreated(self, sub_type, ca_type):
        sub_pubkey = getattr(self, f"{sub_type}_user")
        ca_privkey = getattr(self, f"{ca_type}_ca")

        certificate = _CERT.SSHCertificate.create(
            subject_pubkey=sub_pubkey, ca_privkey=ca_privkey, fields=self.cert_fields
        )

        self.assertTrue(certificate.can_sign())
        certificate.sign()
        certificate.to_file(f"tests/certificates/{sub_type}_{ca_type}-cert.pub")

        self.assertEqual(
            0,
            os.system(
                f"ssh-keygen -Lf tests/certificates/{sub_type}_{ca_type}-cert.pub"
            ),
        )

        reloaded_cert = _CERT.SSHCertificate.from_file(
            f"tests/certificates/{sub_type}_{ca_type}-cert.pub"
        )

        self.assertEqual(certificate.get_signable(), reloaded_cert.get_signable())

    def test_certificate_creation(self):
        for ca_type in CERTIFICATE_TYPES:
            for user_type in CERTIFICATE_TYPES:
                print(
                    "Testing certificate creation for {} CA and {} user".format(
                        ca_type, user_type
                    )
                )
                self.assertCertificateCreated(user_type, ca_type)


if __name__ == "__main__":
    unittest.main()
