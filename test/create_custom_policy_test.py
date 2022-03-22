from apr import iac


if __name__ == "__main__":
    iac.clean_iam()
    iac.create_custom_policy()
    print("OK")
