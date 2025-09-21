import argparse
from kernel.system import System


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", help="Username for automatic login")
    parser.add_argument("--password", help="Password for automatic login")
    args = parser.parse_args()

    system = System()

    # Store the login credentials in the system for use by the login program
    if args.login and args.password:
        # Use setattr to avoid mypy complaints about dynamic attributes
        setattr(system, "_auto_login_user", args.login)
        setattr(system, "_auto_login_password", args.password)

    system.run()


if __name__ == "__main__":
    main()
